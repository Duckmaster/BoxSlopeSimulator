import textwrap

def shiftLeft(obj):
    ## Takes base 2 integer and shifts it 1 to the left
    objL = list(format(obj, "032b"))
    objL.append(objL.pop(0))
    shifted = "".join(objL)
    return int(shifted,2)

def Hash(inString):
    bites = ""

    ## Initial series of buffers consisting of random 32 bit binary integers
    ## These are used towards the end of the function
    buffers = ['00000100110001100110011001000011',
               '10110011000000010001000001101001',
               '00111010101000011011010110111110',
               '00010001001000011111011101001011',
               '01101000111111001100001110001011']

    ## Converts each letter of the plain text into its 8 bit Unicode
    ## representation, then adding this to the 'bites' string
    for letter in inString:
        bites += format(ord(letter), "008b")

    ## Adds a 1 to the end of the string of bytes
    bites += "1"

    ## Calculates the amount of padding (number of 0s) to add to the end
    ## of 'bites' string to make its length up to 448 characters then adds them
    padding = 448 - len(bites)
    bites += "".join(["0" for i in range(padding)])

    ## Adds the length of the plain text, encoded into a 64 bit binary integer,
    ## to the end of the 'bites' string
    stringLen = format(len(inString), "064b")
    bites += stringLen

    ## Splits the 'bites' string into 16 "words" of length 32 each
    words = textwrap.wrap(bites, 32)

    ## Expands the 'words' array from 16 words to 80 words by XORing 4 words
    ## stored at the index indicated by 'indexes'. After each XOR the result
    ## is shifted one to left to improve cryptographic security
    indexes = [0, 2, 8, 13]
    while len(words) < 80:
        xor1 = (int(words[indexes[0]],2)) ^ (int(words[indexes[1]],2)) #Gives decimal
        xor1 = shiftLeft(xor1)
        xor2 = (int(words[indexes[2]],2)) ^ (int(words[indexes[3]],2))
        xor2 = shiftLeft(xor2)
        xor3 = (xor1 ^ xor2)
        xor3 = shiftLeft(xor3)
        words.append(format(xor3, "032b"))
        for i in range(len(indexes)):
            indexes[i] += 1

    ## Condenses the 80 words back down into 4 words by using a sequence of and, or
    ## and not operations with the buffers defined at the start and a word
    ## These operations are again used in conjuction with left shifts
    operations = ["and", "or", "not"]
    opCount = 0
    bufferCount = 0

    for word in words:
        if operations[opCount] == "and":
            buffers[bufferCount] = format(shiftLeft(int(word, 2)) &
                                          int(buffers[bufferCount], 2), "032b")
        elif operations[opCount] == "or":
            buffers[bufferCount] = format(shiftLeft(int(word, 2)) |
                                          int(buffers[bufferCount], 2), "032b")
        elif operations[opCount] == "not":
            temp1 = abs(~int(word, 2))
            temp2 = abs(~int(buffers[bufferCount], 2))
            buffers[bufferCount] = format(temp1 | temp2, "032b")

        buffers[bufferCount] = format(shiftLeft(int(buffers[bufferCount],2)), "032b") 

        opCount += 1
        bufferCount += 1
        if opCount > 2:
            opCount -= 3
        if bufferCount > 4:
            bufferCount -= 5

    ## Converts each buffer into an 8 bit hex string which is then added to a final
    ## 'hashBlock' which is then returned as the result of the hashing algorithm
    digest = ""
    for buffer in buffers:
        hashBlock = format(int(buffer, 2), "008x")
        digest += hashBlock

    return digest
