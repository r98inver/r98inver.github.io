---
title: SekaiCTF - CryptoGRAPHy Series
date: 2023-08-27 12:00:00
categories: [Ctf Writeups, Crypto]
tags: [graph encryption] # TAG names should always be lowercase
math: true
---

We face an implementation of a Graph Encryption Scheme (GAS) for Shortest Path queries. The challenge consists in three levels: in the first one we are given the key, and we just have to decrypt the paths. For the second one we can perform arbitrary queries and we have to use them to leak the structure of the graph. The third and final step is to implement query recovery knowing the tokens of all possible queries.

> **Event Link:** [SekaiCTF 2023](https://ctftime.org/event/1923/){:target="_blank"}   
{: .prompt-info }

## Challenge Description

The challenge implements a Graph Encryption Scheme for shortest path queries. The idea is probably taken from [[1]](#1) even if the notation is slightly different (we will soon understand why). The code is quite intricated, but the main points are:
- the challenge generates some kind of graph, and a key; the key is actually two keys: the first half is called `key_SKE`, and the second half `key_DES`;
- we compute the `SDSP` (*Single Destination Shortest Path*) tree for each node; this is a map from each query to the query for the next step in the shortest path, i.e. if `1 -> 2 -> 3` is a shortest path from `1` to `3` we will have `SDSP[(1,3)] = (2,3)` and `SDSP[(2,3)] = (3,3)`;
- the `SDSP` is then turned into an `SPDX`, that maps a query (e.g. `(1,3)`) into a value `token + ct` where `token` is some `HMAC` of the output query (computed using the function `tokenGen`, which requires the key) and `ct` is the output query encrypted with `key_SKE`;
- finally, the `SPDX` is encrypted in such a way that we can still recover the enrypted queries using consecutive tokens, while still needing the key to decrypt them;
- more specifically, the server implements a `search` function that takes as input a token; the token is computed by the `tokenGen` function from a query (like `(1,3)`) and the key; using this token the server can recover the next query and decrypt it to obtain `token + ct`; the obtained `token` can be used to continue looking for the path (if we sent `(1,3)` we get the token for `(2,3)` and we can use it to move one step forward; then we get the token for `(3,3)` and then no token, which means we got to the destination); however, all the `ct` collected (the actual query steps) cannot be decrypted without the knowledge of the key: the idea is that we can store the encrypted graph on an untrusted server and still perform queries without an adversary being able to see them;
- the `search` function returns a concatenation of all the tokens and all the ciphertext obtained during the search.

## CryptoGRAPHy 1

The aim of the first step is essentially to get familiar with the code; the challenge itself is non particularly hard. We are asked to recover the path of 50 queries given the (second half of the) output of the `search` function on those queries, i.e. the concatenation of all the returned ciphertexts. However, we are also given the full `key`. Since the ciphertexts are actually the steps of the path encrypted with the key, we just have to decrypt them one by one to get the full path. We are kind of implementing a client for our graph scheme.    
While doing this, we learn a first lesson: each step is 32 bits long (64 hex chars), hence only looking at the output of the query we already know the length of the shortes path returned by the server.

> **Solve script**: [solve2.py](/assets/ctf/23-sekai/solve1.py)
{: .prompt-tip }

## CryptoGRAPHY 2

In the second level we actually start playing. The server gives us a destination node in the graph, and we have to return the degree (i.e. number of edges)
of each node in the single-destination shortest path (SDSP) tree for that destination. To do so, we can perform 130 queries for which we get back the tokens and the ciphertexts. However, this time we do not know the key, so we have to look for another method.    
The idea here is that each token with the same destination corresponds to a single path step, even if we do not know which one (at least not in a straightforward way - more on this later). Let's say we have two intersecting shortest path, like `1 -> 2 -> 3` and `4 -> 2 -> 3`. The tokens from the first path will be generated from the values `(1,3)`, `(2,3)`, and `(3,3)` while the ones for the second path from `(4,3)`, `(2,3)` and `(3,3)`. This means that the second and the third token will be the same. So we can build back our tree without labels. Let's start from the first path: we know that the last token is just `(dest, dest)` for all paths, then we have another token that goes from `dest` to an unknown node and then to another unknown node. Then we take the second one: the last two tokens are equal, which means that we are following the same path, then we have a different one, hence a branch. Doing this for all the paths gives us an equivalent graph from which we can easily detect the edge degrees. Conveniently, we are allowed to query the server 130 times, which is exactly the number of nodes in the graph (actually 129 are enough). So given `dest` we can query for `(i, dest)` for all `i` (avoiding `dest`) which will return in a `Bad Query` error stopping the server, and build up our answer.

> **Solve script**: [solve1.py](/assets/ctf/23-sekai/solve2.py)
{: .prompt-tip }

## CryptoGRAPHY 3

The third step is actually the most interesting. We are given the output of all possible query for all possible pairs `(start, end)` and the structure of the graph. Then given the output of a single query we have to determine exactly the query. This is also a real world scenario: let say the graph is a map (so we know its structure) and we can observe people asking routes using this encryption schemes. We can only see the tokens and the responses, while the actual routes may contain sensitive data (i.e. living or working places etc). We already know from step two that the output of all queries to a destination allow us to detect the structure of our graph, but we do not know which node corresponds to which. In this step, we do not even know the destinations; however recall that the last token for a path to `dest` is always `(dest, dest)`, so we can group the paths by final (unknown) destination. 

Googling a bit I came across [[2]](#2): they present a query recovery attack against this exact protocol; the sintax used by the server is conveniently the same, so following it after having solved the first two steps shouldn't be that hard. The idea is the following: from the graph (that we know) we give a *name* to each node and then to each path. The name does not depend on the initial label of a node, but rather on the structure of the graph itself around that node. This re-labeling looks for graph isomorphisms, meaning that two paths are "the same" if and only if they end up with the same name. Then we can do the same for the graph we obtain from the tokens, and match the names. If we are lucky, some queries will get a name that has a unique correspondence in the starting graph, and we are done. In [[2]](#2) they show that we are usually quite lucky in real world graphs, and they also show how to build a graph for which we are always lucky, i.e. every path is uniquely identifiable. The fact that the function used to create the graph is hidden in the third challenge is promising in this sense. Actually we can also notice that we always receive a (connected) tree from the server, which makes some implementation steps easier. Implementing the algorithms from the paper is also quite straightforward, since they are very well explained there. To recap, the attack consists in three steps:
1. process the original graph: compute the SDSP tree for each destination and then canonically name each path;
2. process the query graph: group the path by destination, recover the SDSP tree for each one and canonically name them as well;
3. for each challenge path the server sends us jsut look for its path name and return the original path.

In this way we get the final flag: `SEKAI{Full_QR_Attack_is_not_easy_https://eprint.iacr.org/2022/838.pdf}` (pointing back at [[2]](#2))

> **Solve script**: [solve.py](/assets/ctf/23-sekai/solve.py) / [tree_stuff.py](/assets/ctf/23-sekai/tree_stuff.py)
{: .prompt-tip }

## References

<a id="1">[1]</a> Ghosh, E., Kamara, S. and Tamassia, R., [2021](https://dl.acm.org/doi/10.1145/3433210.3453099). Efficient graph encryption scheme for shortest path queries. In Proceedings of the 2021 ACM Asia Conference on Computer and Communications Security (pp. 516-525).    
<a id="2">[2]</a> Falzon, F. and Paterson, K.G., [2022](https://eprint.iacr.org/2022/838.pdf). An efficient query recovery attack against a graph encryption scheme. In European Symposium on Research in Computer Security (pp. 325-345). Cham: Springer International Publishing.
