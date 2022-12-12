# My simple blog

This project is built using [Pelican](https://docs.getpelican.com/en/latest/index.html), a python based static site generator.

The site is served on (r98inver.github.io)[r98inver.github.io].

### Build

To build the site locally, run `make devserver`.

## Deploy
Run `pelican -s publishconf.py`, then push on git.

### Site Structure

The site content is inside the `content/` foder (you don't say). There is a `pages/` folder for static pages, and an `images/` foder for static images (those are automatically copied in the generated site). Beside that, every cft has it's own folder. They are numbered by year, like `2022-my-ctf`, and the static ones have just some zeros before like `00-natas`. Inside a ctf's folder, there are the challenges, named by `{category}-{slug}`. This simplifies search and generation. Inside every challenge's folder, there is a `README.md` file (the actual writeup) that is read by pelican and transformed into html. Eventually, there are two more folders `sol_files/` and `chall_files/` containing the solution and the challenge files respecively.

### Writeupper

The prupose of the file `writeupper.py` is to take a challenge folder and automatically generate the website folder from it. Some info:

- Only challenges starting with `solved-` are parsed;
- Only subfolders `sol_files/` and `chall_files/` are copied; if a folder does not contain any of those, is skipped;
- Optionally, a file `flag.txt` can be used to recover the flag and a file `desc.txt` can be used to recover the challenge description;
- The second part of the name is the category, followed by chall name (like `solved-crypto-challenge-name`);
- A `TODO.md` file is updated for each challenge generated.

#### Usage

- `chmod +x writeupper.py`
- Configure the values inside
- Then just run it

#### Ideas

- generates content as hidden
