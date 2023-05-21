---
title: DeadSec CTF - Loud(s)
date: 2023-05-21 13:00:00
categories: [Ctf Writeups, Crypto]
tags: [crt, coppersmith method] # TAG names should always be lowercase
math: true
---

We are given some CRT reminders modulo primes of a secret number, together with some fake values. To recover the number, for small instances a simple brute-force solution is enough; for larger instances we can do that using the *Coppersmith Method*. 

> **Event Link:** [DeadSec CTF](https://ctftime.org/event/1962)/   
{: .prompt-info }

## Step 1 - Brute-force

The first wave of challenges included two related problems, `Loud` and `Really Loud`. Both these two challenges admit a simple (unintended) solution, using the Chinese Reminder Theorem only a few times. However, this solution gives some insights for the next one. Let's focus on `Loud`, since the same solution applies directly to `Really Loud`. We are given this `sage` code:

```python
B = 2^2048
flag = randint(1, B) # recover this value, wrap the answer in Dead{}
m = 5
n = 30
ps = [getStrongPrime(1024) for _ in range(n)]
S = [[randint(0, ps[i] - 1) for __ in range(m - 1)] + [int(flag % ps[i])] for i in range(n)]

for Si in S:
    random.shuffle(Si)

print(ps)
print(S)
```

together with its output, the two lists `ps` and `S`. We see that `flag` is a `2048` bit random number. `ps` contains $30$ random `1024`-bit prime numbers, and `S` $30$ lists of $5$ numbers each: 4 of those are just random numbers, while the last one is `flag % ps[i]`. Since the lists are shuffled at random, we do not know which number is the good one.

This can be solved easily in many ways. The most useful for later is the following. We know that $flag < 2^{2048}$, and expect every $p \in ps$ to be $\sim 2^{1024}$. If we apply the *CRT* to a tuple of three numbers coming from the first three lists in `S`, we know that the solution must be unique, and because of the size of the $p_i$ we expect this solution to be $\sim 2^{1024 \cdot 3} = 2^{3072}$. This will likely be true for all random solutions. However, the *correct solution*, i.e. the value of `flag`, will be lower than $2^{2048}$ by definition. If we add more (correct) reminders to the correct solution, those will just be satified; this won't be true for random tuples. This idea is similar to the [Broadcast Attack](https://en.wikipedia.org/wiki/Coppersmith%27s_attack#H%C3%A5stad's_broadcast_attack) on RSA, for instance.

What we can do is to run a simple script to check all the 3-tuples coming from the first three sets, an check for numbers $<2^{2048}$:

```python
from sage.all import *

for s in S[0]:
	for t in S[1]:
		for u in S[2]:
			g = CRT([s,t,u], ps[:3])
			if g <= 2**2048:
				print(f'Hit: {g}')
```

This quickly solves both `Loud` and `Really Loud`. Notice that we only have to compute $5^3 = 125$ CRTs ($1000$ for `Really Loud`).

## Step 2 - Coppersmith Method

This solution is very simple and fast, and hence came out quickly during the challenge. However, the authors said this was unintended, and hence released a second version of the challenges fixing this problem: `Loud Revenge` and `Really Loud Revenge`. They only changed the parameters $m$ and $n$ and the bitlength of the numbers. Here is the code for `Loud Revenge`:

```python
B = 2^4096
flag = randint(1, B) # recover this value, wrap the answer in Dead{}
m = 4
n = 256
ps = [getPrime(128) for _ in range(n)]
S = [[randint(0, ps[i] - 1) for __ in range(m - 1)] + [int(flag % ps[i])] for i in range(n)]

for Si in S:
    random.shuffle(Si)

print(ps)
print(S)
```
As you can see, now we need $32$ `128`-bit primes to get to the size of `B`. The brute-force solution of above would need to compute $4^{32}$ CRTs, which is not feasible. 

