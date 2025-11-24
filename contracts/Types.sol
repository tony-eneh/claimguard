// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// ------------------------------------------------------------------------
/// Shared Types for ClaimGuard
/// ------------------------------------------------------------------------

/// @dev High-level subject roles in the auto-insurance ecosystem.
enum Role {
    NONE,
    DRIVER,
    INSURER,
    REINSURER,
    ADJUSTER,
    POLICE,
    COURT,
    GARAGE,
    REGULATOR,
    CLOUD_PROVIDER
}

/// @dev Generic resource types (FNOL, medical, PDF, video, logs, etc.).
enum ResourceType {
    GENERIC,
    FNOL,
    MEDICAL_REPORT,
    REPAIR_ESTIMATE,
    POLICE_REPORT,
    IMAGE,
    VIDEO,
    PDF,
    TELEMATICS,
    LOG,
    OTHER
}

/// @dev Actions that can be controlled by policies (CRUD + domain-specific).
enum Action {
    READ,       // view/download
    APPEND,     // add new related evidence
    UPDATE,     // change/annotate existing evidence
    DELETE,     // delete (usually highly restricted)
    APPROVE,    // approve/endorse (e.g. claim decision)
    SHARE       // explicitly share with another org/entity
}

/// @dev Global attributes for a subject (address).
struct SubjectAttrs {
    Role role;
    bytes32 orgId;          // e.g. insurer code, police department, hospital ID
    bytes32 jurisdiction;   // e.g. region/country code
    bool   isActive;
}

/// @dev Registered resource/evidence metadata (off-chain payload referenced by URI + hash).
struct Resource {
    uint256 id;
    bytes32 contentHash;    // hash of the off-chain object (video, PDF, JSON, etc.)
    string  uri;            // pointer: s3://..., ipfs://..., https://..., etc.
    bytes32 caseId;         // claims/case identifier
    ResourceType rType;
    uint8   sensitivity;    // 0 = low, higher = more sensitive (e.g. medical)
    address owner;          // entity that registered it (insurer, court, etc.)
    bool    exists;
}

/// @dev A single ABAC-style policy rule.
///
/// Matching semantics:
///   - If a field is zero/wildcard (orgId, jurisdiction, caseId), it does not constrain.
///   - If rType == GENERIC, any resource type is allowed (subject to sensitivity).
///   - Resource.sensitivity must be <= maxSensitivity.
///   - Time window enforced via notBefore / notAfter (0 = unbounded).
struct PolicyRule {
    uint256 id;
    Role role;              // subject role required
    bytes32 orgId;          // optional: constrain to org
    bytes32 jurisdiction;   // optional: constrain to jurisdiction
    ResourceType rType;     // resource type (or GENERIC)
    bytes32 caseId;         // optional: constrain to specific case
    Action action;          // action this policy governs
    uint8  maxSensitivity;  // maximum sensitivity allowed under this rule
    uint64 notBefore;       // unix timestamp; 0 = no lower bound
    uint64 notAfter;        // unix timestamp; 0 = no upper bound
    bool   allow;           // for now only ALLOW rules are used
    bool   active;
}
