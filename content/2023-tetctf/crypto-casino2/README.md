---
Title: Casino2
Date: 2023-01-02 23:14:56
Category: crypto
Slug: 2023-tetctf-crypto-casino2
Tags: prng, golang
Summary: Breaking the PseudoRandom Number Generator of golang (with some heuristic).
Ctf: tetctf 2023
Flag: TetCTF{______l3ft_0r_r1ght_0r_b0th?______}
Status: published
---

## Solution

This challenge is the follow up of `Casino`, where we have a casino implemented in `golang` and we have to make bets in order to earn money and win the flag. The structure is quite simple, and we are provided some `JSON` APIs to play:

- `{'recipient':'Casino', 'command':'Register', 'username':username}` registers a user; this is achieved in my code via the function `register`;
- `{'recipient':'Casino', 'command':'ShowBalanceWithProof', 'username':username}` gives us the balance, plus a proof of the validity of that balance that we have to exibit in order to obtain the flag once we have enough money; this is done via the `showbalance` function;
- `{'recipient':'FlagSeller', 'command':'PrintFlag', 'balance':balance, 'proof_data':proof}`, where `balance` and `proof` are the result of `showbalance`, gives us the flag; by reading the function in `flag_seller.go`, we notice that this call shows us only the first `l` characters of the flag, where `l` is the bitlength of our balance divided by `8`;
- finally, `{'recipient':'Casino', 'command':'Bet', 'username':username, 'amount':amount, 'n':n}` allows us to bet on one number `n`; the casino then picks a random number between `0` and `2023`, and if we guessed correctly, we are given back our bet multiplied by `2023`, otherwise we loose it; notably, if we make a mistake we are returned the correct number.

We start from a balance of `2023` (let's say they are €). The `Casino` challenge was more of an intrduction, since negative bets are allowed. You can hence earn an illimited ammount of money while losing, and quickly buy the flag. However, this bug is fixed in `Casino2`. This means that we have to actually break the casino.   
The random number is generated using the builtin golang function `rand.Intn(2023)`, which is seeded at the startup via `rand.Seed(int64(binary.LittleEndian.Uint64(tmp)))`. The `tmp` vector is initialized using `cryptorand.Read`, which accordingly to the official golang documentation is cryptographically secure. Breaking the seed is hence not an option. We have then to understand how `rand.Intn` works. This was a very hard step, since I never used golang before (hence I tried to avoid reading the source code, regarding it as the last step) and I didn't find a lot of docs online. After some useless research, including ChatGPT trying to convince me it was a `MersenneTwister` citing some inexistent blogs, I found [this post](https://www.leviathansecurity.com/media/attacking-gos-lagged-fibonacci-generator) affirming that `rand` is implemented in golang as a **Lagged Fibonacci Generator** with equation
```latex
x_n = (x_{n-273} + x_{n-607}) mod (2^{63}-1).
```
This means that we have no control on the first `607` numbers, which we can afford by betting `1€` each time and spending `607€` in total, while recording those numbers. After that, we can use the numbers we stored to compute the upcoming ones and win money.   
I implemented this simple formula, and the result was promising: even if we do not have a complete control of the generator, since we are given outputs `mod 2023` while the exact number are computed `mod 2^63 - 1`, we have a good winning rate, say `1/5`. The fact that on a win our bet is multiplied by `2023` clearly makes it a winning game, but this is not enough. If we keep betting, for example, `1€` each time, we end up earning about `2000€` every 5 bets. However, in order to get the flag, we need a balance of `2^(8*L)` where `L` is the legnth of the flag, something we clearly can't achieve in a reasonable time in this way. We need a big amount to be multiplied by `2023` to make our balance grow up quickly, but not too big, because if for some reason we miss some bets consecutively, we do not want to run out of money. So the final algorithm was:

- fix a bet `b` as `1/10` of the actual balance;
- after a win, check for the flag; if we have it we can break, otherwise restart;
- after a lose, increment a counter but keep betting `b`; when the counter hits `9`, start again computing a new bet.

On top of that, I added a treshold of `5000€` below wich only `1€` bets are allowed due to some rounding problems. It was very easy to reach anyway. This algorithm gives us the flag very quickly (considering that a big amount of time was spent on storing the first `607` numbers). The reason why it's winning is that every time we win a bet, our budget gets multiplied by `~200`. Moreover, since we have a winnig rate around `1/5`, in `9` bets we often win. If we loose, anyway, our budget is divided only by `10`.

### Challenge Files  

- [casino.go]({static}chall_files/casino.go)
- [main.go]({static}chall_files/main.go)
- [flag_seller.go]({static}chall_files/flag_seller.go)


### Solve Files  

- [solve.py]({static}sol_files/solve.py)

