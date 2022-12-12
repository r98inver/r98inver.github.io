---
Title: EmoGigi
Date: 2022-12-08 19:04:09
Category: web
Slug: 2022-reply-web-emogigi
Tags: sql injection, unicode
Summary: An emoji search webpage is vulnerable to sql injection due to incorrect sanitizing of unicode characters.
Ctf: reply 2022
Flag: {FLG:O0O0OP5_1_H4V3_B33N_PWN3D_(54DF4C3)!}
Status: published
---

## Solution

I solved this challenge together whit [@Teuler27](https://ctftime.org/user/145398).  
The web page of the challenge consists in a container showing a lot of emoji, divided in custom categories; they can be filtered using an *Emoji Search Box* which immediately suggests a SQL Injection. However, if we search for standard SQL payloads like `'`, `SELECT` or `WHERE` into the box, instead of emoji categories we get a banner with a twisting *questioning hand* emoji saying
![Photo]({attach}chall_files/marcell.png)

We are also provided a leak of the source code in `Message.txt`:
```python
def search():
    # [... SNIP ...] Init the variables here
    
    # Custom SQL filter
    query = sqlfilter(request.form['query'])
    
    # [... SNIP ...]

    if query is None:
        # [... SNIP ...] Return an error here
    else:
        # Normalize weird chars here
        norm = unicodedata.normalize("NFKD", query).encode('ascii', 'ignore').decode('ascii')
        
        # Custom HTML filter
        query = htmlfilter(norm)
        
        conn = sqlite.connect('./emoji.db')
        cur = conn.cursor()

        # Prefix:   f09f90
        # Range:    80;c0
        # Category: animals
        result = cur.execute("SELECT prefix,range,category,id FROM emoji WHERE category like '%" + query + "%'").fetchall()
        conn.close()

        # No Results
        if len(result) == 0:
            return index()

        # [... SNIP ...] Build the results table here
        for r in result:
            rng = r[1].split(';')
            emoji += '<div class="category"><div id="lh"></div>' + r[2].upper() + '<div id="rh"></div></div>'
            emoji += emoji_gen(bytes.fromhex(r[0]), int(rng[0], 16), int(rng[1], 16))
            
        # [... SNIP ...]

    return render_template('index.html', error=error, emoji=emoji, pages=pages, query=query), 200
```

Probably, `sqlfilter()` detects our payloads and returns the *Marcell\*!* alert. But the vulerability here is that the string is unicode normalized *after* the SQL filter. This suggests [Unicode Injection](https://book.hacktricks.xyz/pentesting-web/unicode-injection). Our suspects were enforced by the fact that we found online many emoji payloads for SQL injection.  
So we tried to inject unicode payloads, like `\uff07` for `'` and `\uff08` for `(`. They passed the `sqlfilter()` function, but when normalized in the second step allowed us to execute SQL injection. Encoding literal SQL commands was even easier, since letters with accents are normalized, so for example `SèLECT` was a valid command passing the filter.  
From this point, dump the whole database was quite straightforward. From the leaked message we know that each emoji query asks for four values, `prefix`,`range`,`category` and `id`. While simple operations are performed on `prefix`,`range` and `id`, `category` is displayed unchanged. So that's our endpoint for displaying the db dump. Moreover, we know sample values for each of the three other columns. Finally notice that the `category` field controls the header of the page, so website pagination allowed us to recover multiple results at once. The query we performed, in order, was:

- `xxx\uff07 uniòn sèlect \uff07f09f90\uff07,\uff0780;c0\uff07,name,1 FRòM sqlite_schema WHèRè name likè \uff07%`, from which we found a table `R3PLYCH4LL3NG3FL4G`;
- `xxx\uff07 uniòn sèlect \uff07f09f90\uff07,\uff0780;c0\uff07,name,1 FRòM PRAGMA_TABLE_INFO\uff08\uff07R3PLYCH4LL3NG3FL4G\uff07\uff09 WHèRè name likè \uff07%`, from which we discovered that our table has only one column, `value`;
- finally, `xxx\uff07 uniòn sèlect \uff07f09f90\uff07,\uff0780;c0\uff07,value,1 FRòM R3PLYCH4LL3NG3FL4G WHèRè value likè \uff07%` gave us the flag.

#### Challenge Files  

- [Message.txt]({static}chall_files/Message.txt)

#### Solve Files  

- [solve.py]({static}sol_files/solve.py)
