# %%
from PIL import Image
from collections import Counter
import math
import matplotlib.pyplot as plt
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes

# %%
# Image to list function
def imgToDec(thePath):
    img = Image.open(thePath)
    img = img.convert("L")
    data = list(img.getdata())
    return data

# %%
# Creating the list of pixel values from image
imgPath = "./img.jpg"

img = Image.open(imgPath)
print(img.format, img.size, img.mode)

imgList = imgToDec(imgPath)
print(len(imgList))

# %%
# Creating the list to store histogram values
imgHist = [0 for _ in range(256)]
print(len(imgHist))

# %%
# Creating the histogram
pixel_counter = Counter(imgList)
histogram_list = [pixel_counter.get(pixel_value, 0) for pixel_value in range(256)]

print(histogram_list)
print(sum(histogram_list))
print(len(histogram_list))


# %%
# Variance calculation function
def varienceCalculator(listOfValues):
    meanOfList = 0
    sumOfValues = 0
    sumOfDiff = 0

    for index, e in enumerate(listOfValues):
        sumOfValues += (index * e)
    meanOfList += sumOfValues/sum(listOfValues)

    for index, e in enumerate(listOfValues):
        sumOfDiff += (index - meanOfList)

    variance = (sumOfDiff**2)/sum(listOfValues)

    return variance

# %%
# Find variance of chunks with 32 length and store each chunks variance then return start value of the chunk with smallest variance.
def pixelValueFinder():
    partVarList = []

    for i in range(0, (len(histogram_list)-32)):
        chunk = histogram_list[i: i+32]
        varOfChunk = varienceCalculator(chunk)
        partVarList.append(varOfChunk)
    
    return partVarList.index(min(partVarList))

# %%
pixelValue = pixelValueFinder()
pixelValue

# %%
# Creating a list with index values which have the desired pixel value
def findPixelsToStore(pixelValue):
    wantedPixelIndexes = []
    for index, e in enumerate(imgList):
        if (e == pixelValue):
            wantedPixelIndexes.append(index)

    return wantedPixelIndexes   

# %%
pixelsWithAccValue = findPixelsToStore(pixelValue)
pixelsWithAccValue

# %%
# Choosing the middle value in the list as starting point for insertion of the data
midPixelIndex = pixelsWithAccValue[math.floor(len(pixelsWithAccValue)/2)]
midPixelIndex

# %%
# Creating a list with length 128 and 16 by 8 shape which has the indices for data insertion.
def pixelMatrixMaker(startIndex):
    allSelectedPixelIndexes = []
    tempStart = startIndex

    for i in range(8):
        for j in range(16):
            allSelectedPixelIndexes.append(tempStart + j)

        tempStart = tempStart + 512

    return allSelectedPixelIndexes


# %%
allSelectedPixelIndexes = pixelMatrixMaker(midPixelIndex)

# %%
# Ciphering the given 16 byte data with key that part start index part random bytes. Returning the ciphered text, key, nonce, tag values.
def cipherWithAES(plainData, index):
    dataPadding = b''
    paddingLimit = 16 - len(plainData)

    for _ in range(paddingLimit):
        dataPadding = dataPadding + b'0'

    data = dataPadding + plainData
    indexLen = len(index)
    keyPadding = 15 - len(index)
    key = indexLen.to_bytes(1, "big") + index + get_random_bytes(keyPadding)

    encipher = AES.new(key, AES.MODE_EAX)
    nonce = encipher.nonce
    cipheredText, tag = encipher.encrypt_and_digest(data)

    return cipheredText, tag, nonce, key

# %%
# Dummy data and formatted start index
plainText = b'112233445566'
strIndex = str(midPixelIndex)
startIndex = bytes(strIndex, "ascii")

# %%
cipherText, tag, nonce, key = cipherWithAES(plainText, startIndex)

# %%
# Formating the ciphered data to hex to binary string
binary_string = ''.join(format(byte, '08b') for byte in cipherText)

# %%
print(len(binary_string))
print(binary_string)

