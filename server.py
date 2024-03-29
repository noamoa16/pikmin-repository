# -*- coding: utf-8 -*-
import json
import yaml
import flask
from markupsafe import Markup
from pathlib import Path
from typing import Any

from scripts import pikmin2_treasures, pikmin2_cave_surveys, pixel_arts

app = flask.Flask(__name__)

# 設定ファイルの読み込み
config = yaml.safe_load(open(Path(__file__).parent / 'config.yaml', encoding='utf-8'))
document_info = config['document_info']

def get_title(category: str, page_name: str) -> str:
    try:
        return document_info[category]['pages'][page_name]['title']
    except:
        return 'Unknown Title'

def get_favicon(category: str, page_name: str) -> str:
    try:
        return document_info[category]['pages'][page_name]['favicon']
    except:
        return ''
    
def load_data_file(data_file: Path) -> str:
    assert data_file.exists()
    return open(data_file, encoding = 'utf-8').read()

def get_data(category: str, page_name: str) -> dict[str, str | Markup]:

    # 必要なデータの取得
    try:
        data_files = document_info[category]['pages'][page_name]['data']
    except:
        data_files = []
    data: dict[str, str | Markup] = {}
    for data_file in data_files:
        path = Path(__file__).parent / f'data/{data_file}'
        data[data_file] = load_data_file(path)
    
    # データの解析
    if (category, page_name) == ('pikmin2', 'treasures'):
        data['pikmin2-treasures'] = \
            pikmin2_treasures.generate(data['pikmin2-treasures.yaml'])
    elif (category, page_name) == ('pikmin2', 'cave-surveys'):
        data['pikmin2-cave-surveys'] = \
            pikmin2_cave_surveys.generate(data['pikmin2-cave-surveys.yaml'])
    elif (category, page_name) == ('others', 'pixel-arts'):
        data['pixel-arts'] = pixel_arts.generate(
            Path(__file__).parent / 'static/images/pixel-arts'
        )
    
    return data

@app.route('/')
def index():
    return flask.render_template(
        'index.html', 
        title = config['site']['name'],
        favicon = config['site']['home_favicon'],
        document_info = document_info,
        full_title = config['site']['name'],
    )

@app.route('/<category>/<page_name>.html', methods=['GET'])
def page(category: str, page_name: str):
    try:
        title = get_title(category, page_name)
        context = {
            'title': title,
            'favicon': get_favicon(category, page_name), 
            'document_info': document_info,
            'full_title': title + ' - ' + document_info[category]['title'],
            'data': get_data(category, page_name)
        }
        return flask.render_template(
            f'/{category}/{page_name}.html', 
            **context,
        )
    except:
        return flask.render_template('404.html')

@app.errorhandler(404)
def error_404(error):
    return flask.render_template('404.html')

if __name__ == "__main__":
    app.run(debug = True)