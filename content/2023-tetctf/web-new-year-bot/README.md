---
Title: New Year Bot
Date: 2023-01-02 23:14:56
Category: web
Slug: 2023-tetctf-web-new-year-bot
Tags: python eval, bit ops
Summary: We have to forge requests to a form with limited characters allowed in order to exploit an improperly sanitized eval call.
Ctf: tetctf 2023
Flag: TetCTF{JuSt_F0rFunn(^_^}
Status: published
---

## Solution

We are given a webpage that allows us to submit a form via a simple select, and the backend python code. As we see, the page accepts two `POST` parameters, `type` and `number`, plus an optional `GET` parameter `debug` used to print some extra information. They must match the following requirements:

- `greetNumber`, which is the variable for the `number` parameter, must pass the `isidentifier()` python builtin function, which only allows letters, number and undescores (plus no numbers at the beginning);
- `greetType` has to pass through a more complex (and as we will see more vulnerable) sanitization process:
	- first of all, all spaces are removed;
	- then inside `botValidator` each character is checked; if one is found with ASCII value between `57` and `123` (excluded) the parameter is considered not valid;
	- finally, the numbers alone contained in the string are joined together to form a unique number; this number must not be greater than `5`.
- as a last check, the string `"%s[%s]" % (greetType, greetNumber)` is prepared, and if it is found to be longer than `20` characters, an error is returned;
- finally, the prepared string is passed to `eval()`.

The main idea behind this complex procedure is quite simple. The expected input is something like `('NewYearCategoryList', 2)` that should return the third value of the `NewYearCategoryList` list. However, we can easily replace the first parameter with `FL4G`, which is the string that contains the flag. This gets `eval()` executed on expressions like `FL4G[0]` and gives us the first `6` flag characters (from `0` to `5`). We cannot go further, since `6` is not a valid `greetType`.  
But here comes the funny part. First of all, the weird ASCII check allows `-`; so numbers from `-1` to `-5` gives us also the last chars of the flag. Other operations, like `+`, `*` or `**`, plus round brackets are allowed, but `2*3` is read by `botValidator` as the number `23` and hence blocked since greater then `5`. However, the strange `123` ASCII limit allows us to use also the bitwise negation operator `~`. We can hence exploit the fact that `~0 = -1` to build all the missing numbers: for example `(~0+~0)*3 = -6`, and this is a valid expression, since is seen by `botValidator` as `003 < 5`. In the same way, `(~0+~0+~0)**2 = 9`, `-(~0+~0+~0)*4 = -12` and so on. Enabling the `debug` params tells us that the list we are targeting (which is `FL4G`) has `24` elements (characters), so forging the numbers from `1` to `24` in this way gives us the flag.

### Challenge Files  

- [main.py]({static}chall_files/main.py)


### Solve Files  

- [solve.py]({static}sol_files/solve.py)

