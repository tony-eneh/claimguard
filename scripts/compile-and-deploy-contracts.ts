import { PureChain } from 'purechainlib';

const purechain = new PureChain('testnet');

// Create account
// const account = purechain.account();
// purechain.connect(account.privateKey);
purechain.connect(
  '0x0de42bd796707ca508a259baf734c13405e755792c08dc00b6ed2a207d0e3433'
);

const balance = await purechain.balance()

// const factory = await purechain.contract('./contracts/ClaimguardContracts.sol');
// const subjectAttributeRegistryAddress = '0x51a98fb020E3d0F8F7B3c0dD7b39AE90839E836d';
// const evidenceRegistryAddress = '0x3c129e9025a0d2e72A450f4A331B59C90557cf56';
// const result = await factory.deploy(subjectAttributeRegistryAddress, evidenceRegistryAddress);

// console.log({ result });

console.log({ balance });