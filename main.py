import argparse
from utils import create_wifi_qrcode, render_tex, create_pdf
import json
import os


def run(config):
    """Creates a wifi qrcode given wifi network values and creates a welcome
    pdf

    Arguments:
        config {dict} -- Dictionary of wifi network values
    """
    create_wifi_qrcode(**config)
    tex_dir, tex_path = render_tex(config)
    create_pdf(tex_dir, tex_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Produce QR code'
    )
    parser.add_argument(
        'location',
        type=str, help='Select location'
    )
    parser.add_argument(
        'json',
        type=str,
        help='Select configuration json file',
        default='config.json'
    )
    args = parser.parse_args()
    with open(args.json) as f:
        wifi_networks = json.load(f)
    config = wifi_networks[args.location]
    run(config)
