// contracts/AccessAuditLog.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract AccessAuditLog {
    event AccessChecked(
        address indexed subject,
        bytes32 indexed resourceIdHash,
        bytes32 indexed actionHash,
        bool allow,
        uint256 ts
    );

    function logAccess(
        address subject,
        bytes32 resourceIdHash,
        bytes32 actionHash,
        bool allow
    ) external {
        emit AccessChecked(
            subject,
            resourceIdHash,
            actionHash,
            allow,
            block.timestamp
        );
    }
}
