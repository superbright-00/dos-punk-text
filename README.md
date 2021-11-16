# DOS Punk Text

Inspired by [MAX CAPACITY](https://twitter.com/maxcapacity)'s DOS Punks & the amazing DOS Punk community.

DOS Punk Text is a Python 3 script that converts a DOS Punk image into a text file and displays the DOS Punk as text in the console.

The characters in the DOS Punk image are matched against a unicode version of the original DOS Code Page 437 character set using the Hamming distance between average image hashes.

![Alt text](/screenshots/screenshot_1.jpg?raw=true)

#DOSLIFE 

## Requirements

Requires [Python 3](https://www.python.org/downloads/) and the Pillow image processing library:

```bash
pip install pillow
```

For best results use [BlockZone](https://github.com/ansilove/BlockZone) as your console font with a black foreground & white background. A copy of the BlockZone font is included in this repository.

## Usage

```bash
python DosPunkText.py "path/to/DosPunkImage.png"

# create a text file from a DOS Punk image & display it in the console
python DOSPunkText.py DOSPunk132.png

# display without reversing characters in the console.
python DOSPunkText.py DOSPunk132.png --noinvert

# save the DOS Punk & font image blocks used during the matching process
python DOSPunkText.py DOSPunk132.png --debug

```

## Acknowledgments

[MAX CAPACITY](https://twitter.com/maxcapacity), [greencross](https://twitter.com/greencrosslive) and the rest of the DOS Punk community!

[BlockZone](https://github.com/ansilove/BlockZone)'s pixel-perfect recreation of the original IBM VGA font

[PhotoHash](https://github.com/bunchesofdonald/photohash) for the average hash & Hamming distance algorithms


## License
[MIT](https://choosealicense.com/licenses/mit/)