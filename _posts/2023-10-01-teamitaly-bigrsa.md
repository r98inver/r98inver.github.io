---
title: TeamItaly CTF - BigRSA
date: 2023-10-01 12:00:00
categories: [Ctf Writeups, Crypto]
tags: [rsa] # TAG names should always be lowercase
math: true
---

We have to solve RSA with a leak from which we can recover quite easily $ed - 1$.

> **Event Link:** [TeamItaly CTF 2023](https://ctftime.org/ctf/821){:target="_blank"}   
{: .prompt-info }

## Challenge Description

First of all, we have a weird `keygen` function:

```python
p, q = getStrongPrime(1024), getStrongPrime(1024)

def RSAgen(e = None):
    d = 0
    if not e:
        while(d.bit_length() < 2047):
            e = getPrime(2047)
            d = pow(e, -1, (p-1)*(q-1))
    else:
        d = pow(e, -1, (p-1)*(q-1))
    return (p*q, p, q, e, d)

n = p*q
```

So if we do not provide `e`, we get a pair with both `e` and `d` of size `2047` bits. Otherwise is just common RSA. Then we are given a `leak`:

```python
key = RSAgen()
k = randint(600, 1200)
f = factorial(k)

leak = (pow(key[3], 2) + (key[3]*key[4] - 1)*f)*getPrime(256) + k
```

So we have that the `leak` $$l = (e^2 + (ed - 1)f)y + k$$, where $600 \leq k \leq 1200$ is an unknown number, $f = k!$ and $y$ is a `256`-bit prime. Finally the same `n` is used to encrypt the flag.

## Solution

First thing we notice that, knowing $f$, $$l / f \approx (ed - 1)y$$, since $f$ is huge and $ye^2$ and $k$ are small. This has a `256`-bit factor in common with `leak - k`. So we can just bruteforce `k` and see when we get a hit.

```python
for k in range(600, 1200):
	fact = factorial(k)

	y_ed = (leak - k) // fact 
	y = gcd(y_ed, leak - k)
	if y > (1<<100):
		print(f'{k = } {y = }')

# k = 1000 
# y = 109301875007644313321646793756620023172464141085890087796540184816578976056823
```

In this way we get `y` for free as `gcd(y_ed, leak - k)`. So we have $$ed - 1$$, which is a multiple of `phi`. This is easily solvable, see for instance [here](https://math.stackexchange.com/a/1839766). The described algorithm gives us a factor of `n`:

```python
def find_factor(ed, n):
	h = ed
	while h % 2 == 0:
		h = h // 2
	h = int(h)

	for cnt in range(100):
		print(f'{cnt = }')
		a = random.randint(2, n-2)
		g = gcd(a, n)
		if g != 1:
			print(f'{g = }')
			return g

		while True:
			b = pow(a, h, n)
			g = gcd(b-1, n)
			if g == 1:
				b = pow(b, 2, n)
				continue
			if g == n:
				break
			print(f'{g = }')
			return g
```
