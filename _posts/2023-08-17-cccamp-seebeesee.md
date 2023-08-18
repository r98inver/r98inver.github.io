---
title: CCCamp - SeeBeeSee
date: 2023-08-18 13:00:00
categories: [Ctf Writeups, Crypto]
tags: [cbc bitflipping] # TAG names should always be lowercase
math: true
---

The server accepts encrypted text, decrypts it using `AES-CBC` and an unknown key, and executes it. We are provided a sample script, that we can tamper in different points in order to get the key and hence arbitrary code execution.

> **Event Link:** [CCCamp 2023](https://ctftime.org/event/2048/){:target="_blank"}   
{: .prompt-info }


## Challenge Description

The server gives us access to two important functions. The first one is the `runscript` function:

```python
def runscript(data):
    try:
        global result
        result = b""
        decrypted = decrypt(data, KEY)
        print("---DEC---")
        print(decrypted)
        print("---EOF---")
        dec = decrypted.decode("utf-8", "replace")
        print(dec)
        print("---")
        exec(dec, globals())
        print("r:", result)
        return True
    except Exception as e:
        print("decryption error?")
        print(e)
        return False
```

We can provide `base64` encrypted data, which is decrypted using `AES-CBC` with an unknown `KEY` and passed to `exec` to be executed as python code. After that, the value of the variable `result` is printed.    
The second important function is `getsample`:

```python
def getsample():
    code = b"""
exit()
#AAAAAAAAA
#AAAAAAAAAAAAAAAA
a = r"0000000000000000000000000000"
if a!=r"0000000000000000000000000000":
    testok = True
if testok:
    result = b"See? " + KEY[:-4]
#reset 4 security
result = b"nope"
"""

    cipher = AES.new(KEY, AES.MODE_CBC,iv=b'\x00'*16)
    ciphertext = cipher.encrypt(pad(code, AES.block_size))
    return base64.b64encode(ciphertext)
```

We have access to the encrypted version of `code`, and hence we can execute it. However, the `exit()` command on the first line stops the execution every time we send it to the server.

## Solution

Let's walk through the solution step by step.

### Step 1: get rid of `exit()`

First of all, we have to get rid of the `exit()` function at the beginning of the code. `AES` encrypts chunks of 16 bytes, and `CBC` operation mode implies that if we modify the first chunk also the second one will be affected. If we split `code` in 16-bytes chunk, we get:
```python
b'\nexit()\n#AAAAAAA'
b'AA\n#AAAAAAAAAAAA'
b'AAAA\na = r"00000'
b'0000000000000000'
b'0000000"\nif a!=r'
b'"000000000000000'
b'0000000000000":\n'
b'    testok = Tru'
b'e\nif testok:\n   '
b' result = b"See?'
b' " + KEY[:-4]\n#r'
b'eset 4 security\n'
b'result = b"nope"'
b'\n'
```
So if we manage to get a chunk that decodes to some text (not necessarily ascii) beginning with a `#`, the first line of the text will be a python comment, and the second one as well (since we will probably modify also the `\n`). The third one, however, is safe, so the `AAAA` in the beginning will fall into the comment but then the `\n` allows us to execute the rest of the code. On average, we expect `1/256` ciphertext to produce a plaintext beginning with `#`, so we can just ask the server to decrypt and execute chunks of 16 random bytes until we get no error:
```python
def bf_cip(msg, r):
    r.sendline(b'1')
    r.recvuntil(b'>')
    r.sendline(b64.b64encode(msg))
    lines = r.recvrepeat(timeout=1).decode()
    if not "error" in lines:
        log.info(f'msg: {msg}')
        log.success("SUCCESS")
```
And we get a hit soon with `msg = b'\x10\x90\x17\x81\x18r\x9aq%\xd1\xf6|\x1b\t\x9d'`.

### Step 2: bitflipping

Now that the first and second line are not executed, we can tamper with the rest of the code. We need to modify the value of `a` in the third line in order to enter the `if`. But since also the second line is a comment now, we can easily [bitflip](https://crypto.stackexchange.com/a/66086){:target="_blank"} it to arbitrarily modify the third line and hence the value of `a`. We also need to remove the last three chunks, that reset the value of `result`.

```python
cip = bytes_to_chunks(cip)
cip[0] = b'\x10\x90\x17\x81\x18r\x9aq%\xd1\xf6|`\x1b\t\x9d'
cip[1] = xor(cip[1],  b'\x00'*15 + xor(b'0', b'1'))
cip = b''.join(cip[:-3])
```
Sending this payload to the server gives us `r: b'See? e87feb770447'`.

### Step 3: get the key

We know that four characters of the flag are missing. However we know a pair plaintext-ciphertext (first chunk of `code` for instance), so we can quickly bruteforce them.

```python
key = b'e87feb770447'
plain = b'\nexit()\n#AAAAAAA'
cip = b'\x8e\x9a\xc4\xf9LBa\xd2\x91\xea\xdc\r\xc5\xf3\x01\xeb'
for cmb in product(b'abcdef1234567890', repeat=4):
    k = key + bytes(cmb)
    
    cipher = AES.new(k, AES.MODE_CBC,iv=b'\x00'*16)
    test_cip = cipher.encrypt(plain)
    if test_cip == cip:
        log.success('Key found')
        log.success(f'{k = }')
        exit()
```
This gives us the key: `k = b'e87feb7704477bbc`.

### Step 4: get the flag

With the key, we can encrypt and execute arbitrary code on the server. We can also import `os` to explore the remote server. In `../flag` we finally find the flag: `ALLES!{1m_n3ver_us1ng_cbc_4gaiN!!!1}`.