// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./Types.sol";

/// ------------------------------------------------------------------------
/// Contract: EvidenceRegistry
/// ------------------------------------------------------------------------

contract EvidenceRegistry {
    address public admin;

    uint256 public nextResourceId = 1;

    mapping(uint256 => Resource) private _resources;
    mapping(bytes32 => uint256[]) private _resourcesByCase;

    event AdminChanged(address indexed oldAdmin, address indexed newAdmin);

    event ResourceRegistered(
        uint256 indexed resourceId,
        bytes32 indexed caseId,
        ResourceType rType,
        uint8 sensitivity,
        address indexed owner,
        bytes32 contentHash,
        string uri
    );

    modifier onlyAdmin() {
        require(msg.sender == admin, "EvidenceReg: only admin");
        _;
    }

    constructor() {
        admin = msg.sender;
        emit AdminChanged(address(0), msg.sender);
    }

    function setAdmin(address newAdmin) external onlyAdmin {
        require(newAdmin != address(0), "EvidenceReg: zero addr");
        emit AdminChanged(admin, newAdmin);
        admin = newAdmin;
    }

    /// @notice Register a new resource/evidence object.
    function registerResource(
        bytes32 contentHash,
        string calldata uri,
        bytes32 caseId,
        ResourceType rType,
        uint8 sensitivity
    ) external onlyAdmin returns (uint256 resourceId) {
        require(contentHash != bytes32(0), "EvidenceReg: empty hash");

        resourceId = nextResourceId++;
        Resource storage r = _resources[resourceId];

        r.id           = resourceId;
        r.contentHash  = contentHash;
        r.uri          = uri;
        r.caseId       = caseId;
        r.rType        = rType;
        r.sensitivity  = sensitivity;
        r.owner        = msg.sender;
        r.exists       = true;

        if (caseId != bytes32(0)) {
            _resourcesByCase[caseId].push(resourceId);
        }

        emit ResourceRegistered(
            resourceId,
            caseId,
            rType,
            sensitivity,
            msg.sender,
            contentHash,
            uri
        );
    }

    /// @notice Get full resource metadata.
    function getResource(uint256 resourceId) external view returns (Resource memory) {
        return _resources[resourceId];
    }

    /// @notice Get all resource IDs associated with a case.
    function getResourcesByCase(bytes32 caseId) external view returns (uint256[] memory) {
        return _resourcesByCase[caseId];
    }
}
