import random
import sys
# generate random digits and write to file
# run like: python randomDigitGen.py <inputFile> <size>


def fillFile(size, fileName):
    strA = ''
    for i in range(size):
        strA = strA + str(random.randint(0, 10))  # type: ignore
    file = open(fileName, "w")
    file.write(strA)


def main(args):
    # read command line arguments and call fillFile
    fileName, size = args
    fillFile(int(size), fileName)


if __name__ == "__main__":
    main(sys.argv[1:])
