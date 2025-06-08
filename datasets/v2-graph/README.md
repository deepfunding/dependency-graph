# Deep Funding: Dependency Graph v2

This version of the dependency graph offers three improvements over the previous version:

1. Transitive dependencies are excluded. This primarily affects JavaScript / TypeScript projects.
2. Better support for less common package managers in the Ethereum ecosystem, such as Nuget and Maven.
3. Parsing of specific package URIs that are not well-supported by the GitHub API (eg, Gradle files).

You can view the script used to generate this version of the graph [here](https://github.com/opensource-observer/insights/tree/main/experiments/dependency-graph-v2).

This directory includes JSON files for both the top-level "seed" repos and the dependency set. It also includes a CSV file that contains the full dependency graph. GitHub Actions are not included in the dependency set.

Here is a summary of the data:

```json
{
  "total_repositories": 38,
  "total_dependencies": 15192,
  "by_language": {
    "JavaScript": 11943,
    "Other": 1880,
    "Go": 661,
    "Python": 241,
    "Java": 215,
    "Ruby": 115,
    "C#": 137
  },
  "by_package_manager": {
    "NPM": 11943,
    "GO": 661,
    "ACTIONS": 356,
    "PIP": 241,
    "RUST": 1522,
    "GRADLE": 215,
    "RUBYGEMS": 115,
    "NUGET": 137
  },
  "by_repository": {
    "https://github.com/a16z/helios": {
      "RUST": 256,
      "ACTIONS": 5,
      "NPM": 179
    },
    "https://github.com/alloy-rs/alloy": {
      "RUST": 17,
      "ACTIONS": 7
    },
    "https://github.com/apeworx/ape": {
      "PIP": 36,
      "ACTIONS": 15,
      "NPM": 2
    },
    "https://github.com/chainsafe/lodestar": {
      "ACTIONS": 20,
      "NPM": 555
    },
    "https://github.com/consensys/teku": {
      "ACTIONS": 7,
      "NPM": 142,
      "GRADLE": 94
    },
    "https://github.com/erigontech/erigon": {
      "GO": 271,
      "ACTIONS": 18,
      "NPM": 10
    },
    "https://github.com/eth-infinitism/account-abstraction": {
      "ACTIONS": 4,
      "NPM": 230
    },
    "https://github.com/ethereum-lists/chains": {
      "ACTIONS": 10,
      "NPM": 6
    },
    "https://github.com/ethereum/consensus-specs": {
      "PIP": 22,
      "ACTIONS": 4
    },
    "https://github.com/ethereum/eips": {
      "RUBYGEMS": 108,
      "ACTIONS": 20
    },
    "https://github.com/ethereum/evmone": {
      "n/a": 2
    },
    "https://github.com/ethereum/execution-apis": {
      "ACTIONS": 6,
      "NPM": 257
    },
    "https://github.com/ethereum/fe": {
      "RUST": 239,
      "ACTIONS": 4
    },
    "https://github.com/ethereum/go-ethereum": {
      "GO": 140,
      "PIP": 1,
      "ACTIONS": 3
    },
    "https://github.com/ethereum/py-evm": {
      "PIP": 12
    },
    "https://github.com/ethereum/remix-project": {
      "NPM": 6564,
      "ACTIONS": 7
    },
    "https://github.com/ethereum/solidity": {
      "PIP": 4,
      "ACTIONS": 3
    },
    "https://github.com/ethereum/sourcify": {
      "NPM": 325
    },
    "https://github.com/ethereum/web3.py": {
      "PIP": 14
    },
    "https://github.com/ethereumjs/ethereumjs-monorepo": {
      "ACTIONS": 12,
      "NPM": 331
    },
    "https://github.com/ethers-io/ethers.js": {
      "ACTIONS": 6,
      "NPM": 161
    },
    "https://github.com/foundry-rs/foundry": {
      "RUST": 263,
      "ACTIONS": 22
    },
    "https://github.com/grandinetech/grandine": {
      "RUST": 236,
      "ACTIONS": 4,
      "RUBYGEMS": 7
    },
    "https://github.com/hyperledger-web3j/web3j": {
      "ACTIONS": 9,
      "GRADLE": 11
    },
    "https://github.com/hyperledger/besu": {
      "ACTIONS": 17,
      "GRADLE": 110
    },
    "https://github.com/nethereum/nethereum": {
      "NUGET": 68,
      "ACTIONS": 2
    },
    "https://github.com/nethermindeth/nethermind": {
      "NUGET": 69,
      "ACTIONS": 24
    },
    "https://github.com/nomicfoundation/hardhat": {
      "NPM": 1328,
      "ACTIONS": 16
    },
    "https://github.com/openzeppelin/openzeppelin-contracts": {
      "PIP": 2,
      "ACTIONS": 10,
      "NPM": 237
    },
    "https://github.com/paradigmxyz/reth": {
      "RUST": 232,
      "ACTIONS": 31
    },
    "https://github.com/prysmaticlabs/prysm": {
      "GO": 250,
      "ACTIONS": 8
    },
    "https://github.com/safe-global/safe-smart-account": {
      "PIP": 1,
      "ACTIONS": 5,
      "NPM": 219
    },
    "https://github.com/scaffold-eth/scaffold-eth-2": {
      "ACTIONS": 2,
      "NPM": 278
    },
    "https://github.com/sigp/lighthouse": {
      "RUST": 279,
      "ACTIONS": 12
    },
    "https://github.com/status-im/nimbus-eth2": {
      "PIP": 111,
      "ACTIONS": 10
    },
    "https://github.com/vyperlang/titanoboa": {
      "PIP": 28,
      "ACTIONS": 6
    },
    "https://github.com/vyperlang/vyper": {
      "PIP": 10,
      "ACTIONS": 16
    },
    "https://github.com/wevm/viem": {
      "NPM": 1119,
      "ACTIONS": 11
    }
  }
}
```

## Identifying Missing Dependencies

When checking for missing dependencies in your repository's [JSON array](seedReposWithDependencies.json), follow these steps:

1. First, check if the package is present in the [dependency-graph-v2.csv](dependency-graph-v2.csv) file. This file contains the complete list of all dependencies across all repositories.

2. If the package is not found in the CSV file, it means it wasn't detected by our dependency scanning process. In this case, you should:
   - Verify the package is correctly specified in your repository's dependency management files
   - Check if the package is a transitive dependency (these are excluded in v2)
   - Ensure the package manager is one we support (NPM, GO, PIP, RUST, GRADLE, RUBYGEMS, NUGET)

3. If the package is in the CSV but not in your repository's JSON array, it may be because:
   - The package is not indexed by [deps.dev](https://deps.dev) (an issue for some .NET and Java Gradle packages)
   - The package's source repository couldn't be automatically identified via its metadata

4. For packages not indexed by deps.dev, you may need to manually look up their source repositories and add them to your repository's JSON array.

Example: To check if a package like RocksDB is included, search for it in the [dependency-graph-v2.csv](dependency-graph-v2.csv) file. If it's present but not in your JSON, you'll need to manually add it with its correct source repository information.