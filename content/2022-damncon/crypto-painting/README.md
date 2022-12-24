---
Title: Painting
Date: 2022-12-24 17:38:27
Category: crypto
Slug: 2022-damncon-crypto-painting
Tags: hexahue encoding, image processing
Summary: We are given a hexahue encoded image that decodes to Base64, then to morse, and finally gives the flag.
Ctf: damncon 2022
Flag: DAMNCON{T3Y_Y0U3_LUCK_M1GHT_Y0U_G3T_SUCC35}
Description: Majnu Bhai has decided to auction this beautiful painting. Help the Buyers to Understand what painting wants to say.
Status: published
---

## Solution

The challenge file contains a single image:
![Photo]({static}chall_files/img.jpg)

This is clearly [Hexahue](https://www.boxentriq.com/code-breaking/hexahue) encoding, however it seems hard to solve manually due to the high number of boxes. The hardest part of the challenge was actually to automate the process, using the `PIL` python library. The main steps were:

1. Split the big image into single character blocks; to do so, I computed the size of each box and the average distance between blocks both orizontally and vertically. After having the approximate position of each box, I cropped them removing `3` extra pixel from each side to be sure not to include the background. All the cropped images were then saved into a new folder.
2. Next step was to parse the images. To do so, I took the average color value on `4x4` pixel blocks from top, middle and bottom (both left and right) of the image. The average on each `RGB` component was then rounded to the closest value among `0`, `127` and `255`, due to the nature of the colors in the *hexahue* encoding. Each color was finally mapped to a color code, like `R` for red, `G` for green and so on. So each box is translated into a 6 digit string.
3. Finally, the strings are manually mapped to the corresponding alphabetic character.

The result was a long string:
``` 
IC0GLI4ULS0GLS4TLSAULI0TLI0GLS4TLSATLS0TLSAULI0GLI4ULS0GLI4TLS4TIC4TLI4GLI4TIC0ULS4GLS4TIC4ULS0ULSATLSAULS0TLSATLS4GLI4ULIATIC4ULS0ULSATLI0TIC0TLS0TIC4ULSAULI0TLI0GLS0UIC4ULI0TIC0GLI4TLS4TIC4ULIAULI0GLS4TLIATLI0UIC4ULI0TIC4ULI4UIA
```
First of all, it can be observed that only a few characters appear. This means that the challenge would probably be feasible also by hand; however, I think the coding approach was much better since it's reusable, less error-prone and probably faster anyway.   
That said, this string looks pretty much some repeated text encoded into `Base64`. However, padding and decoding it gives
```
-\x06,\x8e\x14--\x06-.\x13- \x14,\x8d\x13,\x8d\x06-.\x13- \x13--\x13-\x14,\x8d\x06,\x8e\x14--\x06,\x8e\x13-.\x13 .\x13,\x8e\x06,\x8e\x13 -\x14-.\x06-.\x13 .\x14--\x14- \x13- \x14--\x13- \x13-.\x06,\x8e\x14,\x80\x13 .\x14--\x14- \x13,\x8d\x13 -\x13--\x13 .\x14- \x14,\x8d\x13,\x8d\x06--\x14 .\x14,\x8d\x13 -\x06,\x8e\x13-.\x13 .\x14,\x80\x14,\x8d\x06-.\x13,\x80\x13,\x8d\x14 .\x14,\x8d\x13 .\x14,\x8e\x14 
```
We see some dashes and points, suggesting Morse Code, but this is not usable. My first guess was that since *hexahue* is case insensitive something got lost in the passage, and so I tried to recover it. I got some better results by looking at valid `Base64` chunks and lowering `g`, `t` and `u` but nothing completely clean. After being stuck for a while on this point, I realized that on the challenge website they explicitly said to send the long string to the support team, and so I did. They answered me back with this new string:
```
IC0gLi4uLS0gLS4tLSAuLi0tLi0gLS4tLSAtLS0tLSAuLi0gLi4uLS0gLi4tLS4tIC4tLi4gLi4tIC0uLS4gLS4tIC4uLS0uLSAtLSAuLS0tLSAtLS4gLi4uLiAtIC4uLS0uLSAtLi0tIC0tLS0tIC4uLSAuLi0tLi0gLS0uIC4uLi0tIC0gLi4tLS4tIC4uLiAuLi0gLS4tLiAtLi0uIC4uLi0tIC4uLi4uIA
```
which explains why my approach didn't work, even if I was close: some `I` are left uppercase, while some are lowered. From this `Base64` decode gives
```
- ...-- -.-- ..--.- -.-- ----- ..- ...-- ..--.- .-.. ..- -.-. -.- ..--.- -- .---- --. .... - ..--.- -.-- ----- ..- ..--.- --. ...-- - ..--.- ... ..- -.-. -.-. ...-- ..... 
```
which is the Morse Code for `T3Y_Y0U3_LUCK_M1GHT_Y0U_G3T_SUCC35`, which wrapped gives the flag. 

### Challenge Files  

- [img.jpg]({static}chall_files/img.jpg)


### Solve Files  

- [solve.py]({static}sol_files/solve.py)

