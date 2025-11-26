// Must match Solidity enum Action ordering
export enum Action {
  READ = 0,
  APPEND = 1,
  UPDATE = 2,
  DELETE = 3,
  APPROVE = 4,
  SHARE = 5
}

export interface AccessRequestBody {
  subject: string;      // EVM address of requester
  resourceId: number;   // uint256 resource ID
  action: keyof typeof Action; // "READ" | "APPEND" | ...
}

export interface Capability {
  token: string;
  subject: string;
  resourceId: bigint;
  action: Action;
  uri: string;
  contentHash: string;
  expiresAt: Date;
}
