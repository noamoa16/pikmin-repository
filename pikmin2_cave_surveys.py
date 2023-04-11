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

def create_count_table(
        soup: BeautifulSoup, 
        counts: list[int], 
        *, 
        labels: list[str] | None = None,
        ) -> bs4.Tag:
    
    assert labels is None or len(counts) == len(labels)
    if labels is None:
        labels = [str(i) for i in range(len(counts))]

    num_to_generate = sum(counts)
    left_skip = 0
    for i in range(len(counts)):
        if counts[i] == 0:
            left_skip += 1
        else:
            break
    array = np.full((4, len(counts[left_skip:]) + 2), '', dtype = object)
    array[1, 0] = '件数／確率'
    array[2 : 4, 0] = '↓'
    array[0, len(counts[left_skip:]) + 1] = '合計'
    for i, count in enumerate(counts[left_skip:]):
        array[0, 1 + i] = labels[i + left_skip]
        array[1 : 4, 1 + i] = get_count_prob_tuple(count, num_to_generate)
    array[1 : 4, len(counts[left_skip:]) + 1] = \
        get_count_prob_tuple(num_to_generate, num_to_generate)
    background_color = np.full((4, len(counts[left_skip:]) + 2), '', dtype = object)
    background_color[0, :] = '#d0d0d0'
    background_color[1, :] = '#e0e0e0'
    table = create_table(soup, array, background_color = background_color)
    return table

def create_true_false_table(soup: BeautifulSoup, counts: list[int]) -> bs4.Tag:
    return create_count_table(soup, counts, labels = ['あり', 'なし'])

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
    if probability * 100 <= 1e-6 or 1 <= probability * 100:
        return f'{probability * 100:.4g}%'
    else:
        digits = -math.floor(math.log10(probability * 100))
        return f'{probability * 100:.{digits + 3}f}%'
 
def get_fraction_str(probability: float) -> str:
    assert 0 <= probability <= 1
    if probability == 0:
        return '1/∞'
    elif 1 <= 1 / probability <= 1e4 or 1e6 <= 1 / probability:
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
        bold.append(f'{jp_stage_name} (seed = 0x{seed:08X}, ..., 0x{seed + num_to_generate - 1:08X})')
        soup.append(bold)
        soup.append(soup.new_tag('p', style = 'margin:20px'))

        if stage_name == 'FC-7':
            soup.append('オオガネモチ出現率')
            counts = [result['{oogane: true}'], result['{oogane: false}']]
            table = create_true_false_table(soup, counts)
            soup.append(table)
        elif stage_name == 'SR-6':
            soup.append('オナラシ出現率')
            counts = [result['{onarashi: true}'], result['{onarashi: false}']]
            table = create_true_false_table(soup, counts)
            soup.append(table)
        elif stage_name == 'CH2-2':
            soup.append('地形とタマゴムシ')
            array = np.full((13, 4), '', dtype = object)
            array[0, 0] = '地形＼タマゴムシ'
            array[[1, 4, 7, 10], 0] = ('丸部屋', '丸部屋 (S字)', '三日月', '合計')
            array[[2, 3, 5, 6, 8, 9, 11, 12], 0] = '↓'
            for mitites in [1, 2]:
                array[0, mitites] = mitites
                array[1 : 4, mitites] = get_count_prob_tuple(result[f'{{room: circle, mitites: {mitites}}}'], num_to_generate)
                array[4 : 7, mitites] = get_count_prob_tuple(result[f'{{room: circle_s, mitites: {mitites}}}'], num_to_generate)
                array[7 : 10, mitites] = get_count_prob_tuple(result[f'{{room: crescent, mitites: {mitites}}}'], num_to_generate)
                array[10 : 13, mitites] = get_count_prob_tuple(sum(result[f'{{room: {room}, mitites: {mitites}}}'] for room in ['circle', 'circle_s', 'crescent']), num_to_generate)
            array[0, 3] = '合計'
            array[1 : 4, 3] = get_count_prob_tuple(sum(result[f'{{room: circle, mitites: {mitites}}}'] for mitites in [1, 2]), num_to_generate)
            array[4 : 7, 3] = get_count_prob_tuple(sum(result[f'{{room: circle_s, mitites: {mitites}}}'] for mitites in [1, 2]), num_to_generate)
            array[7 : 10, 3] = get_count_prob_tuple(sum(result[f'{{room: crescent, mitites: {mitites}}}'] for mitites in [1, 2]), num_to_generate)
            array[10 : 13, 3] = get_count_prob_tuple(num_to_generate, num_to_generate)
            background_color = np.full((13, 4), '', dtype = object)
            background_color[0, :] = '#d0d0d0'
            background_color[[1, 4, 7, 10], :] = '#e0e0e0'
            table = create_table(soup, array, background_color = background_color)
            soup.append(table)

            soup.append(soup.new_tag('p', style = 'margin:20px'))
            
            soup.append('タマゴムシの確率 (B1とB2の合計)')
            b1_mitites_probs = [calc_mitites_prob(2, mitites) for mitites in range(3)]
            b2_mitites_probs = [
                sum(result[f'{{room: {room}, mitites: {mitites}}}'] 
                    for room in ['circle', 'circle_s', 'crescent']) / num_to_generate 
                    for mitites in [1, 2]]
            mitites_probs = [0] * (len(b1_mitites_probs) + len(b2_mitites_probs) - 1)
            for i in range(len(b1_mitites_probs)):
                for j in range(len(b2_mitites_probs)):
                    mitites_probs[i + j] += b1_mitites_probs[i] * b2_mitites_probs[j] 
            array = np.full((3, 5), '', dtype = object)
            array[0, 0] = 'タマゴムシのセット数'
            array[1, 0] = '確率'
            array[2, 0] = '↓'
            for mitites, mities_prob in enumerate(mitites_probs):
                array[0, mitites + 1] = mitites + 1
                array[1 : 3, mitites + 1] = get_prob_tuple(mities_prob)
            background_color = np.full((3, 5), '', dtype = object)
            background_color[0, :] = '#d0d0d0'
            background_color[1, 0] = '#e0e0e0'
            table = create_table(soup, array, background_color = background_color)
            soup.append(table)
        elif stage_name == 'CH8':
            soup.append('コチャ出現数')
            max_kochas: int = max(yaml.safe_load(k)['kocha'] for k in result.keys())
            kochas = [result.get(f'{{kocha: {kocha}}}', 0) for kocha in range(max_kochas + 1)]
            table = create_count_table(soup, kochas)
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
            table = create_count_table(soup, eggs)
            soup.append(table)

            soup.append(soup.new_tag('p', style = 'margin:20px'))

            soup.append('タマゴムシの確率')
            egg_probs = [result.get(f'{{eggs: {eggs}}}', 0) / num_to_generate for eggs in range(max_eggs + 1)]
            table = create_mitites_table(soup, egg_probs)
            soup.append(table)
        else:
            raise NotImplementedError

    return flask.Markup(soup.prettify())