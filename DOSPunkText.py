import os
import sys
import platform
import types
import json
from PIL import Image, ImageOps, ImageFont, ImageDraw, ImageEnhance 
if sys.platform != 'Windows':
    from colortrans import rgb2short

char_font = ImageFont.truetype("BlockZone.ttf", 160) # font used for matching
font_blocks = {}      # dictionary - key = unicode char, value = font record (hash, fg, bg)
image_blocks = []     # array of images - the dos punk image split into charcter blocks 
debug = False         # save the font & image blocks created for debugging

dirname = os.path.dirname(__file__)
dir_punk_blocks = os.path.join(dirname, 'punk-blocks')
dir_font_blocks = os.path.join(dirname, 'font-blocks')

# console codes for reversing character
RESET = "\033[0;0m"
REVERSE = "\033[;7m"

# compute the hamming distance between two hashes
def hash_distance(hash1, hash2):
    if len(hash1) != len(hash2):
        raise ValueError('Hamming distance requires two strings of equal length')

    return sum(map(lambda x: 0 if x[0] == x[1] else 1, zip(hash1, hash2)))

# Compute the average hash of the given image.
def average_hash(image, hash_size=80):
    
    # resize image and convert it to grayscale.
    image = ImageOps.autocontrast(image)
    image = ImageOps.grayscale(image)
    image = image.resize((hash_size, hash_size), Image.ANTIALIAS)
    
    pixels = list(image.getdata())
    avg = sum(pixels) / len(pixels)

    # Compute the hash based on each pixels value compared to the average.
    bits = "".join(map(lambda pixel: '1' if pixel > avg else '0', pixels))
    hashformat = "0{hashlength}x".format(hashlength=hash_size ** 2 // 4)
    return int(bits, 2).__format__(hashformat)

# Compute the hamming distance between two images
def distance(image1, image2):
    hash1 = average_hash(image1)
    hash2 = average_hash(image2)
    return hash_distance(hash1, hash2)

# Match images to a tolerance
def images_match(image1, image2, tolerance=100):
    return distance(image1, image2) <= tolerance

# Match hashes to a tolerance
def hashes_match(hash1, hash2, tolerance=100):
    return hash_distance(hash1, hash2) <= tolerance

# Create an image of a character in the font
def create_char_image(char_code):
    image = Image.new('RGB', (80, 160), color = 'white')
    char = chr(char_code)
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), char, font=char_font, fill=(0,0,0))
    image = image.convert('L')
    return image      

# Returns the first pixel that matches the color
def get_pixel_by_color(image, color):
    for y in range(0, image.height):
        for x in range(0, image.width):
            if (image.getpixel((x,y)) == color):
                # +5 to to choose a pixel not effected by any antialiasing if image has
                # been resized, bit of a hack - there must be a better way to do this!
                return ((x+5,y+5)) 
    return ((-1,-1))

# Creates a font record
def create_font_record(image):
    rec = types.SimpleNamespace()
    rec.hash = average_hash(image)
    rec.fg_pixel = get_pixel_by_color(image, 0) # fg pixel xy
    rec.bg_pixel = get_pixel_by_color(image, 255) # bg pixel xy
    return rec
  
# create an image for each character in the font and store
# the average hash of the image against the unicode 
def create_font_blocks():
    # create images of non-blank characters from the font
    for char_code in range(0x0021, 0x0266C):
      image = create_char_image(char_code)
      image = image.convert("L")
      clrs = image.getcolors()
      if (len(clrs)>1): 
          font_blocks[char_code] = create_font_record(image)
          if debug:
              image.save(f"{dir_font_blocks}/{char_code}.png")
    # add the space character back in
    image = create_char_image(0x00A0)
    image = image.convert("L")
    font_blocks[0x00A0] = create_font_record(image)
        

# split the DOS punk image up into chracter blocks
# width 80, height 160 in 
def create_punk_blocks(filename):
    image = Image.open(filename).convert('RGB')

    # check image is square
    if (image.width != image.height):
        print('Image must have equal width & height')
        sys.exit()

    # resize to 1280x1280 if required
    if (image.width !=1280):
        if optimize:
            # optimize for character matching
            image = image.resize( (1280, 1280), Image.LANCZOS)
        else:
            # optimize for color matching
            image = image.resize( (1280, 1280), Image.NONE)
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(4)
        if debug:
            image.save(f"{dir_punk_blocks}/image.png")

    # split image up into blocks
    block_num = 1
    for y in range(0, 1280, 160):
        for x in range(0, 1280, 80): 
            block_image = image.crop((x, y, x+80, y+160)) 
            image_blocks.append(block_image)           
            if debug:
              block_image.save(f"{dir_punk_blocks}/{block_num}.png")
            block_num += 1

