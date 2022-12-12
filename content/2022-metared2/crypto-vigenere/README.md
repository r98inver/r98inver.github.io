---
Title: Vigenere
Date: 2022-10-01 12:23:10
Category: crypto
Slug: 2022-metared2-crypto-vigenere
Tags: rep key xor
Summary: We target an alternative Vigenere cipher that becomes a repeated key xor cipher in an unknown language.
Ctf: metared2 2022
Flag: CTFUA{11_odiabpcsetf_Hungarian}
Status: published
---

## Solution

We are targeting an alternative vigenere cipher. The description provides us most of the insights we need to solve it:

- the plaintext and the ciphertext are bytes that can go from 0 to 256;
- the key, however, is composed only by alphabetic chars from `a` to `z`;
- the plaintext is not english, but instead a foreign language that must be detected as a part of the flag.

We have a mix of Vigenere and XOR ciphers vulnerabilities. Of course we need to exploit the fact that the key is only composed by alphabetic characters to obtain the more likely ones. However, since we do not know the plaintext language, character frequencies cannot be used to analyize the key. Instead, we have to rely on the fact that most (but not all) characters of the plaintext will be printable ASCII, which is a standard XOR technique.  
Another important aspect is how the key is encrypted. We are told that the cipher is *additive*, but not if it is XOR additive or Vigenere additive. The alphabetic key seems to suggest the second option, which is confirmed after some trials: so for example `a` moves the byte values by one, `b` by 2 and so on. To decrypt we must hence subtract values corresponding to those letters.  
We are now ready to build the actual decryption algorithm. We are told that the flag will be `keylen_key_lang` where `lang` is the language of the plaintext. Since we do not now the keylength, we need to bruteforce it in a reasonable range (we choose `2-30`). For each possible lenght `l`, we split the ciphertext in chunks of length `l` and try to decrypt each chunk with any possible letter. In this way for each position we guess the best key bit and than see for which length we get a better overall result. As stated before, for better overall result we mean the resulting plaintext with highest number of ASCII printable characters.  
After some trial and error, we obtain the best result for `l=11`. The correspondent key is `odiabpcsetf` and the text, which is filled with some random bytes, is detected by Google Translate as Hungarian. This gives us the flag.

#### Challenge Files  

- [critpograma.txt]({static}chall_files/criptograma.txt)

#### Solve Files  

- [solve.py]({static}sol_files/solve.py)
