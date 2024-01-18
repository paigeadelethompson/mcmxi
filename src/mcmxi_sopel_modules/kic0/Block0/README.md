# Block0
Sopel Modules to interact with Monero NodeJS Pool

pool.py gives info on Pool:

```
last - info on last mined block
status - info on pool statistics
effort - if only effort gives current round effort if a X string is given it will give the average effort on last X number of blocks 
stats - Gives miner info for given wallet address mining on the pool
mine - How much xmr mined per given Hashrate
solo - Expected time to find block with given Hashrate
```

block-alert.py sends message to IRC #chan when new block is found

network.py gives info on Monero Network:

```
network - Blockheight Diff and Hashrate
fork - Info on next upcoming fork
mempool - number Txs in mempool
blocksize - Median Blocksize
```
## Requirements 

Sopel Irc Bot - https://sopel.chat/

Linux

## Configuration

Edit the files to use the pool you which, this example uses https://pool.xmr.pt

Copy files to ~/.sopel/modules/

Reload the bot and go

## Donations

Feel free to send some XMR

47DMEU3dbmeXN6wZGucK8C3hwYcmbVGKa1Fhs5v8sCFrgqHyAwfCkZ4bMgCYN5CFyxgkHqz5zdcvo6JzqFZTSRjEUwYMSYJ