# return full file path to file
def check_relative_filename(filename):
    if not os.path.isfile(filename):
       relative = os.path.join(dirname, filename)
       if os.path.isfile(relative):
           filename = relative
    return(filename)

# print coloured chracter to the console
def print_color(char, fg, bg):
    if platform.system() == 'Windows':
       ## rgb escape code  works on windows console
       sys.stdout.write("\033[38;2;{};{};{}m".format(fg[0], fg[1], fg[2]))
       sys.stdout.write("\033[48;2;{};{};{}m".format(bg[0], bg[1], bg[2]))
    else:
       # translate rgb colour to closest coulor in 256 bit xterm pallet
       fg_clr = rgb2short(fg[0], fg[1], fg[2])
       bg_clr = rgb2short(bg[0], bg[1], bg[2])
       sys.stdout.write("\033[38;5;{}m".format(fg_clr))
       sys.stdout.write("\033[48;5;{}m".format(bg_clr))
    print_sl(char)
    
# print to console without new line
def print_sl(value):
    print(value, sep='', end='', flush=True)

# creates a dict to hold the metadata
def create_metadata_dict():
    rec = {}
    rec["text"] = ""
    rec["pallet"] = []
    rec["fgColors"] = []
    rec["bgColors"] = []
    return(rec)

# adds a colour to the pallet & returns the index
def pallet_index(color, pallet):
    if color not in pallet:
        pallet.append(color)
    return pallet.index(color)

# match the image block to the font block & output the unicode character
# to the console & text buffer
def match_blocks():
    text = ""
    metadata = create_metadata_dict()

    for num, image in enumerate(image_blocks, start=1):
    
        # output a new console line every 16 blocks
        if ( ((num % 16) == 1) and (num !=1)):
            sys.stdout.write(RESET)
            print("")
            text += "\r\n"

        # get the hash & inverse hash for the block we're matching
        image = image.convert("RGB")
        img_hash = average_hash(image)
        img_hash_inv = average_hash(ImageOps.invert(image))

        # setup some default values for the match
        best_score = sys.maxsize
        char_code = 0
        inverted = False
        
        # match the block or it's inverse to a character in the font
        for key in font_blocks:
            char_hash = font_blocks[key].hash
            # match against font block
            distance = hash_distance(char_hash, img_hash)
            if distance < best_score:
                best_score = distance
                char_code = key
                inverted = False
            # match against reversed font block    
            distance = hash_distance(char_hash, img_hash_inv)
            if distance < best_score:
                best_score = distance
                char_code = key
                inverted = True
  
        text += chr(char_code)
        metadata["text"]+= chr(char_code)
        fg = image.getpixel(font_blocks[char_code].fg_pixel)
        bg = image.getpixel(font_blocks[char_code].bg_pixel)
        fg_idx = pallet_index(fg, metadata["pallet"])
        bg_idx = pallet_index(bg, metadata["pallet"])
        metadata["fgColors"].append(fg_idx)
        metadata["bgColors"].append(bg_idx)

        print_color(chr(char_code), fg, bg)
        
        if debug:
            sys.stdout.write(RESET) 
            print(f" Block:{num} Matched:{char_code} Score:{best_score} Inverted:{inverted}")

    # reset the console color    
    sys.stdout.write(RESET)
    return (text, metadata)

# ----------------------------------------------------

# set terminal to color on Windows platforms so we can
# display reversed characters in the console
if platform.system() == 'Windows':
    os.system('COLOR') 

# get the filename from args
filename = check_relative_filename(sys.argv[1])
if not os.path.isfile(filename):
    print(f"file not found: {filename}")
    exit()

# get flags from args
optimize = "--optimize" in sys.argv
debug = "--debug" in sys.argv

# in debug mode create the dirs to store the punk & font blocks 
if debug:
    if not os.path.isdir(dir_font_blocks):
      os.makedirs(dir_font_blocks)
    if not os.path.isdir(dir_punk_blocks):  
        os.makedirs(dir_punk_blocks)

if platform.system() == 'Windows':
    print("") # need an extra line on windows

# create image bloack form the font 
create_font_blocks()           
# split the DOS punk image into blocks
create_punk_blocks(filename)  
# match the blocks (& output to console) 
result = match_blocks()
text = result[0]
metadata = result[1]              

# save the output to a text file
text_filename = os.path.splitext(filename)[0]+".txt"
with open(text_filename,"wb+") as f:
    f.write(text.encode('utf-8'))
    f.close()

# save metadata as json
json_filename = os.path.splitext(filename)[0]+".json"
with open(json_filename, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, ensure_ascii=False, separators=(',', ':'))

print("")  
if not platform.system() == 'Windows':
    print("") # need an extra line on osx
