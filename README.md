# Bitcoin Paper Implementation

I read bitcoin original white paper and impleted it on Python.

## Key Ideas
After reading the paper, I realized that Satoshi intended to create a decentralized, electronic version of gold. From an economic perspective, he designed a self-sustaining system where nodes (miners) are compensated for their work. Furthermore, he sought to ensure scarcity, much like gold, by computationally limiting the creation of new coins. Over time, the mining reward is programmed to decrease achieving a maximum of 21 million coins. Also has control over the creation of new blocks increasing the computational cost of creating them.

From the security prespective, he was concerned about the system's vulnerability to attacks by malicious nodes. He posited that if the incentives for honest nodes outweigh those for malicious ones, the system will naturally converge to security. He achieved this by enforcing a high computational cost (which penalizes attackers) while rewarding honest nodes for mining.

The key concepts of the paper are:
### Decentralized and public
Satoshi got the conclusion that if you make a decentralized network, it has to be public. Any transaction is broadcasted to all the network.

### Privacy
Satoshi proposed a system where transactions are public but identities are private. This system is based on the use of public keys and private keys. **A problem of this system is that if someone knows your public key, then he knows all your transactions done with that key.**

### P2P Network
The network is composed of nodes that communicate with each other. Each node contains a copy of the blockchain.

### Majority Rule
Considers the truth what the majority of the nodes have (> 51%).

### Hashing and chain
Each block contains a hash that represents the content of the block, including the hash of the previous block. This creates a chain of blocks. This makes that if you change a block, then the hash of that block changes, and you have to change the next blocks consequently. This is a way to ensure the integrity of the blockchain, making harder to modify past blocks (in theory impossible if we also consider majority rule).

### Proof of work (Mining)
**Creating a block should be computationally expensive for making it difficult to create blocks to malicius nodes.** Proof of work is a way to make computationally expensive to create blocks. The original idea was imposing a rule for resulting hash, for example, that the hash starts with a certain number of zeros.

So in your block you have a paremeter called nonce which is an integer, you must iterate over different nonce values until you find a hash that starts with the desired number of zeros. The process of finding a valid nonce is called *mining*. This makes that creating a block is computationally expensive, but verifying it is computationally cheap.

```python
def mine(self) -> str:
    while not ZerosPOW.is_valid_hash(self.hash):
        self.nonce += 1
        self.hash = self.get_hash()
    return self.hash
```
This method increments nonce value until hash achives proof of work.

If we define a Proof of Work (PoW) where the first $d$ (difficulty) digits of the hash must be zero—given that the hash is expressed as a hexadecimal number—the probability of randomly finding a valid hash is $16^{-d}$.Consequently, the expected number of attempts to find a valid nonce is:

$$E[X] = \sum_{i=1}^{\infty} i \cdot (1-p)^{i-1} p = \frac{1}{p} = 16^{d}$$

$$\sigma[X] = \sqrt{\sum_{i=1}^{\infty} (i - \mu)^2 p (1-p)^{i-1}} = \sqrt{\frac{1-p}{p^2}} \approx \frac{1}{p} = 16^{d}$$


This results in a computational cost of $O(16^d)$ to mine a single block. 



### Rewardings (Coinbase)
Called as *Coinbase* in the original paper. It is a reward for the miner who finds a valid Nonce value. It is a way to incentivize the creation of blocks, and also creates new coins. Satoshi had the hypothesis that if you give a reward for mining make less atractive to be malicius.

### Maximum number of coins
To ensure scarcity of coins (as gold or other precious metals), Satoshi considered that the maximum number of coins should be 21 million. So the reward for creating a block is halved every 210,000 blocks (approximately every 4 years). When the maximum is reached, the reward will be 0 but the miner will still be rewarded with transaction fees.

### Solving conflicts
In case of 2 miners achive a blocks at (almost) the same time, it will be taken the longest chain as the truth.

## Implementation
For the code logic I used Python. Implemented classes for `Transaction`, `Block`, `Blockchain`, and `Node`. `Transaction` is the minimum unit of value transfer. `Block` is a collection of transactions, and contains the hash of the previous block, a hashing method, a mine method and a nonce value. `Blockchain` is a chain of blocks. `Node` is a node in the network, it contains a blockchain and a list of non confirmed transactions.

For the network simmulation I used FastAPI to create a REST API for each node. I know that it is not "descentralized" but I created a central registry API to register the nodes, it works as a DNS server, nodes register themselves in the registry and then you can check the alive nodes. After a block is mined, the node broadcast it to the network and the other nodes verify it and add it to their blockchain. If a node receives a block that is not valid, it discards it. If a node receives a block that is valid but it is not the longest chain, it discards it.

Also Gemini added a simple dashboard to visualize the blockchain, the transactions, and simmulate transactions and nodes.

### Project Structure

```
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
uv run pytest

# Launch a registry + 4 nodes (default)
./run_network.sh

# Launch a registry + 8 nodes
./run_network.sh 8
```

## To do
For the moment I am using simple transactions (e.g: Alice -> Bob: 10 coins). But in the original paper there are UTXOs (Unspent Transaction Outputs). I should implement that.

Merkle tree