# %%
# Embedding the ciphered data to the image using LSB technique. Creating a image with ciphered data embeded.
def embedBitsLSB(sourceImgList, cipheredBinary):
    newImgList = sourceImgList[:]

    for i in range(len(cipheredBinary)):
        temp_cipher_bi_val = cipheredBinary[i]
        temp_cipher_bi_val = int(temp_cipher_bi_val, 2)
        print("Cipher Bit : ", temp_cipher_bi_val)

        temp_pixel_val = newImgList[allSelectedPixelIndexes[i]]
        print(temp_pixel_val)
        bi_temp_pixel_val = bin(temp_pixel_val)
        print(bi_temp_pixel_val)
        lsb_bi_pixel = bi_temp_pixel_val[-1]
        lsb_bi_pixel = int(lsb_bi_pixel, 2)
        print("LSB Bit : ", lsb_bi_pixel)
        temp_byte_holder = temp_cipher_bi_val
        print(temp_byte_holder)
        bi_temp_pixel_val = bi_temp_pixel_val[0: -1]
        bi_temp_pixel_val += str(temp_byte_holder)
        print(bi_temp_pixel_val)
        int_temp_pixel_val = int(bi_temp_pixel_val, 2)
        print("FINAL : ", int_temp_pixel_val)

        newImgList[allSelectedPixelIndexes[i]] = int_temp_pixel_val
        print("NEW PIXEL", newImgList[allSelectedPixelIndexes[i]])


    image3 = Image.new("L", (512, 512))
    image3.putdata(newImgList)
    image3.save("cipher_embedded_img.png", format="PNG")

# %%
embedBitsLSB(imgList, binary_string)

# %%
# Because we embeded the start index to the key we need to extract it. Here we extract the key. Key is 3 part first is how long the start index is second part is start index and third part is random bytes.
def indexExtractFromKey(key):
    print(key)
    key_binary_string = ''.join(format(byte, '08b') for byte in key)
    print(key_binary_string)
    index_len_in_key = key_binary_string[0:8]
    print(index_len_in_key)
    index_len_int = int(index_len_in_key, 2)
    print(index_len_int)
    start_index_bin = key_binary_string[8: ((index_len_int * 8) + 8)]
    print(len(start_index_bin))
    binary_chunks = [start_index_bin[i:i+8] for i in range(0, len(start_index_bin), 8)]
    ascii_characters = ''.join(chr(int(chunk, 2)) for chunk in binary_chunks)
    print(ascii_characters)

    extracted_start = int(ascii_characters)
    print("Extracted Start Index : ", extracted_start)

    return extracted_start

# %%
extractedStart = indexExtractFromKey(key)

# %%
# Here creating the list for indices that holds values that embeded cipher data. This the same with embeding.
all_start_pixels_extracted = pixelMatrixMaker(extractedStart)
all_start_pixels_extracted

# %%
# Extracting the last bit from the values that are given in the indices.
def extract_cipher(img_path):
    c_img_list = imgToDec(img_path)
    print(c_img_list)
    print(len(c_img_list))

    extract_img_list = c_img_list[:]

    cipher_bit_string = ""

    for i in range(len(all_start_pixels_extracted)):
        ciphered_pixel = bin(extract_img_list[all_start_pixels_extracted[i]])
        print(ciphered_pixel)
        cipher_bit = ciphered_pixel[-1]
        print(cipher_bit)
        cipher_bit_string += cipher_bit
        

    print(cipher_bit_string)

    return cipher_bit_string

# %%
ciphered_img_path = "./cipher_embedded_img.png"

cipher_bit_string = extract_cipher(ciphered_img_path)

# %%
# Here decipher the ciphered data with key, tag, nonce.
def decipher_AES(key, tag, nonce, cipher_bits):
    new_byte_string = int(cipher_bits, 2).to_bytes((len(cipher_bits)) // 8, 'big')
    decipher = AES.new(key, AES.MODE_EAX, nonce)
    plainText = decipher.decrypt_and_verify(new_byte_string, tag)

    return plainText

# %%
decipher_AES(key, tag, nonce, cipher_bit_string)


