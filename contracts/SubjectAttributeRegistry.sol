// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./Types.sol";

/// ------------------------------------------------------------------------
/// Contract: SubjectAttributeRegistry
/// ------------------------------------------------------------------------

contract SubjectAttributeRegistry {
    address public admin;

    mapping(address => SubjectAttrs) private _subjects;

    event AdminChanged(address indexed oldAdmin, address indexed newAdmin);

    event SubjectAttributesSet(
        address indexed subject,
        Role role,
        bytes32 orgId,
        bytes32 jurisdiction,
        bool isActive
    );

    modifier onlyAdmin() {
        require(msg.sender == admin, "SubjectAttr: only admin");
        _;
    }

    constructor() {
        admin = msg.sender;
        emit AdminChanged(address(0), msg.sender);
    }

    function setAdmin(address newAdmin) external onlyAdmin {
        require(newAdmin != address(0), "SubjectAttr: zero addr");
        emit AdminChanged(admin, newAdmin);
        admin = newAdmin;
    }

    /// @notice Set attributes for a subject (user, organization agent, etc.).
    function setSubjectAttributes(
        address subject,
        Role role,
        bytes32 orgId,
        bytes32 jurisdiction,
        bool isActive
    ) external onlyAdmin {
        _subjects[subject] = SubjectAttrs({
            role: role,
            orgId: orgId,
            jurisdiction: jurisdiction,
            isActive: isActive
        });

        emit SubjectAttributesSet(subject, role, orgId, jurisdiction, isActive);
    }

    /// @notice Get full attribute struct for a subject.
    function getSubjectAttrs(address subject) external view returns (SubjectAttrs memory) {
        return _subjects[subject];
    }
}
