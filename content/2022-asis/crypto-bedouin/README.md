---
Title: Bedouin
Date: 2023-01-02 22:48:20
Category: crypto
Slug: 2022-asis-crypto-bedouin
Tags: rsa
Summary: A very custom RSA challenge.
Ctf: asis 2022
Flag: ASIS{B48y_CrYpT0_4_WaRm_Up_N3veR_TrU57_yOuR_3yEs!}
Description: In the bedouin era, trying to survive required a lot of searching. But in today's life, human intelligence has ended this vast search.
Status: published
---

## Solution

This is a very custom RSA challenge, in which all the components are implemented in an unusual way and must hence be inspected. First of all, `e` is not fixed nor given to us. Instead, it is computed as the inverse of `d`, which is given by `1 ^ l ** nbit << 3 ** 3` where `l` and `nbit` are two unknown values. The same two values are involved in the `genbed` function, that consists in a few steps:

1. a prime number `zo` of `nbit` bits is generated and then converted in its binary form;
2. the string obtained is then repeated `l` times and a `1` is added at the end;
3. if the string obtained, *seen as an integer*, is a prime number, it is returned.

The same process is used to generate both `p` and `q`, that ends up being prime number made by a repeated pattern of zeroes and ones. We are then given `n = p*q`, which is a `2047`-bit number, and the encrypted message `c = m^e mod n`.   
The easiest way to solve the challenge is to actually determine `d`, since then `c^d = m mod n` will give us the flag. To do so, we must determine `l` and `nbits`, and we have a lot of information to brutforce them. Notice that, given `l` and `nbits`, both `p` and `q` must be `l*nbits` digit numbers, made only by `1` and `0`; hence it holds `11...1 >= p,q >= 10...0`. For every pair of values we can then compute the highest and lowest possible values of `n`, namely `11...1^2` and `10...0^2`, and their respective number of bits; `2047` must then lie between those values. This happens for only 12 pairs of `(nbits, l)` and trying to use each of them to generate `d` finally gives us the flag.

### Challenge Files  

- [output.txt]({static}chall_files/output.txt)
- [bedouin.py]({static}chall_files/bedouin.py)


### Solve Files  

- [solve.py]({static}sol_files/solve.py)

