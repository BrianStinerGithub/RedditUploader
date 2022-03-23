import imageio
import os, sys
import argparse
from PIL import Image
from config import *

def convertFile(inputpath, targetFormat = '.gif'):
    outputpath, ext = os.path.splitext(inputpath)
    outputpath += targetFormat
    print("converting\r\n\t{0}\r\nto\r\n\t{1}".format(inputpath, outputpath))

    if(inputpath.endswith(FILE_EXTENSIONS)):
        im = Image.open(inputpath).convert('RGB')
        im.save(outputpath, format=targetFormat[1:])
    elif(inputpath.endswith(VID_EXTENTIONS)):
        reader = imageio.get_reader(inputpath)
        fps = reader.get_meta_data()['fps']

        writer = imageio.get_writer(outputpath, fps=fps)
        for i,im in enumerate(reader):
            sys.stdout.write("\rframe {0}".format(i))
            sys.stdout.flush()
            writer.append_data(im)
    else:
        print("File not convertable. Image or video only.")

    print("\r\nFinalizing...")
    os.remove(inputpath)
    if(writer):
        writer.close()
    print("Done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Converts a video to a gif or mp4')
    parser.add_argument('-f', '--file', type=str, help='The path to the video to convert')
    parser.add_argument('-t', '--target', type=str, default='.gif', help='The target format to convert to')
    args = parser.parse_args()
    print(args)
    inputpath = args.file
    targetFormat = args.target
    convertFile(inputpath, targetFormat)