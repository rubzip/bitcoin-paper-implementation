# Bitcoin Paper Implementation

I read bitcoin original white paper and impleted it on Python.

## Key Ideas
### Decentralized and public
Satoshi got the conclusion that if you make a decentralized network, it has to be public. Any transaction is broadcasted to all the network.
### P2P Network
The network is composed of nodes that communicate with each other. Each node contains a copy of the blockchain.
### Majority Rule
Considers the truth what the majority of the nodes have (> 51%).
### Hashing and chain
Each block contains a hash that represents the content of the block, including the hash of the previous block. This creates a chain of blocks. This makes that if you change a block, then the hash of that block changes, and you have to change the next blocks too. This is a way to ensure the integrity of the blockchain.
### Proof of work
Creating a block should be computationally expensive so malicius nodes can't create blocks. Proof of work is a way to make computationally expensive to create blocks. The original idea was imposing a rule for resulting hash, for example, that the hash starts with a certain number of zeros. So in your block you have a paremeter called nonce which is an integer, you must iterate over different nonce values until you find a hash that starts with the desired number of zeros. This makes that creating a block is computationally expensive, but verifying it is computationally cheap.
### Rewardings
Called as *Coinbase* in the original paper. It is a reward for the miner who creates a block. It is a way to incentivize the creation of blocks. Goes in the header of a transaction. 
### Maximum number of coins
To ensure scarcity of coins (as gold or other precious metals), Satoshi considered that the maximum number of coins should be 21 million. So the reward for creating a block is halved every 210,000 blocks (approximately every 4 years). When the maximum is reached, the reward will be 0 but the miner will still be rewarded with transaction fees.
### Solving conflicts
In case of 2 miners achive a blocks at the same time, 2 different exist it will be taken the longest chain as the truth.

## Implementation
For the code logic I used Python. Implemented classes for `Transaction`, `Block`, `Blockchain`, and `Node`. `Transaction` is the minimum unit of value transfer. `Block` is a collection of transactions, and contains the hash of the previous block, a hashing method, a mine method and a nonce value. `Blockchain` is a chain of blocks. `Node` is a node in the network, it contains a blockchain and a list of non confirmed transactions.

For the network simmulation I used FastAPI to create a REST API for each node. I know that it is not "descentralized" but I created a central registry to register the nodes, it works as a DNS server, nodes register themselves in the registry and then you can check the alive nodes. After a block is mined, the node broadcast it to the network and the other nodes verify it and add it to their blockchain. If a node receives a block that is not valid, it discards it. If a node receives a block that is valid but it is not the longest chain, it discards it.

Also Gemini added a simple dashboard to visualize the blockchain and the transactions, and simmulate transactions and nodes.

### Project Structure

.
├── bitcoin/
│   ├── api/            # FastAPI models, routes, and templates
│   ├── blockchain/     # Core logic: Proof of Work, Ledger, and Node
├── logs/               # Node and Registry logs (git ignored)
├── tests/              # Pytest integration & unit tests
├── main.py             # CLI entrypoint
└── run_network.sh      # Orchestration script
```

### Running the Network

```bash
uv pip install -r requirements.txt
```

```bash
uv run pytest
```


```bash
# Launch a registry + 4 nodes (default)
./run_network.sh

# Launch a registry + 8 nodes
./run_network.sh 8
```

## To do
For the moment I am using simple transactions (e.g: Alice -> Bob: 10 coins). But in the original paper there are UTXOs (Unspent Transaction Outputs). I should implement that.
