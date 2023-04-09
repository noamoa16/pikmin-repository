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
        array: np.ndarray,
        *,
        background_color: np.ndarray | None = None
        ) -> bs4.Tag:
    table = soup.new_tag(
        'table', 
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

def create_count_table(soup: BeautifulSoup, counts: list[int], title: str) -> bs4.Tag:
    num_to_generate = sum(counts)
    array = np.full((4, len(counts) + 2), '', dtype = object)
    array[1, 0] = '件数／確率'
    array[2 : 4, 0] = '↓'
    array[0, len(counts) + 1] = '合計'
    for i, count in enumerate(counts):
        array[0, 1 + i] = i
        array[1 : 4, 1 + i] = get_count_prob_tuple(count, num_to_generate)
    array[1 : 4, len(counts) + 1] = get_count_prob_tuple(num_to_generate, num_to_generate)
    background_color = np.full((4, len(counts) + 2), '', dtype = object)
    background_color[0, :] = '#d0d0d0'
    background_color[1, :] = '#e0e0e0'
    table = create_table(soup, array, background_color = background_color)
    return table

def create_mitites_table(soup: BeautifulSoup, egg_probs: list[float]) -> bs4.Tag:
    array = np.full((3, len(egg_probs) + 1), '', dtype = object)
    array[0, 0] = 'タマゴムシのセット数'
    array[1, 0] = '確率'
    array[2, 0] = '↓'
    for mitites in range(len(egg_probs)):
        array[0, 1 + mitites] = mitites
        prob = sum(
            egg_probs[eggs] * calc_mitites_prob(eggs, mitites) 
            for eggs in range(mitites, len(egg_probs))
        )
        array[1 : 3, 1 + mitites] = get_prob_tuple(prob)
    background_color = np.full((3, len(egg_probs) + 1), '', dtype = object)
    background_color[0, :] = '#d0d0d0'
    background_color[1, 0] = '#e0e0e0'
    table = create_table(soup, array, background_color = background_color)
    return table

def get_percentage_str(probability: float) -> str:
    assert 0 <= probability <= 1
    if probability * 100 <= 1e-8 or 1 <= probability * 100:
        return f'{probability * 100:.4g}%'
    else:
        digits = -math.floor(math.log10(probability * 100))
        return f'{probability * 100:.{digits + 3}f}%'
 
def get_fraction_str(probability: float) -> str:
    assert 0 <= probability <= 1
    if probability == 0:
        return '1/∞'
    elif 1 <= 1 / probability <= 1e4 or 1e8 <= 1 / probability:
        return f'1/{1 / probability:.4g}'
    else:
        return f'1/{int(1 / probability)}'

def get_prob_tuple(probability: float):
    assert 0 <= probability <= 1
    return (get_percentage_str(probability), get_fraction_str(probability))
        
def get_count_prob_tuple(count: int, num_to_generate: int):
    assert 0 <= count <= num_to_generate
    return (count, get_percentage_str(count / num_to_generate), get_fraction_str(count / num_to_generate))
    
def calc_mitites_prob(num_eggs: int, mitites: int) -> float:
    mprob = 1 / 20
    return math.comb(num_eggs, mitites) * (mprob ** mitites) * ((1 - mprob) ** (num_eggs - mitites))

def parse_data(data_str: str):
    data: dict[str, str] = yaml.safe_load(data_str)
    stage_names = list(data.keys())
    soup = BeautifulSoup()
    for stage_index, stage_name in enumerate(stage_names):
        if stage_index != 0:
            for _ in range(2):
                soup.append(soup.new_tag('br'))

        trial: dict[str, Any] = data[stage_name]['trial']
        seed: int = trial['seed']
        num_to_generate: int = trial['num']
        result: dict[str, Any] = trial['result']
        bold = soup.new_tag('b')
        jp_stage_name = data[stage_name]['name']
        if '-' in stage_name:
            sublevel: int = int(stage_name.split('-')[1])
            jp_stage_name += f' (地下{sublevel}階)'
        bold.append(f'{jp_stage_name} (seed = {seed}, ..., {seed + num_to_generate - 1})')
        soup.append(bold)
        soup.append(soup.new_tag('p', style = 'margin:20px'))

        if stage_name == 'SR-6':
            soup.append('オオガネモチ出現率')
            array = np.full((4, 4), '', dtype = object)
            array[1, 0] = '件数／確率'
            array[2 : 4, 0] = '↓'
            array[0, 3] = '合計'
            array[0, 1 : 3] = ['あり', 'なし']
            array[1 : 4, 1] = get_count_prob_tuple(result['{onarashi: true}'], num_to_generate)
            array[1 : 4, 2] = get_count_prob_tuple(result['{onarashi: false}'], num_to_generate)
            array[1 : 4, 3] = get_count_prob_tuple(num_to_generate, num_to_generate)
            background_color = np.full((4, 4), '', dtype = object)
            background_color[0, :] = '#d0d0d0'
            background_color[1, :] = '#e0e0e0'
            table = create_table(soup, array, background_color = background_color)
            soup.append(table)
        elif stage_name == 'CH28':
            soup.append('タマゴ出現数')
            array = np.full((7, 8), '', dtype = object)
            array[0, 0] = 'タマゴ'
            array[1, 0] = 'エレキショイグモあり'
            array[[2, 3, 5, 6], 0] = '↓'
            array[4, 0] = 'エレキショイグモなし'
            array[0, 7] = '合計'
            for eggs in range(6):
                elec_true = result.get(f'{{eggs: {eggs}, elec: true}}', 0)
                elec_false = result.get(f'{{eggs: {eggs}, elec: false}}', 0)
                array[0, 1 + eggs] = eggs
                array[1 : 4, 1 + eggs] = get_count_prob_tuple(elec_true, num_to_generate)
                array[4 : 7, 1 + eggs] = get_count_prob_tuple(elec_false, num_to_generate)
            elec_true_sum = sum(v for k, v in result.items() if yaml.safe_load(k)['elec'])
            elec_false_sum = sum(v for k, v in result.items() if not yaml.safe_load(k)['elec'])
            array[1 : 4, 7] = get_count_prob_tuple(elec_true_sum, num_to_generate)
            array[4 : 7, 7] = get_count_prob_tuple(elec_false_sum, num_to_generate)
            background_color = np.full((7, 8), '', dtype = object)
            background_color[0, :] = '#d0d0d0'
            background_color[[1, 4], :] = '#e0e0e0'
            table = create_table(soup, array, background_color = background_color)
            soup.append(table)

            soup.append(soup.new_tag('p', style = 'margin:20px'))

            soup.append('タマゴムシの確率（キショイグモあり）')
            egg_probs = [result.get(f'{{eggs: {eggs}, elec: true}}', 0) / num_to_generate for eggs in range(6)]
            table = create_mitites_table(soup, egg_probs)
            soup.append(table)
        elif stage_name == 'CH29':
            soup.append('タマゴ出現数')
            max_eggs: int = max(yaml.safe_load(k)['eggs'] for k in result.keys())
            eggs = [result.get(f'{{eggs: {egg}}}', 0) for egg in range(max_eggs + 1)]
            table = create_count_table(soup, eggs, 'タマゴ')
            soup.append(table)

            soup.append(soup.new_tag('p', style = 'margin:20px'))
            soup.append('タマゴムシの確率')
            egg_probs = [result.get(f'{{eggs: {eggs}}}', 0) / num_to_generate for eggs in range(max_eggs + 1)]
            table = create_mitites_table(soup, egg_probs)
            soup.append(table)
        else:
            raise NotImplementedError

    return flask.Markup(soup.prettify())