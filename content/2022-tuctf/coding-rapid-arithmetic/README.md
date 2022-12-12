---
Title: Rapid Arithmetic
Date: 2022-12-09 19:04:09
Category: coding
Slug: 2022-tuctf-coding-rapid-arithmetic
Tags: parsing
Summary: A server asks us to solve quickly math operations, first written normally, then encoded in natural language, roman numbers, morse and a wierd custom multiline encoding. Solving them all gives us the flag.
Ctf: tuctf 2022
Flag: TUCTF{7h3_k1n6_0f_7h3_m47h_c457l3_15_m3_425927}
Status: published
---

## Solution

I solved this challenge together with [@vikvdl](https://ctftime.org/user/121116).

We are given a netcat endpoint that ask us to solve math operations. After the first one, which was always `100x25`, the operations immediately became very hard and confused. However, they always consisted in standard operations; hence a simple `eval()` would solve them.  
After a while the remote server started to send us, together with the operation, also a malicius python script that if passed to `eval` could scramble our running program; luckily, we checked for that before, so we got an error instead of its exectution. After that, we just skipped all the rows containing `exec`.  
The next step was to solve operation encoded in natural language. We found a very well written python library for that, called [number-parser](https://github.com/scrapinghub/number-parser). The only problem was that the server passed thousands like `one thousand, one hundred` and this was parsed as `1000 100` due to the `,`. However replacing the comma with an empty space solved the problem.
After that we got roman numerals, for which we discovered python has a builtin [library](https://pypi.org/project/roman/) (why?), and then morse code, potentially hard to parse due to the presence of `-`. But checking for many points finally did the job.  
The last level was much harder. For a long time, we couldn't figure out what was going on. We keep getting lines like  
```
3333  44  44 777777  9999          3333   2222   3333   2222
```
Moreover, the script was taking much time to execute due to the huge number of requests to be made to solve the previous level, and every time we missed one of those answer (basically every time) we got kicked out and had to restart, leading to a very few examples. After a while, we figured out that the server message was multiline, looking like
```
44  44  0000  44  44  9999          3333   8888   0000   2222
44  44 00  00 44  44 99  99        33  33 88  88 00  00 22  22 
444444 00  00 444444  99999  ====     333  8888  00  00    22  
    44 00  00     44     99        33  33 88  88 00  00   22   
    44  0000      44  9999          3333   8888   0000  222222
```
Parsing it was not trivial, but we noticed that looking only at the third line and replacing `00 00` with `00` we had 8 chunks of number plus one or two (the `-` sometimes appeared before the first number) chunks of sign. After solving that, we finally got the flag.

#### Solve Files  

- [parser.py]({static}sol_files/parser.py)
- [solve.py]({static}sol_files/solve.py)
