# Copyright (c) 2023 MikeCAT
# Licensed under The MIT License. https://opensource.org/license/mit/

import sys
import os

OOBMODE_ERROR = 0
OOBMODE_EXTEND = 1
OOBMODE_WRAP = 2

FLASH_NONE = 0
FLASH_LF = 1
FLASH_ALL = 2

sourceFile = None
arraySize = 30000
oobMode = OOBMODE_EXTEND
flashMode = FLASH_LF
eofChar = 0xff
wantHelp = False

i = 1
numArgs = len(sys.argv)
while i < numArgs:
    if sys.argv[i][0:2] == "--":
        if sys.argv[i] == "--array-size":
            i += 1
            arraySize = int(sys.argv[i])
        elif sys.argv[i] == "--oob-mode":
            i += 1
            if sys.argv[i] == "error": oobMode = OOBMODE_ERROR
            elif sys.argv[i] == "extend": oobMode = OOBMODE_EXTEND
            elif sys.argv[i] == "wrap": oobMode = OOBMODE_WRAP
            else: raise Exception("unknown out-of-bounds mode: " + sys.argv[i])
        elif sys.argv[1] == "--flash-mode":
            i += 1
            if sys.argv[i] == "none": flashMode = FLASH_NONE
            elif sys.argv[i] == "line": flashMode = FLASH_LF
            elif sys.argv[i] == "all": flashMode = FLASH_ALL
            else: raise Exception("unknown flash: " + sys.argv[i])
        elif sys.argv[i] == "--eof-char":
            i += 1
            eofChar = int(sys.argv[i]) & 0xff
        elif sys.argv[i] == "--eof-error":
            eofChar = None
        elif sys.argv[i] == "--help":
            wantHelp = True
        else:
            raise Exception("unknown option: " + sys.argv[i])
    else:
        if sourceFile is not None:
            raise Exception("only one source file can be specified")
        sourceFile = sys.argv[i]
    i += 1

if wantHelp or (sourceFile is None):
    sys.stderr.write("FizzBuzzF*ck\n")
    sys.stderr.write("\n")
    sys.stderr.write("Usage: python " + os.path.basename(__file__) + " [options] sourceFile\n")
    sys.stderr.write("\n")
    sys.stderr.write("options:\n")
    sys.stderr.write("  --array-size size : set number of elements of the array (default: 30000)\n")
    sys.stderr.write("  --oob-mode mode   : set what to do when the pointer goes outside the array\n")
    sys.stderr.write("                      error  : abort execution\n")
    sys.stderr.write("                      extend : extend the array (default)\n")
    sys.stderr.write("                      wrap   : move pointer to another side of the array\n")
    sys.stderr.write("  --flash-mode mode : set when to flash the standard output\n")
    sys.stderr.write("                      none   : no explicit flash is performed\n")
    sys.stderr.write("                      line   : flash after printing LF (default)\n")
    sys.stderr.write("                      all    : flash after printing every characters\n")
    sys.stderr.write("  --eof-char number : set what to read after reaching EOF (default: 255)\n")
    sys.stderr.write("  --eof-error       : abort execution when trying to read after reaching EOF\n")
    sys.stderr.write("  --help            : show this help\n")
    sys.exit(0)

with open(sourceFile, "rb") as f:
    source = f.read()

jumpDestinationMap = {}
jumpStack = []
for i, b in enumerate(source):
    c = chr(b)
    if c == "[":
        jumpStack.append(i)
    elif c == "]":
        if len(jumpStack) > 0:
            pairedPosition = jumpStack.pop()
            jumpDestinationMap[i] = pairedPosition
            jumpDestinationMap[pairedPosition] = i

theArray = [0 for _ in range(arraySize)]
theArrayNegative = []
arrayPointer = 0
programCounter = 0
programLength = len(source)

def S(i):
    if i % 15 == 0: return "FizzBuzz"
    if i % 3 == 0: return "Fizz"
    if i % 5 == 0: return "Buzz"
    return str(i)

fizzBuzzString = "".join([S(i) + "\n" for i in range(1, 101)])
for i, c in enumerate(fizzBuzzString[:len(theArray)]):
    theArray[i] = ord(c) & 0xff

def readArray(idx):
    if idx >= 0:
        return theArray[idx]
    else:
        return theArrayNegative[-idx - 1]

def writeArray(idx, value):
    if idx >= 0:
        theArray[idx] = value
    else:
        theArrayNegative[-idx - 1] = value

while programCounter < programLength:
    c = chr(source[programCounter])
    if c == ">":
        arrayPointer += 1
        if arrayPointer >= len(theArray):
            if oobMode == OOBMODE_EXTEND:
                theArray.append(0)
            elif oobMode == OOBMODE_WRAP:
                arrayPointer = 0
            else:
                sys.stderr.write("pointer overrun at " + str(programCounter) + "\n")
                sys.exit(1)
    elif c == "<":
        arrayPointer -= 1
        if arrayPointer < -len(theArrayNegative):
            if oobMode == OOBMODE_EXTEND:
                theArrayNegative.append(0)
            elif oobMode == OOBMODE_WRAP:
                arrayPointer = len(theArray) - 1
            else:
                sys.stderr.write("pointer underrun at " + str(programCounter) + "\n")
                sys.exit(1)
    elif c == "+":
        writeArray(arrayPointer, (readArray(arrayPointer) + 1) & 0xff)
    elif c == "-":
        writeArray(arrayPointer, (readArray(arrayPointer) - 1) & 0xff)
    elif c == ".":
        out = readArray(arrayPointer).to_bytes()
        sys.stdout.buffer.write(out)
        if flashMode == FLASH_ALL or (flashMode == FLASH_LF and out == b'\n'):
            sys.stdout.buffer.flush()
    elif c == ",":
        ch = sys.stdin.buffer.read(1)
        if len(ch) == 0:
            if eofChar is None:
                sys.stderr.write("read EOF at " + str(programCounter) + "\n")
                sys.exit(1)
            writeArray(arrayPointer, eofChar)
        else:
            writeArray(arrayPointer, ch[0])
    elif c == "[":
        if readArray(arrayPointer) == 0:
            if programCounter in jumpDestinationMap:
                programCounter = jumpDestinationMap[programCounter]
            else:
                sys.stderr.write("unmatched [ at " + str(programCounter) + "\n")
                sys.exit(1)
    elif c == "]":
        if readArray(arrayPointer) != 0:
            if programCounter in jumpDestinationMap:
                programCounter = jumpDestinationMap[programCounter]
            else:
                sys.stderr.write("unmatched ] at " + str(programCounter) + "\n")
                sys.exit(1)
    programCounter += 1

arrayPointerAtEnd = arrayPointer
while True:
    c = readArray(arrayPointer)
    if c == 0: break
    sys.stdout.buffer.write(c.to_bytes())
    arrayPointer += 1
    if arrayPointer >= len(theArray):
        if oobMode == OOBMODE_EXTEND:
            break
        elif oobMode == OOBMODE_WRAP:
            arrayPointer = 0
        else:
            sys.stderr.write("pointer overrun at final output\n")
            sys.exit(1)
    if arrayPointer == arrayPointerAtEnd: break
