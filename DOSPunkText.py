import os
import sys
import platform
from PIL import Image, ImageOps, ImageFont, ImageDraw, ImageEnhance

char_font = ImageFont.truetype("BlockZone.ttf", 160) # font used for matching
font_hashes = {}      # dictionary - key = unicode chr, value = average hash of font char
image_blocks = []     # array of images - the dos punk image split into charcter blocks 
invert_enabled = True # flag - use reverse video when outputting chrs to the console
debug = False         # save the font & image blocks created for debugging
filename = ""         # filename of the DOS Punk Image

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
    
    # resize image and convert it to grayscal.
    image = image.resize((hash_size, hash_size), Image.ANTIALIAS)
    image = ImageOps.grayscale(image)
    
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
    draw.text((0, -1), char, font=char_font, fill=(0,0,0))
    image = image.convert('L')
    return image      

# create an image for each character in the font and store
# the average hash of the image against the unicode 
def create_font_blocks():
    # create images of non-blank characters from the font
    for char_code in range(0x0021, 0x0266C):
      image = create_char_image(char_code)
      image = image.convert("L")
      clrs = image.getcolors()
      if (len(clrs)>1): 
          font_hashes[char_code] = average_hash(image)
          if debug:
              image.save(f"{dir_font_blocks}/{char_code}.png")
    # add the space character back in
    image = create_char_image(0x00A0)
    image = image.convert("L")
    ##image.save(f"{dir_match}/{0x00A0}.png")
    font_hashes[0x00A0] = average_hash(image)

# split the DOS punk image up into chracter blocks
# width 80, height 160 in 
def create_punk_blocks(filename):
    image = Image.open(filename).convert("L")

    # check image is correct reolution
    if (image.width != 1280) or (image.height != 1280):
        print('Please supply the 1280x1280 image of your DOS Punk!')
        sys.exit()

    # split image up intp blocks
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

# print to console without new line
def print_sl(value):
    print(value, sep='', end='', flush=True)

# print to console with reverse characters
def print_char(char, reverse):
    if reverse and invert_enabled:
        sys.stdout.write(REVERSE)        
        print_sl(char)
    else:
        sys.stdout.write(RESET)
        print_sl(char)    

# match the image block to the font block & output the unicode character
# to the console & text buffer
def match_blocks():
    text = ""
    for num, image in enumerate(image_blocks, start=1):
    
        # output a new console line every 16 blocks
        if ((num % 16) == 1):
            sys.stdout.write(RESET)
            print("")
            text += "\r\n"

        # get the hash & inverse hash for the block we're matching
        img_hash = average_hash(image)
        img_hash_inv = average_hash(ImageOps.invert(image))

        # setup some default values for the match
        best_score = sys.maxsize
        char = ""
        invert = False
        
        # match the block or it's inverse to a character in the font
        for key in font_hashes:
            char_hash = font_hashes[key]
            # match against font block
            distance = hash_distance(char_hash, img_hash)
            if distance < best_score:
                best_score = distance
                char = chr(key)
                invert = False
            # match against reversed font block    
            distance = hash_distance(char_hash, img_hash_inv)
            if distance < best_score:
                best_score = distance
                char = chr(key)
                invert = True
            
        # special case - try to work out whether a space 
        # character should be rendered with reverse video
        if (ord(char) == 160):
            clrs = image.getcolors()
            if (clrs[0][1] < 30):
                invert = True

        print_char(char, invert) # output char to console
        text += char

    #reset the console color    
    sys.stdout.write(RESET)
    return text

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
invert_enabled = not "--noinvert" in sys.argv
debug = "--debug" in sys.argv

# in debug mode create the dirs to store the punk & font blocks 
if debug:
    if not os.path.isdir(dir_font_blocks):
      os.makedirs(dir_font_blocks)
    if not os.path.isdir(dir_punk_blocks):  
        os.makedirs(dir_punk_blocks)

# create image bloack form the font 
create_font_blocks()           
# split the DOS punk image into blocks
create_punk_blocks(filename)  
# match the blocks (& output to console) 
punk_text = match_blocks().encode('utf-8')               

# save the output to a text file
text_filename = os.path.splitext(filename)[0]+".txt"
f = open(text_filename,"wb+")
f.write(punk_text)
f.close()

print("")  
if not platform.system() == 'Windows':
    print("") # need an extra line on windows
