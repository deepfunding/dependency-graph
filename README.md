# Deep Funding - Dependency Graph

Data and docs for Deep Funding's dependency graph.

>🚨 **Updates** 🚨<br>- 2025-01-20:  We've updated the graph to include more seed nodes (and edges). You can still view the V1 graph data [here](./graph/v1/).

## Overview

The **Deep Funding** project involves analyzing a depth-2 directed graph of dependencies and using it to allocate funding. The graph consists of nodes representing repositories (on GitHub and various package managers) that are one or two hops away from Ethereum.

- Total number of Level 1 (seed) nodes: 31
- Total number of Level 2 (dependency) nodes: 5,024
- Total number of edges: 14,927

Here is a [visualization of the V1 graph](https://cosmograph.app/run/?data=https://raw.githubusercontent.com/opensource-observer/insights/refs/heads/main/community/deep_funder/data/unweighted_graph.csv&source=seed_repo_name&target=package_repo_name&gravity=0.25&repulsion=1&repulsionTheta=1&linkSpring=1&linkDistance=10&friction=0.1&renderLabels=true&renderHoveredLabel=true&renderLinks=true&linkArrows=true&curvedLinks=true&nodeSizeScale=0.5&linkWidthScale=1&linkArrowsSizeScale=1&nodeSize=size-default&nodeColor=color-outgoing%20links&linkWidth=width-number%20of%20data%20records&linkColor=color-number%20of%20data%20records&) of the graph.

![image](https://github.com/user-attachments/assets/b3023ab5-f934-4e92-ad40-1e42d37239b6)

Here is an example of a single edge in the graph:
```json
{
   "relation": "GOLANG",
   "weight": 0.1,
   "source": "https://github.com/prysmaticlabs/prysm",
   "target": "https://github.com/multiformats/go-multihash"
}
```

The `source` in the graph is the **dependent** node and the `target` is the **dependency** node. By weighting the edges of the graph, we aim to signal the most important dependencies and allocate funding proportionally to them.

Your job is to submit a list of weights for the edges, where the weight of an edge `source` (dependent) -> `target` (dependency) represents the portion of the credit for `source` (dependent) that belongs to `target` (dependency). The weights coming out of a `source` node into its `target` nodes should sum to less than one; the remainder represents the portion of credit that rests with the `source` node itself.

You can mine GitHub, dependency, and blockchain data for free from [OSO's BigQuery](https://docs.opensource.observer/docs/integrate/) or connect to other data sources.

## Getting Started

1. Explore the dependency data at [./graph/unweighted_graph.json](./graph/unweighted_graph.json). In this version, every edge has a weight of zero. You can also use [`./graph/unweighted_graph.csv`](./graph/unweighted_graph.csv) if you prefer a CSV format.
2. Try running the example [oso_forks_and_funding_weighting.ipynb](./notebooks/weighting_examples/oso_forks_and_funding_weighting.ipynb) notebook in the `notebooks/weighting_examples` directory to see how we might construct a weighted graph. This version uses a simple approach based on data from Gitcoin, Optimism Retro Funding, and fork counts. The result is exported to [oso_forks_and_funding_weighted_graph.json](./graph/weighting_examples/oso_forks_and_funding_weighted_graph.json).
3. Experiment! You can access more public datasets from [OSO's BigQuery](https://docs.opensource.observer/docs/integrate/) and use [Vertex AI](https://cloud.google.com/vertex-ai/docs/training/overview) to train your own model. Or you can take things in a completely different direction!

## How It Works

The initial graph is seeded with the primary repos of the top consensus and execution layer projects (according to https://clientdiversity.org). We also include a set of related infrastructure projects as seed nodes.

The full list of seed nodes is: 

- **Consensus Clients**: `prysmaticlabs/prysm`, `sigp/lighthouse`, `consensys/teku`, `status-im/nimbus-eth2`, `chainsafe/lodestar`, `grandinetech/grandine`
- **Execution Clients**: `ethereum/go-ethereum`, `nethermindeth/nethermind`, `hyperledger/besu`, `erigontech/erigon`, `paradigmxyz/reth`
- **Other Infra & Dev Tools**: `a16z/helios`, `alloy-rs/alloy`, `apeworx/ape`, `eth-infinitism/account-abstraction`, `ethereum-lists/chains`, `ethereum/fe`, `ethereum/py-evm`, `ethereum/remix-project`, `ethereum/solidity`, `ethereum/sourcify`, `ethereum/web3.py`, `ethereumjs/ethereumjs-monorepo`, `ethers-io/ethers.js`, `foundry-rs/foundry`, `hyperledger-web3j/web3j`, `nethereum/nethereum`, `nomicfoundation/hardhat`, `openzeppelin/openzeppelin-contracts`, `safe-global/safe-smart-account`, `scaffold-eth/scaffold-eth-2`, `vyperlang/titanoboa`, `vyperlang/vyper`, `wevm/viem`

The latest version of the graph no longer includes `web3/web3.js` following the announcement that the project is being sunsetted.

Next, we pull the Software Bill of Materials (SBOM) for each of the above repositories and identify all packages in Go, Rust, JavaScript, and Python. 

This gives us a list of approximately 7,000 packages:

- JavaScript: 5575 (hosted on npm)
- Rust/Cargo: 1363 (hosted on crates.io)
- Go/Golang: 387 (hosted on GitHub)
- Python: 162 (hosted on PyPi)

Finally, we try to map each package to an open source repository and build a dependency graph. In total, we are left with 2,046 unique package maintainers on GitHub. 

The notebook used to create the initial graph is [generate_unweighted_graph.ipynb](./notebooks/generate_unweighted_graph.ipynb). You can experiment with adding layers or changing the seed nodes, and getting fresh data from OSO's BigQuery.

Let us know if you find any issues with the data or the graph construction.

## Ideas for Weighting the Graph

There are several data dumps included in [./datasets](./datasets) to get you going, including two from OSO and one from [Drips](https://drips.network).

The largest is a parquet file that contains a snapshot of GitHub activity data for all relevant repositories, indexed by Git user ID:

| Data Type | Count |
|------------|-------|
| Relevant Repos | 648 |
| Git Users | 112,280 |
| Code Commits | 192,680 |
| Issue Comments | 1,150,326 |
| Issues Opened | 124,535 |
| Issues Closed | 152,122 |
| Issues Reopened | 7,446 |
| PRs Opened | 217,284 |
| PRs Closed | 236,648 |
| PRs Merged | 177,137 |
| PRs Reopened | 5,049 |
| PR Review Comments | 553,608 |
| Releases Published | 10,243 |
| Repository Forks | 99,860 |
| Repository Stars | 488,372 |

In the directory [./notebooks/weighting_examples](./notebooks/weighting_examples), we also show some examples of how you can join the graph on other datasets and start weighting the graph. These examples export JSON data to [./graph/weighting_examples](./graph/weighting_examples).

## Utilities

We've included a few utilities for validating and serializing the graph:

- `validate_graph.py`: Validate the graph edge weights add up to 1.0 or less for each seed node.
- `serialize_graph.py`: Serialize the graph to a JSON file.

## Additional Resources
- Get more data (free): [OSO Documentation](https://docs.opensource.observer/docs/integrate/)
- Ask questions: [OSO Discord](https://www.opensource.observer/discord)
- Report issues: Open an issue in this repository