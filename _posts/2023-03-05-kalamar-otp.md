---
title: KalamarCTF - OTP
date: 2023-03-05 20:00:00 +0100
categories: [Ctf Writeups, Crypto]
tags: [otp, single-key-xor] # TAG names should always be lowercase
math: true
---

Two interesting challenges about OneTimePassword (OTP) encription. In both cases we have a key reuse, which allows us to reduce to breaking single-key-xor in an obvious (BabyOTP) and less obvious (EasyOTP) way.

> **Event Link:** [KalmarCTF](https://ctftime.org/event/1878/)    
  **Solution Script:** [solve_otp.py](/assets/ctf/23-kalmar/solve_otp.py)
{: .prompt-info }

## BabyOTP - Challenge Description

*BabyOTP* is the first of the two related challenges on **OTP**. The most relevant part of the script is the function `encrypt_otp`:
```python
PASS_LENGTH_BYTES = 128
def encrypt_otp(cleartext, key = os.urandom(PASS_LENGTH_BYTES)):
    print(f'{key = }')
    ciphertext = bytes([key[i % len(key)] ^ x for i,x in enumerate(cleartext.hex().encode())])
    print(f'{ciphertext = }')
    return ciphertext, key
```
This function is called twice. First of all, a random password is generated and encrypted with OTP and a random key:
```python
password = os.urandom(PASS_LENGTH_BYTES)
enc, _ = encrypt_otp(password)
print(f'Here is my password encrypted with a one-time pad: {enc.hex()}')
```
After that, we are allowed to provide a permutation. If the permutation is valid, the password is permuted and OTP-enrcypted again, and again sent to us.
```python
permutation = input('Permutation: ')
permutation = [int(x) for x in permutation.strip().split(',')]
assert set(permutation) == set(range(PASS_LENGTH_BYTES))
enc, _ = encrypt_otp(bytes([password[permutation[i]] for i in range(PASS_LENGTH_BYTES)]))
print(f'Here is the permuted password encrypted with another one-time pad: {enc.hex()}')
```
Finally, we are asked the password. If we are able to guess it, the server gives us the flag.

## BabyOTP - Solution

The behaviour of this challenge is higly different from what it looks like. This code has three main issues:

1. in `encrypt_otp`, `cleartext` and `key` are supposed to have the same length to apply a proper OTP encryption. However, the encryption is applied to `cleartext.hex()`, and for every byte of `cleartext` we will obtain 2 hexadecimal characters. The consequence is that `cleartext.hex()` is twice longer than `key`; this is the first key reuse.
2. In `encrypt_otp`, `key = os.urandom(PASS_LENGTH_BYTES)` generates the key in a secure way, but as a default argument the key is generated [only the first time](https://stackoverflow.com/questions/62412902/python-function-default-argument-random-value) and then fixed. This means that all the encryption with no key provided will use the same key.
3. Finally, `assert set(permutation) == set(range(PASS_LENGTH_BYTES))` is supposed to check that we provide a valid permutation. However, it doens't check the length of the permutation. This means that if we send 128 times `0` and then all the numbers from `1` to `127` this will be a valid permutation, but the actual permutation applied to the password will only encrypt the first byte 128 times.

These issues allow us to come up with a simple solution. First of all, we send a permutation that repeats the first character of the password for 64 times, followed by the first 64 characters.    
```python
permutation = [b'0']*(PASS_LENGTH_BYTES//2) + [str(i).encode() for i in range(PASS_LENGTH_BYTES)]
```
Notice that to pass the check we have to append the number from 64 to 127 to the permutation at the end. However, those numbers are ignored when building the permutation. Now recall that the password hex encoded and then xored on the key. The key is 128 bytes, and hence get xored with the hex value of the first character of the password (two bytes) repeated 64 times. After that, the key is xored again with the first 64 characters of the password. We also know that the two values that are repeatedly xored against the key are valid hex characters, i.e. in `0123456789abcdef`. We only have to break a simple single-key-xor to retrieve the key, and then use it to recover the full password from the first encryption `enc1`.
```python
k1 = enc2[:(PASS_LENGTH_BYTES)]
k2 = enc2[(PASS_LENGTH_BYTES):]
cset = set('1234567890abcdef'.encode())
for c in zip(cset, cset):
    guess_key = xor(k1, bytes(c))
    guess_pass = xor(guess_key, k2)
    if set(guess_pass).issubset(cset):
        pass1 = guess_pass
        break
k1 = enc1[:(PASS_LENGTH_BYTES)]
k2 = enc1[(PASS_LENGTH_BYTES):]
key = xor(k1, pass1)
pass2 = xor(k2, key)
password = pass1 + pass2
r.sendline(password)
r.interactive() # The flag is kalmar{why_do_default_args_work_like_that_0.0}
```

## EasyOTP - Challenge Description

Two of the three issues of *BabyOTP* are fixed in *EasyOTP*. The `encrypt_otp` function becomes
```python
def encrypt_otp(cleartext):
    key = os.urandom(len(cleartext))
    ciphertext = bytes([key[i % len(key)] ^ x for i,x in enumerate(cleartext.hex().encode())])
    return ciphertext, key
```
and a check on the length of the permutation is performed:
```python
permutation = [int(x) for x in permutation.strip().split(',')]
assert len(permutation) == PASS_LENGTH_BYTES
assert set(permutation) == set(range(PASS_LENGTH_BYTES))
```
The rest of the challenge is identical to *BabyOTP*.   

## EasyOTP - Solution

The second and third issues of *BabyOTP* are now fixed. However, the first one is still there: the password is hex encoded before xoring it with the key, so we have a key reuse. Let see what this implies. We will assume for simplicity `PASS_LENGTH_BYTES = 4`. If we denote the 4 bytes of the key as $k_1,k_2,k_3,k_4$ and the 8 bytes of `hex(password)` as $p_1,p_2,\dots, p_8$, the 8 bytes of `enc1` will be $k_1\oplus p_1,\dots,k_4\oplus p_4,k_1\oplus p_5,\dots,k_4\oplus p_8$. Now since the xor is self-inverse, we have $(k_1\oplus p_1) \oplus (k_1\oplus p_5) = p_1 \oplus p_5$. Similarly, from the first encoded password we obtain $p_2\oplus p_6$, $p_3 \oplus p_7$ and $p_4 \oplus p_8$.    
Now we chose as permutation `[0,1,3,2]`, i.e. we leave unchanged the first half of the password and shift the second half by one. Since the characters are doubled, the new password will be $p_1,\dots,p_4,p_7,p_8,p_5,p_6$. From here, we obtain $p_1\oplus  p_7$, $p_2 \oplus p_8$ and so on. Now look at the odd position. We know $p_1 \oplus p_5$ and $p_1 \oplus p_7$. But from the first one, we also have $p_3 \oplus p_7$, so we can compute $(p_1 \oplus p_7) \oplus (p_3 \oplus p_7) = p_1 \oplus p_3$. Since the right half of the password is shifted by 1 in the permutation, we can iteratively obtain $p_1 \oplus p_i$ for every odd $i$ (and of course the same reasoning applies to the even ones). In this way we reduced the problem to a single-key-xor on $p_1$, which is made even simpler by the fact that both $p_1$ and the $p_i$ must be valid hex characters. Since for each xor we have 128 samples, it is quite easy to recover $p_1$ and $p_2$ and from there the whole password. The code implementing this logic can be found at [solve_otp.py](/assets/ctf/23-kalmar/solve_otp.py).