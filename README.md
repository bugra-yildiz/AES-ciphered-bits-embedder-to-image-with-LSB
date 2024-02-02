# AES-ciphered-bits-embedder-to-image-with-LSB
Embedding 16bytes long AES ciphered data to an grey scale image with LSB.

This project aims to hide a ciphered data to an image and recover it back without making any noticeable changes to image.
To do this I use a custom function to find we the noise the highest (I don't know if it is done this way before).

## STEPS
1. Convert the image to an list.
2. Create a histogram with pixel value frequencies.
3. Calculate the variance of chunks and find starting point of the chunk with lowest variance. This is our pixel value.
4. Find the all pixel indices with the found pixel value.
5. Select the middle index in indice list.
6. Starting from the middle point create a list with length 128 and shape 16 by 8.
7. Cipher the data using AES. To create a key use the starting index we choosed and add random bytes to match the length.
8. Format the ciphered text to binary.
9. Embed the binary to image using the list we created which has the indices. Using the Least Significant Bit steganography.
10. To extract first extract the start index from key.
11. Recreate the list with indices that holds the embedded bits.
12. Using the reconstructed index list extract the bits. Reverse LSB.
13. Format the bit string and decipher the ciphered bits using key, tag, nonce.


## Sample Plain Image
![img](https://github.com/bugra-yildiz/AES-ciphered-bits-embedder-to-image-with-LSB/assets/42612286/4b3eaebd-34d0-41d4-951f-a547c8aa5aed)


## 16 Byte Data Embedded Image
![cipher_embedded_img](https://github.com/bugra-yildiz/AES-ciphered-bits-embedder-to-image-with-LSB/assets/42612286/4c95f90f-07bb-4a55-a39a-1312adacf46c)


## Highlighted Places of Embeding
