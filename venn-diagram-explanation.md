# That Node Diagram

I'm talking about this venn diagram from my [blog post](https://medium.com/@gloriazhao/map-of-the-bitcoin-network-c6f2619a76f3). 
Every once in a while somebody tweets about this node diagram being wrong/surprising so here's my FAQ.
<img src ="https://miro.medium.com/max/1400/1*uDBzD2l4b0hVKXPa6pWHSA.png">

**Q: Light clients can be mining nodes?**

I define a mining node as a node that produces a block. 
Technically, you could have a bunch of light clients that are connected to a full node pool manager that constructs the block for them, and they just compute the hash puzzle needed to solve the block.
No, this doesn't include mining hardware that isn't communicating via P2P protocol (they wouldn't be nodes).
I can't tell you how common this is but this is my explanation for "how is that possible?"

**Q: Pruning nodes are full nodes?**

Yes, they're full nodes. They have the UTXO set which is used to validate new blocks and all of the transactions in them.
Nodes do not look in their blocks database to validate; they use ChainState (the UTXO set).
Puned nodes will have validated all past transactions during IBD; they just don't store them anymore.

**Q: Light clients are full nodes?**

No. The label for light clients is just pointing to the area in All Nodes that _excludes_ Full Nodes.
I can see how you can read the diagram that way, but it's just a diagram.
