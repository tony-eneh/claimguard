import { ethers } from "hardhat";

async function main() {
  const [deployer] = await ethers.getSigners();
  const address = await deployer.getAddress();
  const balance = await ethers.provider.getBalance(address);
  
  console.log("\n=== Sepolia Wallet Info ===");
  console.log("Address:", address);
  console.log("Balance:", ethers.formatEther(balance), "ETH");
  console.log("===========================\n");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