An unintended solution to those two was found as well, probably involving some random seed cracking, and a third version, `LLLoud` and `LLLoud 2`, was released. This version had no substantial difference in the code, except that `randint` was replaced by a cryptographically secure version of `random`. However, the name gives us a big hint towards the **Lenstra-Lenstra-Lovasz** ([LLL](https://en.wikipedia.org/wiki/Lenstra%E2%80%93Lenstra%E2%80%93Lov%C3%A1sz_lattice_basis_reduction_algorithm)) algorithm. This algorithm is widely used in cryptography and cryptanalysis when you want to recover information from some partial data. The easiest way to apply LLL to these kind of problems is usually the **Copppersmith Method**.

The Coppersmith Method is a method to find small integer zeroes of (monic) polynomials modulo a given integer (see for instance [wikipedia](https://en.wikipedia.org/wiki/Coppersmith_method) or [this](https://www.cits.ruhr-uni-bochum.de/imperia/md/content/may/paper/intro_to_coppersmiths_method.pdf) article). More specifically, let 

$$ F(x) = x^d + a_{d-1}x^{d-1} + \dots + a_1 x + a_0 $$

be a degree $d$ polynomial. Given a module $N$ and a bound $X$ such that $X \leq 0.5 N^{1/d}$, the Coppersmith Method efficiently recovers all the solutions $x_i \leq X$ such that $F(x_i) \equiv 0 \mod N$.

All we need is to define the right polynomial. Here the observation we made before to build the brute-force solution comes in our help. Let $P = \prod p_i \sim 2^{32768}$ be the product of all the $256$ $p_i$'s. If we define a polynomial that has as zeros all the possible combinations obtained via CRT with all possible reminders we are given, this polynomial will have many very big solution $\mod P$ (of the order of magnitude of $P$ itself), but also a small solution, namely $flag \leq 2^{4096}$. This polynomial is easy to build: for each set $S_i$, we compute

$$ f_i = (x-s_1)(x-s_2)(x-s_3)(x-s_4) \mod p_i,$

where $s_1,s_2,s_3,s_4$ are the four elements of $S_i$. We can then obtain the desired polynomial $f$ by taking the CRT of all $f_i$ modulo the $p_i$. In this way, we have $N=P \sim 2^{32768}$, $X=2^{4096}$ and $d=4$. Since $0.5N^{1/4} \sim 2^{8192}$ we can apply the Coppersmith Method. Luckily, this is already implemented in `sage` with the function `small_roots`, so we don't need to worry about that. The final code is:

```python
from sage.all import *

# Input values
ps = ...
S = ... 

# Lists for the coefficients of fi
c0, c1, c2, c3, c4 = [], [], [], [], []

for i in range(len(S)):
	Ki = Zmod(ps[i])
	
	P = PolynomialRing(Ki, implementation='NTL', names=('x',)); 
	(x,) = P._first_ngens(1)
	
	# For each i compute fi
	x1,x2,x3,x4 = S[i]
	fi = (x - x1)*(x - x2)*(x - x3)*(x - x4) 
	n0, n1, n2, n3, n4 = fi.int_list()
	c0.append(n0); c1.append(n1);c2.append(n2);	c3.append(n3); c4.append(n4);

print('CRT')
# Coefficients of the final f
c0 = CRT(c0, ps); c1 = CRT(c1, ps); c2 = CRT(c2, ps); c3 = CRT(c3, ps); c4 = CRT(c4, ps);

P = product(ps)
K = Zmod(P)

R = PolynomialRing(K, implementation='NTL', names=('x',)); 
(x,) = R._first_ngens(1)

f = c0 + c1*x + c2*x**2 + c3*x**3 + c4*x**4

print(f'Computing Small roots')
B = 2**4096
s_roots = f.small_roots(X = B, beta=0.5) 
print(f'{s_roots}')
```

## Step 2 - Really Loud Revenge

Like before, the difference between `Loud Revenge` and `Really Loud Revenge` is only in the parameters. This is the source code for `Really Loud Revenge`:

```python
B = 2^4096
flag = randint(1, B) # recover this value, wrap the answer in Dead{}
m = 4
n = 20
ps = [getPrime(256) for _ in range(n)]
S = [[randint(0, ps[i] - 1) for __ in range(m - 1)] + [int(flag % ps[i])] for i in range(n)]

for Si in S:
    random.shuffle(Si)
```

This time, we only have $20$ reminders of `256` bits each. If we apply the above idea, we get $N \sim 2^{5120}$, and $X = 2^{4096}$. Since $d = 4$, we can no longer apply Coppersmith Method, at least not in this way (actually, for it to work we would need $d=1$). As of now, I don't know the solution to this part. It may require to build the lattice directly to apply LLL (without Coppersmith Method), or some different idea.