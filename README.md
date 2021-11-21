# DOS Punk Text

Inspired by [MAX CAPACITY](https://twitter.com/maxcapacity)'s DOS Punks & the amazing DOS Punk community.

DOS Punk Text is a Python 3 script that renders a DOS Punk image as coloured text in the console and exports the text & colour map to a JSON file.

![Alt text](/screenshots/screenshot_1.jpg?raw=true)

The characters in the DOS Punk image are matched against a unicode version of the original DOS Code Page 437 character set using the Hamming distance between average image hashes.

**#DOSLIFE** 

## Requirements

Requires [Python 3](https://www.python.org/downloads/) and the Pillow image processing library:

```bash
pip install pillow
```

For best results use [BlockZone](https://github.com/ansilove/BlockZone) as your console font. A copy of the BlockZone font is included in this repository.

Use the original 1280 x 1280 DOS Punk image where possible. 
For low res images use the --optimize flag to optimize for character matching over color matching.

## Usage

```bash
python DosPunkText.py "path/to/DosPunkImage.png"

# display the DOS Punk image as text in the console
# and export text & colour map to JSON file
python DOSPunkText.py DOSPunk132.png

# optimize character matching over color matching for low res images
python DOSPunkText.py DOSPunk132.png --optimize

# save the DOS Punk & font image blocks used during the matching process
python DOSPunkText.py DOSPunk132.png --debug

```

## Acknowledgments

[MAX CAPACITY](https://twitter.com/maxcapacity), [greencross](https://twitter.com/greencrosslive) and the rest of the DOS Punk community!

[BlockZone](https://github.com/ansilove/BlockZone)'s pixel-perfect recreation of the original IBM VGA font

[PhotoHash](https://github.com/bunchesofdonald/photohash) for the average hash & Hamming distance algorithms

[colortrans](https://github.com/soarpenguin/python-scripts/blob/master/colortrans.py) for converting RGB to 256bit XTERM pallet


## License
[MIT](https://choosealicense.com/licenses/mit/)
