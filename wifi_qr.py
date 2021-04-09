import qrcode
import argparse
import os
from qrcode.image.svg import SvgPathImage as svg


def wifi_string(ssid, password):
    return 'WIFI:T:WPA;S:{};P:{};;'.format(ssid, password)

def main():
    parser = argparse.ArgumentParser(description="Generate a QR code SVG for wifi sharing.")
    parser.add_argument("ssid", help="The network name")
    parser.add_argument("password", help="The network password")
    parser.add_argument("filename", help="The name to use for the image file")
    parser.add_argument("--type", "-t", help="The type of file to create", 
            choices=["png", "svg", "jpg"], default="png")
    parser.add_argument("--box-size", "-s", help="The size in mm of each box", type=float, default=2.5)
    parser.add_argument("--border", "-b", help="The size in boxes of the border", type=int, default=4)
    args = parser.parse_args()
    
    if os.path.exists(args.filename):
        resp = input(args.filename + " already exists! Overwrite? (y/N) ")
        if not resp.lower().startswith("y"):
            return
    f = open(args.filename, "wb")
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=args.box_size * 10,
        border=args.border,
    )
    #print(qrcode.constants.ERROR_CORRECT_L, qrcode.constants.ERROR_CORRECT_M, qrcode.constants.ERROR_CORRECT_Q, qrcode.constants.ERROR_CORRECT_H)
    
    wifi = wifi_string(args.ssid, args.password)
    qr.add_data(wifi)
    qr.make()
    print(len(wifi) * 8)
    if args.type == "png":
        img = qr.make_image()
        img.save(f, format="PNG")
    elif args.type == "jpg":
        img = qr.make_image()
        img.save(f, format="JPEG")
    elif args.type == "svg":
        img = qr.make_image(image_factory=svg)
        img.save(f)

if __name__ == "__main__":
    main()
