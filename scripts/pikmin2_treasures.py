import yaml
import flask
from bs4 import BeautifulSoup
from markupsafe import Markup

def generate(data_str: str):
    KEY_TO_COLUMNS = {
        'imagePath': '画像',
        'jpId': 'No. (日本版)', 
        'usId': 'No. (米国版)',
        'euId': 'No. (欧州版)',
        'jpName': '名前(日本語)', 
        'enName': '名前(英語)', 
        'weight': '重さ', 
        'maxCarriers': '最大運搬数', 
        'value': '価値', 
        'location': '場所', 
        'sublevel': '階層',
        'jpSeries': 'シリーズ(日本語)', 
        'enSeries': 'シリーズ(英語)', 
        'jpRealLifeItem': '見た目(日本語)',
        'enRealLifeItem': '見た目(英語)',
    }
    data: list[dict[str, int | str]] = yaml.safe_load(data_str)

    soup = BeautifulSoup()
    table = soup.new_tag(
        'table', 
        id = 'treasure-table', 
        border = "1", 
        style = "border-collapse:collapse;text-align:center;font-size:10px",
    )

    thead = soup.new_tag('thead')
    tr = soup.new_tag('tr')
    for column in KEY_TO_COLUMNS.values():
        th = soup.new_tag('th', style = "padding:3")
        th.append(column)
        tr.append(th)
    thead.append(tr)
    table.append(thead)

    tbody = soup.new_tag('tbody')
    for treasure in data:
        tr = soup.new_tag('tr')
        for key in KEY_TO_COLUMNS.keys():
            td = soup.new_tag('td', style = "padding:3")
            if key == 'imagePath':
                image_path = treasure[key]
                img = soup.new_tag(
                    'img',
                    decoding = "async",
                    src = '..' + flask.url_for('static', filename = f'images/treasures/{image_path}'),
                    alt = image_path,
                    title = image_path,
                )
                td.append(img) 
            else:
                if key in treasure:
                    value = treasure[key]
                else:
                    value = '---'
                td.append(str(value))
            tr.append(td)
        tbody.append(tr)
    table.append(tbody)

    soup.append(table)
    return Markup(soup.prettify())
