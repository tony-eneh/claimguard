// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./Types.sol";
import "./SubjectAttributeRegistry.sol";
import "./EvidenceRegistry.sol";

/// ------------------------------------------------------------------------
/// Contract: AccessPolicyManager
/// ------------------------------------------------------------------------

contract AccessPolicyManager {
    address public admin;

    SubjectAttributeRegistry public subjectRegistry;
    EvidenceRegistry public evidenceRegistry;

    uint256 public nextPolicyId = 1;
    mapping(uint256 => PolicyRule) private _policies;

    event AdminChanged(address indexed oldAdmin, address indexed newAdmin);

    event PolicyCreated(
        uint256 indexed policyId,
        Role role,
        bytes32 orgId,
        bytes32 jurisdiction,
        ResourceType rType,
        bytes32 caseId,
        Action action,
        uint8 maxSensitivity,
        uint64 notBefore,
        uint64 notAfter,
        bool allow
    );

    event PolicyRevoked(uint256 indexed policyId, address indexed by);

    event AccessChecked(
        address indexed subject,
        uint256 indexed resourceId,
        Action action,
        bool allowed
    );

    modifier onlyAdmin() {
        require(msg.sender == admin, "PolicyMgr: only admin");
        _;
    }

    constructor(address subjectRegistry_, address evidenceRegistry_) {
        require(subjectRegistry_ != address(0), "PolicyMgr: subj reg zero");
        require(evidenceRegistry_ != address(0), "PolicyMgr: evid reg zero");

        admin = msg.sender;
        emit AdminChanged(address(0), msg.sender);

        subjectRegistry = SubjectAttributeRegistry(subjectRegistry_);
        evidenceRegistry = EvidenceRegistry(evidenceRegistry_);
    }

    function setAdmin(address newAdmin) external onlyAdmin {
        require(newAdmin != address(0), "PolicyMgr: zero addr");
        emit AdminChanged(admin, newAdmin);
        admin = newAdmin;
    }

    /// @notice Create a new policy rule.
    function createPolicy(
        Role role,
        bytes32 orgId,
        bytes32 jurisdiction,
        ResourceType rType,
        bytes32 caseId,
        Action action,
        uint8 maxSensitivity,
        uint64 notBefore,
        uint64 notAfter,
        bool allow
    ) external onlyAdmin returns (uint256 policyId) {
        require(role != Role.NONE, "PolicyMgr: role=NONE");
        if (notAfter != 0) {
            require(notAfter > notBefore, "PolicyMgr: time window invalid");
        }

        policyId = nextPolicyId++;
        PolicyRule storage p = _policies[policyId];

        p.id           = policyId;
        p.role         = role;
        p.orgId        = orgId;
        p.jurisdiction = jurisdiction;
        p.rType        = rType;
        p.caseId       = caseId;
        p.action       = action;
        p.maxSensitivity = maxSensitivity;
        p.notBefore    = notBefore;
        p.notAfter     = notAfter;
        p.allow        = allow;
        p.active       = true;

        emit PolicyCreated(
            policyId,
            role,
            orgId,
            jurisdiction,
            rType,
            caseId,
            action,
            maxSensitivity,
            notBefore,
            notAfter,
            allow
        );
    }

    /// @notice Deactivate a policy rule (revocation).
    function revokePolicy(uint256 policyId) external onlyAdmin {
        PolicyRule storage p = _policies[policyId];
        require(p.id != 0, "PolicyMgr: policy not found");
        require(p.active, "PolicyMgr: already inactive");
        p.active = false;
        emit PolicyRevoked(policyId, msg.sender);
    }

    /// @notice View a policy rule.
    function getPolicy(uint256 policyId) external view returns (PolicyRule memory) {
        return _policies[policyId];
    }

    /// @notice Core ABAC decision: can `subject` perform `action` on `resourceId`?
    function checkAccess(
        address subject,
        uint256 resourceId,
        Action action
    ) public view returns (bool) {
        // Load resource and subject attributes from the registries
        Resource memory r = evidenceRegistry.getResource(resourceId);
        if (!r.exists) {
            return false;
        }

        SubjectAttrs memory s = subjectRegistry.getSubjectAttrs(subject);
        if (!s.isActive || s.role == Role.NONE) {
            return false;
        }

        // Linear scan over policies: 1..nextPolicyId-1
        for (uint256 pid = 1; pid < nextPolicyId; pid++) {
            PolicyRule storage p = _policies[pid];
            if (!p.active || !p.allow) continue;

            // Role must match.
            if (p.role != s.role) continue;

            // Optional org and jurisdiction constraints.
            if (p.orgId != bytes32(0) && p.orgId != s.orgId) continue;
            if (p.jurisdiction != bytes32(0) && p.jurisdiction != s.jurisdiction) continue;

            // Resource type constraint (GENERIC serves as wildcard).
            if (p.rType != ResourceType.GENERIC && p.rType != r.rType) continue;

            // Case constraint (0 = any case).
            if (p.caseId != bytes32(0) && p.caseId != r.caseId) continue;

            // Action must match.
            if (p.action != action) continue;

            // Sensitivity constraint.
            if (r.sensitivity > p.maxSensitivity) continue;

            // Time window constraint.
            uint64 nowTs = uint64(block.timestamp);
            if (p.notBefore != 0 && nowTs < p.notBefore) continue;
            if (p.notAfter  != 0 && nowTs > p.notAfter)  continue;

            // First matching allow rule wins.
            return true;
        }

        return false;
    }

    /// @notice checkAccess + emit event for on-chain audit / off-chain listeners.
    function checkAccessAndEmit(
        address subject,
        uint256 resourceId,
        Action action
    ) external returns (bool) {
        bool allowed = checkAccess(subject, resourceId, action);
        emit AccessChecked(subject, resourceId, action, allowed);
        return allowed;
    }
}
