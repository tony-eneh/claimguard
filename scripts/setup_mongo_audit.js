// MongoDB Audit Log Schema for ClaimGuard E5 Experiment
// Creates collection with validation and indexes

db = db.getSiblingDB('audit_logs');

// Drop collection if exists (for clean reruns)
db.audit_log.drop();

// Create collection with schema validation
db.createCollection('audit_log', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['subject', 'resourceIdHash', 'action', 'allowed', 'timestamp'],
      properties: {
        subject: {
          bsonType: 'string',
          pattern: '^0x[a-fA-F0-9]{40}$',
          description: 'Ethereum address (must be 0x + 40 hex chars)'
        },
        resourceIdHash: {
          bsonType: 'string',
          pattern: '^0x[a-fA-F0-9]{64}$',
          description: 'keccak256 hash (must be 0x + 64 hex chars)'
        },
        action: {
          bsonType: 'string',
          enum: ['READ', 'APPEND', 'UPDATE', 'DELETE', 'ADJUDICATE', 'DISCLOSE'],
          description: 'Access control action type'
        },
        allowed: {
          bsonType: 'bool',
          description: 'Authorization decision (true = allowed, false = denied)'
        },
        timestamp: {
          bsonType: 'date',
          description: 'Event timestamp'
        },
        blockNumber: {
          bsonType: ['int', 'null'],
          description: 'Optional: blockchain block number for correlation'
        },
        transactionHash: {
          bsonType: ['string', 'null'],
          description: 'Optional: blockchain transaction hash'
        }
      }
    }
  },
  validationAction: 'error',
  validationLevel: 'strict'
});

// Create indexes for query patterns
db.audit_log.createIndex({ subject: 1 }, { name: 'idx_subject' });
db.audit_log.createIndex({ resourceIdHash: 1 }, { name: 'idx_resource' });
db.audit_log.createIndex({ timestamp: 1 }, { name: 'idx_timestamp' });
db.audit_log.createIndex({ allowed: 1 }, { name: 'idx_allowed' });

// Partial index for denials
db.audit_log.createIndex(
  { allowed: 1 },
  { name: 'idx_denied', partialFilterExpression: { allowed: false } }
);

// Composite indexes for compound queries
db.audit_log.createIndex(
  { subject: 1, timestamp: 1 },
  { name: 'idx_subject_timestamp' }
);
db.audit_log.createIndex(
  { resourceIdHash: 1, timestamp: 1 },
  { name: 'idx_resource_timestamp' }
);

// Verify collection and indexes
print('\n=== MongoDB Collection Info ===');
print('Collection: audit_log');
print('\nIndexes:');
db.audit_log.getIndexes().forEach(function(index) {
  print('  - ' + index.name);
});

print('\nMongoDB audit_log schema created successfully!');
