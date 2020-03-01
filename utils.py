import qrcode
from qrcode.image.svg import SvgPathImage
import os
import jinja2
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from subprocess import Popen
from shutil import move


def create_wifi_qrcode(location, wifi_name, wifi_password, protocol='WPA',
                       **kwargs):
    """Creates a QR code in multiple file types given wifi network details

    Arguments:
        location {string} -- Place where network is located
        wifi_name {str} -- WiFi network name
        wifi_password {str} -- WiFi network password

    Keyword Arguments:
        protocol {str} -- WiFi network security protocol(default: {'WPA/WPA2'}
        )
    """
    string = f'WIFI:S:{wifi_name};T:{protocol};P:{wifi_password};;'

    factories = [
        {
            'method': 'svg',
            'factory': {
                'image_factory': SvgPathImage
            }
        },
        {
            'method': 'png',
            'factory': {}
        }
    ]

    kwargs.get('version', 1)
    kwargs.get('error_correction', qrcode.constants.ERROR_CORRECT_L)
    kwargs.get('box_size', 20)
    kwargs.get('border', 4)

    qr = qrcode.QRCode(**kwargs)

    qr.add_data(string)
    qr.make(fit=True)
    for factory in factories:
        method = factory['method']
        img = qr.make_image(**factory['factory'])
        if not os.path.exists(location):
            os.mkdir(location)
        img_path = os.path.join(location, wifi_name + '.' + method)
        img.save(img_path)
    qr_code = svg2rlg(os.path.join(location, wifi_name + '.svg'))
    img_path = os.path.join(location, wifi_name + '.pdf')
    renderPDF.drawToFile(qr_code, img_path)
    return


def render_tex(config):
    """Renders the template latex with our network specific data

    Arguments:
        config {dict} -- Dictionary of network values

    Returns:
        tuple -- Tuple of strings indicating the directory the rendered latex
        file is located as well as the latex file's direct path
    """

    latex_jinja_env = jinja2.Environment(
        block_start_string=r'\BLOCK{',
        block_end_string='}',
        variable_start_string=r'\VAR{',
        variable_end_string='}',
        comment_start_string=r'\#{',
        comment_end_string='}',
        line_statement_prefix='%%',
        line_comment_prefix='%#',
        trim_blocks=True,
        autoescape=False,
        loader=jinja2.FileSystemLoader(os.path.abspath('/'))
    )

    template = latex_jinja_env.get_template(
        os.path.realpath('template.tex')
    )

    qr_path = os.path.realpath(os.path.join(
        config['location'], config['wifi_name'] + '.pdf'))

    for key in config:
        config[key] = config[key].replace('_', r'\_')

    renderer_template = template.render(
        location=config['location'],
        wifi_name=config['wifi_name'],
        wifi_password=config['wifi_password'],
        qr_path=qr_path
    )

    tex_dir = os.path.realpath(os.path.join(config['location'], 'latex'))
    if not os.path.exists(tex_dir):
        os.makedirs(tex_dir)

    tex_path = os.path.realpath(os.path.join(tex_dir, 'welcome.tex'))
    with open(tex_path, 'w') as f:
        f.write(renderer_template)
    return tex_dir, tex_path


def create_pdf(tex_dir, tex_path):
    """Runs pdflatex to compile the rendered template and moves the resulting
    pdf to the parent directory

    Arguments:
        tex_dir {str} -- Path to the parent directory of the .tex file to be
        compiled
        tex_path {str} -- Direct path to the .tex file to be compiled
    """
    os.chdir(tex_dir)
    p = Popen(['pdflatex', tex_path])
    p.communicate()
    move('welcome.pdf', '../welcome.pdf')
