# -*- coding: utf-8 -*-

import operator
import argparse
from PIL import Image
from jinja2 import Template

def _green_screen_check(rgb, sensibility, reverse=False):
    """Checks if this pixel needs to be green"""
    if sensibility is None:
        return False
    op = operator.gt if reverse else operator.le
    for x in rgb:
        if not op(x, sensibility):
            return False
    return True


def gif2txt(filename, maxLen=80, output_file='out.html', with_color=False,
        green_screen_sensibility=None, reverse_green_screen=False):
    try:
        maxLen = int(maxLen)
    except:
        maxLen = 80

    chs = "MNHQ$OC?7>!:-;. "

    try:
        img = Image.open(filename)
    except IOError:
        exit("file not found: {}".format(filename))

    width, height = img.size
    rate = float(maxLen) / max(width, height)
    width = int(rate * width)
    height = int(rate * height)

    palette = img.getpalette()
    strings = []

    try:
        while 1:
            img.putpalette(palette)
            im = Image.new('RGB', img.size)
            im.paste(img)
            im = im.resize((width, height))
            string = ''
            for h in range(height):
                for w in range(width):
                    rgb = im.getpixel((w, h))
                    if _green_screen_check(rgb,
                                           green_screen_sensibility,
                                           reverse_green_screen):
                        rgb = (0, 255, 0)
                    if with_color:
                        string += "<span style=\"color:rgb%s;\">▇</span>" % str(rgb)
                    else:
                        string += chs[int(sum(rgb) / 3.0 / 256.0 * 16)]
                string += '\n'
            if isinstance(string, bytes):
                string = string.decode('utf8')
            strings.append(string)
            img.seek(img.tell() + 1)
    except EOFError:
        pass

    with open('template.jinja') as tpl_f:
        template = Template(tpl_f.read())
        html = template.render(strings=strings)
    with open(output_file, 'w') as out_f:
        if not isinstance(html, str):
            html = html.encode('utf8')
        out_f.write(html)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('filename',
                        help='Gif input file')
    parser.add_argument('-m', '--maxLen', type=int,
                        help='Max width of the output gif')
    parser.add_argument('-o', '--output',
                        help='Name of the output file')
    parser.add_argument('-c', '--color', action='store_true',
                        default=False,
                        help='With color')
    parser.add_argument('-g', '--green-screen-sensibility',
                        type=int, default=None,
                        help='convert black and grey into green, '
                             'sensibility between 1 and 255, suggested 128')
    parser.add_argument('-r', '--reverse-green-screen',
                        action='store_true', default=False,
                        help='white (instead of black) is converted into '
                             'green, you can still use -g option to set sensibility')
    args = parser.parse_args()

    if not args.maxLen:
        args.maxLen = 80
    if not args.output:
        args.output = 'out.html'
    if args.reverse_green_screen and not args.green_screen_sensibility:
        args.green_screen_sensibility = 128
    if args.green_screen_sensibility:
        args.color = True

    gif2txt(
        filename=args.filename,
        maxLen=args.maxLen,
        output_file=args.output,
        with_color=args.color,
        green_screen_sensibility=args.green_screen_sensibility,
        reverse_green_screen=args.reverse_green_screen,
    )

if __name__ == '__main__':
    main()
