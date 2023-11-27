from bs4 import BeautifulSoup
from markupsafe import Markup
import flask
from pathlib import Path

def generate(image_dir_path: Path):
    soup = BeautifulSoup()
    image_paths = sorted([p for p in image_dir_path.iterdir() if p.is_file()])
    for image_path in image_paths:
        name, size_str = image_path.stem.split('_')
        width = int(size_str.split('x')[0])
        height = int(size_str.split('x')[1])
        img_src = '..' + flask.url_for('static', filename = f'images/pixel-arts/{image_path.stem}.png')
        a_tag = soup.new_tag(
            'a', 
            href = img_src, 
            style = 'text-decoration: none;',
            target = '_blank',
        )
        image_tag = soup.new_tag(
            'img',
            src = img_src, 
            width = width,
            height = height,
            alt = name,
            decoding = 'async',
        )
        a_tag.append(image_tag)
        soup.append(a_tag)

    return Markup(soup.prettify())

if __name__ == '__main__':
    markup = generate(Path(__file__).parent / 'static/images/pixel-arts')
    print(markup)