import subprocess
import time

# digitSizes = [100, 1000, 10000, 100000, 500000, 1000000, 5000000, 10000000]
digitSizes = [100, 1000, 10000, 100000, 500000]


# generate random digits and write to file
def generateRandomDigitsFiles(size):
    subprocess.call(['python', 'randomDigitGen.py',
                    './src/input.txt', str(size)])
    print('\nGenerated random digits of size ' + str(size))


def runCompress(size):  # run compress.py from command line and find the execution time
    start = time.time()
    subprocess.call(['python', './src/compress.py',
                    './src/input.txt', './src/compressed.bin'])
    end = time.time()
    print('For {} digits compression time: {} seconds'.format(size, end - start))


def runDecompress(size):  # run decompress.py from command line and find the execution time
    start = time.time()
    subprocess.call(['python', './src/decompress.py',
                    './src/compressed.bin', './src/output.txt'])
    end = time.time()
    print('For {} digits decompression time: {} seconds'.format(
        size, end - start))


def main():
    for size in digitSizes:
        generateRandomDigitsFiles(size)
        runCompress(size)
        runDecompress(size)


if __name__ == "__main__":
    main()
