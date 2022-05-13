import torch
from torchvision import transforms
from torchvision.utils import save_image
import sketch_gan
import subprocess

from PIL import Image
import argparse

parser = argparse.ArgumentParser(description='Sketch simplification demo.')
parser.add_argument('--model', type=str, default='model_gan.t7', help='Model to use.')
parser.add_argument('--img',   type=str, default='test.png',     help='Input image file.')
parser.add_argument('--out',   type=str, default='out.png',      help='File to output.')
opt = parser.parse_args()

def remove_noises(input_filepath, output_filepath):
    use_cuda = torch.cuda.device_count() > 0

    model = sketch_gan.sketch_gan
    model.load_state_dict(torch.load('sketch_gan.pth'))
    model.eval()

    immean = 0.966411457764
    imstd = 0.0858381272737

    data  = Image.open(input_filepath).convert('L')
    w, h  = data.size[0], data.size[1]
    pw    = 8-(w%8) if w%8!=0 else 0
    ph    = 8-(h%8) if h%8!=0 else 0
    data  = ((transforms.ToTensor()(data) - immean) / imstd).unsqueeze(0)
    if pw != 0 or ph != 0:
        data = torch.nn.ReplicationPad2d( (0,pw,0,ph) )( data ).data

    if use_cuda:
        pred = model.cuda().forward( data.cuda() ).float()
    else:
        pred = model.forward( data )
    save_image( pred[0], output_filepath )


def simplify_image(input_file, output_file):
    without_noises_file = 'without_noises.png'
    remove_noises(input_file, without_noises_file)
    cmd = 'convert {} bmp:- | mkbitmap - -t 0.3 -o - | potrace --svg -t 2 -o - > {}'.format(without_noises_file, output_file)
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = process.communicate()[0]

