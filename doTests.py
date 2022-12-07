import subprocess
import time
import os
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import math

# digitSizes = [1000, 10000, 100000, 500000, 1000000, 5000000]
digitSizes = [10000, 50000, 75000, 100000, 250000, 500000, 750000]
fileSizesInKB = []
compressedFileSizesInKB = []
decompressionTimes = []
compressionTimes = []


# generate random digits and write to file
def generateRandomDigitsFiles(size):
    subprocess.call(['python', 'randomDigitGen.py',
                    './src/input.txt', str(size)])
    print('\nGenerated random digits of size ' + str(size))
    fileSizesInKB.append(round(os.path.getsize('./src/input.txt') / 1024, 1))


def runCompress(size):  # run compress.py from command line and find the execution time
    start = time.time()
    subprocess.call(['python', './src/compress.py',
                    './src/input.txt', './src/compressed.bin'])
    end = time.time()
    compressionTimes.append(round(end - start, 2))
    print('For {} digits compression time: {} seconds'.format(size, end - start))
    compressedFileSizesInKB.append(round(
        os.path.getsize('./src/compressed.bin') / 1024, 1))


def runDecompress(size):  # run decompress.py from command line and find the execution time
    start = time.time()
    subprocess.call(['python', './src/decompress.py',
                    './src/compressed.bin', './src/output.txt'])
    end = time.time()
    decompressionTimes.append(round(end - start, 2))
    print('For {} digits decompression time: {} seconds'.format(
        size, end - start))


def plotLineGraph(x, y, xTitle, yTitle, title):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    plt.plot(range(len(x)), y, 'bo')  # Plotting data
    plt.xticks(range(len(x)), x)  # Redefining x-axis labels

    for i, v in enumerate(y):
        ax.annotate(str(v), xy=(i, v), xytext=(-7, 7),
                    textcoords='offset points')
    plt.xlabel(xTitle)
    plt.ylabel(yTitle)
    plt.title(title)
    plt.show()


def plotComparisonBarGraph(x, y1, y2, xTitle, yTitle, bar1title, bar2title, title):
    X = np.arange(len(x))
    width = 0.35

    fig, ax = plt.subplots()
    rects1 = ax.bar(X - width/2, y1, width, label=bar1title)
    rects2 = ax.bar(X + width/2, y2, width, label=bar2title)

    ax.set_ylabel(yTitle)
    ax.set_xlabel(xTitle)
    ax.set_title(title)
    ax.set_xticks(X, x)
    ax.legend()

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)

    fig.tight_layout()

    plt.show()


def main():
    for size in digitSizes:
        generateRandomDigitsFiles(size)
        runCompress(size)
        runDecompress(size)

    plotLineGraph(fileSizesInKB, compressionTimes, 'Original File Size (KB)',
                  'Compression Time (seconds)', 'File Size vs Compression')
    plotLineGraph(fileSizesInKB, decompressionTimes, 'Original File Size (KB)',
                  'Decompression Time (seconds)', 'File Size vs Decompression')
    plotLineGraph(compressionTimes, decompressionTimes, 'Compression Time (seconds)',
                  'Decompression Time(seconds)', 'Compression vs Decompression')
    plotLineGraph(digitSizes, compressionTimes, 'Number of Digits',
                  'Compression Time (seconds)', 'Numbers of Digits vs Compression')

    plotComparisonBarGraph(digitSizes, fileSizesInKB, compressedFileSizesInKB, 'Number of Digits',
                           'File Size (KB)', 'Original File Size (KB)', 'Compressed File Size (KB)', 'File Size Comparison')

    plotComparisonBarGraph(digitSizes, compressionTimes, decompressionTimes, 'Number of Digits',
                           'Time (Seconds)', 'Compression Times (Seconds)', 'Decompression Times (Seconds)', 'Time Comparison')

    # uncomment the following lines to delete the files generated
    # os.remove("./src/compressed.bin")
    # os.remove("./src/output.txt")
    # os.remove("./src/input.txt")


if __name__ == "__main__":
    main()
