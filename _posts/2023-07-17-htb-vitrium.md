---
title: HTB Business CTF - Vitrium Stash
date: 2023-05-21 13:00:00
categories: [Ctf Writeups, Crypto]
tags: [DSA, lattice, lattice inequalities] # TAG names should always be lowercase
math: true
---

We have to forge a DSA signature for the `admin` being able to ask the server a signature for an arbitrary `username`. We exploit the fact that the message is not hashed in the signature, and hence find two messages that are equal `mod q` giving us a valid signature.

I solved this challenge together with [@robin](https://ur4ndom.dev/){:target="_blank"}.

> **Event Link:** [HTB Business CTF 2023](https://ctftime.org/event/1989/)   
{: .prompt-info }

> The full **solution scripts** is composed by:
> - [rkm_solver.sage](/assets/ctf/23-htbbus/rkm_solver.sage) (copy of [rkm_solver](https://raw.githubusercontent.com/rkm0959/Inequality_Solving_with_CVP/main/solver.sage) for completeness)
> - [match_strings.sage](/assets/ctf/23-htbbus/match_strings.sage) (based on [versesrev's wrapper](https://gist.github.com/versesrev/0f994f70c6de20344f6f44893adb80b0) for the solver)
{: .prompt-tip }

## Challenge Description

The challenge setting is quite simple. It consists in a server implementing [DSA](https://en.wikipedia.org/wiki/Digital_Signature_Algorithm) signature, with fixed (secure) `p`, `q` and `g`. We are given two options. First of all, we can create a new user, providing a `username`. The server returns us the message `json.dumps({"username": username, "admin": False})`, together with the signature `(r,s)` of the message. We can also send a message and a signature to the server. If the signature is valid and the message contains `"admin":true`, the server gives us the flag.    

## Solution

The vulnerable part of the challenge is the `sign` function:
```python
def sign(message):
    m = bytes_to_long(message)
    k = randbelow(p)
    r = pow(g, k, p) % q
    s = (inverse(k, q) * (m + x*r)) % q
    return r, s
```
The difference between this and the actual DSA protocol is that `s` here is computed using the message `m`, and not a hash of it as suggested. The consequence is that given a message `m`, its signature `(r, s)` will be valid for each message `m' = m mod q`, since 

$$
((k^{-1}\bmod q)(m + nq + rx)) \equiv ((k^{-1}\bmod q)(m + rx)) \bmod q
$$

We can ask the server to sign messages of the form `{"username": username, "admin": False}`, where `username` is an arbitrary string we can provide. We win if we manage to find a value for `username` such that the resulting string is congruent `mod q` to another string containing `"admin":true`.    
Recall that a string here is just a large number: each letter is in fact a `8-bit` integer, so we can see `ab = 97*2^8 + 98` (`a` is `97` in ASCII and `b` is `98`). We can easily generalize this idea including variables instead of characters: the string $a_2a_1a_0$ correspond with the number $a_0 + 2^8 a_1 + 2^{16}a_2$, and so on. In our problem, some of this variables will be fixed by the structure of the message. The holes instead will have a strictly bounded value: we want them to be printable, so they can be integers between `32` and `126` (theoretically we should be more careful here, since not every printable character can go inside a `json` string, but fine). We can also impose more strict requirements, for example if we want only printable digits we may ask numbers between `48` and `57`. To sum up, we have a bunch of integer inequalities, which can be solved quite effectively as a CVP instance using Babai's algorithm (see [here](https://github.com/rkm0959/Inequality_Solving_with_CVP) for the implementation)).     
First of all, we need a template for our strings. The target string is fixed, we can put holes only on the username. For the forged string we decided to keep it as simple as possible, setting only the `admin` parameter.
```python
s1 = b'{"admin": 1################################}'
s2 = b'{"username": "????????????????????????????????", "admin": false}'
```
Here `?` represents a printable ASCII, and `#` a printable digit.    
The implementation is conveniently based on [versesrev's wrapper](https://gist.github.com/versesrev/0f994f70c6de20344f6f44893adb80b0): we only have to set up the variables and the constraints, and it does the rest of the job with the lattice. The constraints are quite simple: we want `left_string - right_string + zq = 0`, where `z` is a variable and `left_string` and `right_string` are computed as above. Specifically, every time we find a regular character we add its value (mutiplied by the right power of $2$) to the sum, while every time we encounter `?` or `#` we add a new variable to the sum and then add a constraint to ensure that the variable is a printable ASCII or digit respectively. The function `match_strings(s1, s2, p)` accepts two such strings and return two valid strings satisfying the requirements (if possible). In this case, we got very quickly
```python
s1 = b'{"admin": 144454544455544565622743625683666}'
s2 = b'{"username": "UWdaNYLKAR/F[>1C`_VQETCQSX@HBYu;", "admin": false}'
```
Sending this username to the server, and using the signature for `s1` finally gave us the flag.