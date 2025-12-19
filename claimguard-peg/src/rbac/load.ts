// src/rbac/load.ts
import fs from "node:fs";
import { RbacStore, SubjectJson, ResourceJson } from "./store";

export function buildStoresFromOutputs(opts: {
    store: RbacStore;
    subjectsPath: string;
    resourcesPath: string;
}) {
    const subjRaw = fs.readFileSync(opts.subjectsPath, "utf-8");
    const resRaw = fs.readFileSync(opts.resourcesPath, "utf-8");

    const subjects = JSON.parse(subjRaw) as SubjectJson[];
    const resources = JSON.parse(resRaw) as ResourceJson[];

    opts.store.loadFromJson(subjects, resources);
    return { subjectsCount: subjects.length, resourcesCount: resources.length };
}
