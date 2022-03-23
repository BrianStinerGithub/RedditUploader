import imageio
import os, sys
import argparse
from PIL import Image
from config import *

def convertFile(inputpath, targetFormat = '.gif'):
    if not os.path.exists(inputpath):
        print('File does not exist')
    if os.path.isdir(inputpath):
        for file in os.listdir(inputpath):
            if file.endswith(FILE_EXTENSIONS) or file.endswith(VID_EXTENTIONS):
                convertFile(file, targetFormat)
    else:
        outputpath, ext = os.path.splitext(inputpath)
        outputpath += targetFormat
        print("converting\r\n\t{0}\r\nto\r\n\t{1}".format(inputpath, outputpath))

        writer = None
        if(ext in FILE_EXTENSIONS):
            im = Image.open(inputpath)
            im.save(outputpath, format=targetFormat[1:])
        elif(ext in VID_EXTENTIONS):
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
        if(writer):
            writer.close()
        try:os.remove(inputpath)
        except:print(f'{inputpath} not deleted\n')
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