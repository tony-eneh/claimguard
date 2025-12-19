// src/rbac/store.ts
import crypto from "node:crypto";
import { Action } from "../types";

export type SubjectJson = {
  index: number;
  address: `0x${string}`;
  role: string;          // e.g. "INSURER"
  orgId: string;         // hex hash string
  jurisdiction: string;  // hex hash string
};

export type ResourceJson = {
  resourceId: number;
  contentHash: string;
  caseId: string;        // hash string
  rType: string;         // e.g. "FNOL", "PDF"
  sensitivity: number;
  uri: string;
};

export type RbacRule = {
  role: string;                 // required
  action: keyof typeof Action;               // required (READ/WRITE/etc)
  rType?: string;               // optional resource type constraint
  caseId?: string;              // optional
  allow: boolean;

  // optional extra constraints (useful for “ABAC-ish RBAC”)
  maxSensitivity?: number;
  notBefore?: number;           // unix seconds
  notAfter?: number;            // unix seconds
};

export type RbacDecision = {
  allow: boolean;
  reason: string;
  matchedRule?: RbacRule;
};

export class RbacStore {
  subjects = new Map<string, SubjectJson>();     // key: lowercased address
  resources = new Map<number, ResourceJson>();   // key: resourceId
  rules: RbacRule[] = [];

  loadFromJson(subjects: SubjectJson[], resources: ResourceJson[]) {
    this.subjects.clear();
    this.resources.clear();

    for (const s of subjects) this.subjects.set(s.address.toLowerCase(), s);
    for (const r of resources) this.resources.set(r.resourceId, r);
  }

  evaluate(params: {
    subjectAddr: `0x${string}`;
    resourceId: number;
    action: string;
    nowSec?: number;
  }): RbacDecision {
    const now = params.nowSec ?? Math.floor(Date.now() / 1000);

    const subj = this.subjects.get(params.subjectAddr.toLowerCase());
    if (!subj) return { allow: false, reason: "SUBJECT_NOT_REGISTERED" };

    const res = this.resources.get(params.resourceId);
    if (!res) return { allow: false, reason: "RESOURCE_NOT_FOUND" };

    const candidates = this.rules.filter((rule) => {
      if (rule.role !== subj.role) return false;
      if (rule.action !== params.action) return false;

      if (rule.notBefore !== undefined && now < rule.notBefore) return false;
      if (rule.notAfter !== undefined && now > rule.notAfter) return false;

      if (rule.rType !== undefined && rule.rType !== res.rType) return false;
      if (rule.caseId !== undefined && rule.caseId !== res.caseId) return false;

      if (rule.maxSensitivity !== undefined && res.sensitivity > rule.maxSensitivity) return false;

      return true;
    });

    if (candidates.length === 0) {
      return { allow: false, reason: "NO_MATCHING_RULE" };
    }

    // Prefer most specific, then last-write-wins
    const score = (rule: RbacRule) =>
      (rule.rType !== undefined ? 1 : 0) +
      (rule.caseId !== undefined ? 1 : 0) +
      (rule.maxSensitivity !== undefined ? 1 : 0) +
      (rule.notBefore !== undefined ? 1 : 0) +
      (rule.notAfter !== undefined ? 1 : 0);

    const best = candidates
      .map((r, idx) => ({ r, idx }))
      .sort((a, b) => score(b.r) - score(a.r) || b.idx - a.idx)[0]!.r;

    return best.allow
      ? { allow: true, reason: "ALLOW_RULE_MATCH", matchedRule: best }
      : { allow: false, reason: "DENY_RULE_MATCH", matchedRule: best };
  }
}

export function issueCapability(params: {
  secret: string;
  subject: `0x${string}`;
  resourceId: number;
  action: string;
  ttlSec: number;
  nowSec?: number;
}) {
  const now = params.nowSec ?? Math.floor(Date.now() / 1000);
  const exp = now + params.ttlSec;

  // Keep payload minimal + stable for experiments
  const payload = {
    sub: params.subject,
    rid: params.resourceId,
    act: params.action,
    iat: now,
    exp,
    v: 1,
  };

  const body = Buffer.from(JSON.stringify(payload)).toString("base64url");
  const sig = crypto.createHmac("sha256", params.secret).update(body).digest("base64url");
  return { token: `${body}.${sig}`, payload };
}
