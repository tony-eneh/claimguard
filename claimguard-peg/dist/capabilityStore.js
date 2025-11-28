"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.saveCapability = saveCapability;
exports.getCapability = getCapability;
const caps = new Map();
function saveCapability(cap) {
    caps.set(cap.token, cap);
}
function getCapability(token) {
    const cap = caps.get(token);
    if (!cap)
        return undefined;
    if (cap.expiresAt.getTime() < Date.now()) {
        caps.delete(token);
        return undefined;
    }
    return cap;
}
