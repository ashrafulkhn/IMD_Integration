# import struct

# def read_float_word_swap(buffer, index):
#     # Extract the two 16-bit words
#     word1 = buffer[index:index + 2]      # low word
#     word2 = buffer[index + 2:index + 4]  # high word

#     # Swap word order: [word2][word1]
#     swapped = word2 + word1

#     # Decode as big-endian float
#     return struct.unpack('>f', swapped)[0]


# data = b'\x00\x00\x41\x20'  # Example buffer
# value = read_float_word_swap(data, 0)

# print(value)

