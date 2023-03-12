---
title: HexaHue Decoder
date: 2022-12-24 17:38:27
categories: [Ctf Writeups, Misc]
tags: [hexahue] # TAG names should always be lowercase
# math: true
---

As part of a challenge in the [Damncon 2022](https://ctftime.org/event/1726/) CTF, I had to decode the follownig image:

![](/assets/ctf/22-damncon/hex.jpg)    

This is clearly the [Hexahue](https://www.boxentriq.com/code-breaking/hexahue) Cipher. However, not without surprise, I could not find any automatic image decoder online. All the decoders (like [dcode.fr](https://www.dcode.fr/hexahue-cipher)) let you type your message using the images, which is perfect for small messages but not applicable to this image. I hence decided to go ahed and write a HexaHue decoder by myself.

### Cropping the image

First of all, I had to crop the original image into small pieces, each one representing one hexahue char. This is an easy task for image manipulation libraries like `PIL`. I only had to compute the average size of a block and the average distance between blocks. Then I removed `3` extra pixel from each side to be sure not to include the background. Finally, I saved the blocks in numbered images in the same folder.

### Image to Code

Next step was to parse the images. To do so, I took the average color value on `4x4` pixel blocks from top, middle and bottom (both left and right) of the image. The average on each `RGB` component was then passed to the function `roundcolor` and rounded to the closest value among `0`, `127` and `255`. This is an easy way to prevent mistakes, since those three are the only possible `RGB` values for hexahue encoding. Each color was finally mapped to a color code, like `R` for red, `G` for green and so on. Due to the high number of `G` in color names, I used `D` for black and `X` for gray. So each box is translated into a 6 digit string based on its colors, starting from the top left.

### Code to string

Finally, I wrote a dictionary to map each color combination to the corresponding letter.

> The full **solution script** can be found at [hexahue.py](/assets/ctf/22-damncon/hexahue.py)
{: .prompt-tip }
