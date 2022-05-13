import simplification
import instructions

import argparse


def main():
    parser = argparse.ArgumentParser(description='Sketch simplification demo.')
    parser.add_argument('--img', type=str, required=True, help='Input image file.')
    parser.add_argument('--out', type=str, required=True, help='File to output.')
    opt = parser.parse_args()

    simplified_image_file = 'simpklified_image.svg'
    simplification.simplify_image(opt.img, simplified_image_file)
    instructions.draw_instructions(simplified_image_file, opt.out)


if __name__ == '__main__':
    main()
