from bs4 import BeautifulSoup
import bs4
import flask
import numpy as np
import json
import yaml
from typing import Any
import math

def create_table(
        soup: BeautifulSoup, 
        stage_name: str, 
        array: np.ndarray,
        *,
        background_color: np.ndarray | None = None
        ) -> bs4.Tag:
    table = soup.new_tag(
        'table', 
        id = f'{stage_name}-table',
        border = '1',
        style = 'border-collapse:collapse;text-align:center;background-color:#f0f0f0;font-size:16',
    )

    rowspans = np.ones(array.shape)
    while True:
        changed = False
        for i in range(array.shape[0] - 1, 1, -1):
            for j in range(array.shape[1]):
                if array[i, j] == '↓':
                    array[i, j] = ''
                    rowspans[i - 1, j] += rowspans[i, j]
                    rowspans[i, j] = 0
                    changed = True
                    break
            if changed:
                break
        if not changed:
            break

    for i in range(array.shape[0]):
        table_row = soup.new_tag('tr')
        for j in range(array.shape[1]):
            if rowspans[i, j] == 0:
                continue
            td_style = 'padding:5'
            if background_color is not None and background_color[i, j] != '':
                td_style += f';background-color:{background_color[i, j]}'
            options = {
                'style': td_style,
            }
            if rowspans[i, j] != 1:
                options['rowspan'] = str(rowspans[i, j])
            table_data = soup.new_tag('td', **options)
            table_data.string = str(array[i, j])
            table_row.append(table_data)
        table.append(table_row)
    return table

def get_percentage_str(probability: float) -> str:
    assert 0 <= probability <= 1
    if 1 <= probability * 100 or probability == 0:
        return f'{probability * 100:.4g}%'
    else:
        digits = -math.floor(math.log10(probability * 100))
        return f'{probability * 100:.{digits + 3}f}%'
 
def get_fraction_str(probability: float) -> str:
    assert 0 <= probability <= 1
    if probability == 0:
        return '1/∞'
    elif 1 <= 1 / probability <= 1e4:
        return f'1/{1 / probability:.4g}'
    else:
        return f'1/{int(1 / probability)}'
    
def calc_mitites_prob(num_eggs: int, mitites: int) -> float:
    mprob = 1 / 20
    return math.comb(num_eggs, mitites) * (mprob ** mitites) * ((1 - mprob) ** (num_eggs - mitites))

def parse_data(data_str: str):
    data: dict[str, str] = json.loads(data_str)
    stage_names = list(data.keys())
    soup = BeautifulSoup()
    for stage_name in stage_names:
        trial: dict[str, Any] = data[stage_name]['trial']
        seed: int = trial['seed']
        num_to_generate: int = trial['num']
        bold = soup.new_tag('b')
        text = soup.new_tag('div')
        jp_stage_name = data[stage_name]['name']
        text.string = f'{jp_stage_name} (seed = {seed}, ..., {seed + num_to_generate - 1})'
        bold.append(text)
        soup.append(bold)
        soup.append(soup.new_tag('p', style = 'margin:20px'))

        if stage_name == 'CH28':
            text = soup.new_tag('div')
            text.string = 'タマゴ出現数'
            soup.append(text)
            array = np.full((7, 8), '', dtype = object)
            array[0, 0] = 'タマゴ'
            array[1, 0] = 'エレキショイグモあり'
            array[[2, 3, 5, 6], 0] = '↓'
            array[4, 0] = 'エレキショイグモなし'
            array[0, 7] = '合計'
            result: dict[str, Any] = trial['result']
            for eggs in range(6):
                elec_true = result.get(f'{{eggs: {eggs}, elec: true}}', 0)
                elec_false = result.get(f'{{eggs: {eggs}, elec: false}}', 0)
                array[0, 1 + eggs] = eggs
                array[1, 1 + eggs] = elec_true
                array[2, 1 + eggs] = get_percentage_str(elec_true / num_to_generate)
                array[3, 1 + eggs] = get_fraction_str(elec_true / num_to_generate)
                array[4, 1 + eggs] = elec_false
                array[5, 1 + eggs] = get_percentage_str(elec_false / num_to_generate)
                array[6, 1 + eggs] = get_fraction_str(elec_false / num_to_generate)
            elec_true_sum = sum(v for k, v in result.items() if yaml.safe_load(k)['elec'])
            elec_false_sum = sum(v for k, v in result.items() if not yaml.safe_load(k)['elec'])
            array[1, 7] = elec_true_sum
            array[2, 7] = get_percentage_str(elec_true_sum / num_to_generate)
            array[3, 7] = get_fraction_str(elec_true_sum / num_to_generate)
            array[4, 7] = elec_false_sum
            array[5, 7] = get_percentage_str(elec_false_sum / num_to_generate)
            array[6, 7] = get_fraction_str(elec_false_sum / num_to_generate)
            background_color = np.full((7, 8), '', dtype = object)
            background_color[0, :] = '#d0d0d0'
            background_color[[1, 4], :] = '#e0e0e0'
            table = create_table(soup, stage_name, array, background_color = background_color)
            soup.append(table)

            soup.append(soup.new_tag('p', style = 'margin:20px'))

            text = soup.new_tag('div')
            text.string = 'タマゴムシの確率（キショイグモあり）'
            soup.append(text)
            array = np.full((3, 7), '', dtype = object)
            array[0, 0] = 'タマゴムシのセット数'
            array[1, 0] = '確率'
            array[2, 0] = '↓'
            egg_probs = [result.get(f'{{eggs: {eggs}, elec: true}}', 0) / num_to_generate for eggs in range(6)]
            for mitites in range(6):
                array[0, 1 + mitites] = mitites
                prob = sum(
                    egg_probs[eggs] * calc_mitites_prob(eggs, mitites) 
                    for eggs in range(mitites, 6)
                )
                array[1, 1 + mitites] = get_percentage_str(prob)
                array[2, 1 + mitites] = get_fraction_str(prob)
            background_color = np.full((3, 7), '', dtype = object)
            background_color[0, :] = '#d0d0d0'
            background_color[1, 0] = '#e0e0e0'
            table = create_table(soup, stage_name, array, background_color = background_color)
            soup.append(table)
        else:
            raise NotImplementedError

    return flask.Markup(soup.prettify())