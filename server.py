# -*- coding: utf-8 -*-
import yaml
import flask
from pathlib import Path

app = flask.Flask(__name__)

# 設定ファイルの読み込み
config = yaml.safe_load(open(Path(__file__).parent / 'config.yaml', encoding='utf-8'))
document_info = config['document_info']

def get_title(category: str, page_name: str) -> str:
    try:
        return document_info[category]['structure'][page_name]['title']
    except:
        return 'Unknown Title'

def get_favicon(category: str, page_name: str) -> str:
    try:
        return document_info[category]['structure'][page_name]['favicon']
    except:
        return ''

@app.route('/')
def index():
    return flask.render_template(
        'index.html', 
        title = config['site']['name'],
        favicon = config['site']['home_favicon'],
        document_info = document_info,
    )

@app.route('/<category>/<page_name>.html', methods=['GET'])
def page(category: str, page_name: str):
    try:
        return flask.render_template(
            f'/{category}/{page_name}.html', 
            title = get_title(category, page_name), 
            favicon = get_favicon(category, page_name), 
            document_info = document_info,
        )
    except:
        return flask.render_template('404.html')

@app.errorhandler(404)
def error_404(error):
    return flask.render_template('404.html')

if __name__ == "__main__":
    app.run(debug = True)