import { Capability } from "./types";

const caps = new Map<string, Capability>();

export function saveCapability(cap: Capability) {
  caps.set(cap.token, cap);
}

export function getCapability(token: string): Capability | undefined {
  const cap = caps.get(token);
  if (!cap) return undefined;
  if (cap.expiresAt.getTime() < Date.now()) {
    caps.delete(token);
    return undefined;
  }
  return cap;
}
