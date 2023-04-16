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
    '''
    `array`を元に表を作成
    '''
    table_parent = soup.new_tag('div', style = 'overflow:auto')
    table = soup.new_tag(
        'table', 
        border = '1',
        style = 'border-collapse:collapse;text-align:center;background-color:#f0f0f0;font-size:16;white-space:nowrap',
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

    table_parent.append(table)
    return table_parent

def create_count_table(
        soup: BeautifulSoup, 
        counts: list[int], 
        *, 
        labels: list[str] | None = None,
        ) -> bs4.Tag:
    '''
    `counts`を横に並べた表を作成
    '''

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
    '''
    ありかなしかの2択を表す表を作成
    '''
    return create_count_table(soup, counts, labels = ['あり', 'なし'])

def create_mitites_table(
        soup: BeautifulSoup, 
        *, 
        egg_probs: list[float] | None = None,
        mitites_probs: list[float] | None = None,
        ) -> bs4.Tag:
    '''
    タマゴの確率分布`egg_probs`またはタマゴムシの確率`mitites_probs`を元に表を作成
    '''
    assert (egg_probs is not None and mitites_probs is None) or \
        (egg_probs is None and mitites_probs is not None)
    if egg_probs is not None:
        mitites_probs = []
        for mitites in range(len(egg_probs)):
            mitites_probs.append(sum(
                egg_probs[eggs] * calc_mitites_prob(eggs, mitites) 
                for eggs in range(mitites, len(egg_probs))
            ))

    left_skip = 0
    for i in range(len(mitites_probs)):
        if mitites_probs[i] == 0:
            left_skip += 1
        else:
            break

    array = np.full((3, len(mitites_probs[left_skip:]) + 1), '', dtype = object)
    array[0, 0] = 'タマゴムシのセット数'
    array[1, 0] = '確率'
    array[2, 0] = '↓'
    for mitites, mitites_prob in enumerate(mitites_probs[left_skip:]):
        array[0, 1 + mitites] = mitites + left_skip
        array[1 : 3, 1 + mitites] = get_prob_tuple(mitites_prob)
    background_color = np.full((3, len(mitites_probs) + 1), '', dtype = object)
    background_color[0, :] = '#d0d0d0'
    background_color[1, 0] = '#e0e0e0'
    table = create_table(soup, array, background_color = background_color)
    return table

def get_percentage_str(probability: float) -> str:
    assert 0 <= probability <= 1, probability
    if probability * 100 <= 1e-6 or 1 <= probability * 100:
        return f'{probability * 100:.4g}%'
    else:
        digits = -math.floor(math.log10(probability * 100))
        return f'{probability * 100:.{digits + 3}f}%'
 
def get_fraction_str(probability: float) -> str:
    assert 0 <= probability <= 1, probability
    if probability == 0:
        return '1/∞'
    elif 1 <= 1 / probability <= 1e4 or 1e6 <= 1 / probability:
        return f'1/{1 / probability:.4g}'
    else:
        return f'1/{int(1 / probability)}'

def get_prob_tuple(probability: float):
    assert 0 <= probability <= 1, probability
    return (get_percentage_str(probability), get_fraction_str(probability))
        
def get_count_prob_tuple(count: int, num_to_generate: int):
    assert 0 <= count <= num_to_generate
    return (count, get_percentage_str(count / num_to_generate), get_fraction_str(count / num_to_generate))
    
def calc_mitites_prob(num_eggs: int, mitites: int) -> float:
    if num_eggs < mitites:
        return 0.
    else:
        mprob = 1 / 20
        return math.comb(num_eggs, mitites) * (mprob ** mitites) * ((1 - mprob) ** (num_eggs - mitites))

def parse_data(data_str: str):
    data: dict[str, str] = yaml.safe_load(data_str)
    stage_names = list(data.keys())
    soup = BeautifulSoup()

    # 目次作成
    table_of_contents = soup.new_tag('ul', **{'class': 'table-of-contents'})
    for stage_name in stage_names:
        jp_stage_name = data[stage_name]['name']
        if '-' in stage_name:
            sublevel: int = int(stage_name.split('-')[1])
            jp_stage_name += f' (地下{sublevel}階)'
        list_item = soup.new_tag('li')
        anchor = soup.new_tag('a', href = f'#tables-{stage_name}')
        anchor.string = jp_stage_name
        list_item.append(anchor)
        table_of_contents.append(list_item)
    soup.append(table_of_contents)

    for stage_index, stage_name in enumerate(stage_names):  
        if stage_index != 0:
            soup.append(soup.new_tag('hr'))
        tables = soup.new_tag('div', id = f'tables-{stage_name}')
        tables.append(soup.new_tag('br'))

        trial: dict[str, Any] = data[stage_name]['trial']
        seed: int = trial['seed']
        num_to_generate: int = trial['num']
        result: dict[str, Any] = trial['result']
        bold = soup.new_tag('b')
        jp_stage_name = data[stage_name]['name']
        if '-' in stage_name:
            sublevel: int = int(stage_name.split('-')[1])
            jp_stage_name += f' (地下{sublevel}階)'
        bold.string = jp_stage_name
        tables.append(bold)
        tables.append(soup.new_tag('br'))
        tables.append(soup.new_tag('span', style = 'margin-right: 1em'))
        seed_text = f'seed = 0x{seed:08X}, ..., 0x{seed + num_to_generate - 1:08X}'
        if num_to_generate == 0x80000000:
            seed_text += ' (全探索)'
        elif 0x80000000 % num_to_generate == 0 and 0x80000000 // num_to_generate <= 16:
            seed_text += f' (1/{0x80000000 // num_to_generate}探索)'
        tables.append(seed_text)
        tables.append(soup.new_tag('p', style = 'margin:20px'))

        if stage_name in ['FC-7', 'SC-4']:
            tables.append('オオガネモチ出現率')
            counts = [result['{oogane: true}'], result['{oogane: false}']]
            table = create_true_false_table(soup, counts)
            tables.append(table)
        elif stage_name == 'SCx-7':
            tables.append('固定タマコキン出現率')
            counts = [result['{fixedTamakokin: true}'], result['{fixedTamakokin: false}']]
            table = create_true_false_table(soup, counts)
            tables.append(table)
        elif stage_name == 'GK-5':
            tables.append('ムラサキポンガシ出現率')
            counts = [result['{murasakipom: true}'], result['{murasakipom: false}']]
            table = create_true_false_table(soup, counts)
            tables.append(table)
        elif stage_name == 'SR-6':
            tables.append('オナラシ出現率')
            counts = [result['{onarashi: true}'], result['{onarashi: false}']]
            table = create_true_false_table(soup, counts)
            tables.append(table)
        elif stage_name == 'SR-7':
            tables.append('ケメクジ出現率')
            counts = [result['{kemekuji: true}'], result['{kemekuji: false}']]
            table = create_true_false_table(soup, counts)
            tables.append(table)

            tables.append(soup.new_tag('p', style = 'margin:20px'))

            no_kemekuji_seed = data[stage_name]['seeds']['no_kemekuji']
            tables.append(f'ケメクジのいない地形 (シード値 = 0x{no_kemekuji_seed:08X})')
            tables.append(soup.new_tag('br'))
            img = soup.new_tag('img', src = flask.url_for('static', filename = f'images/CaveGen/{stage_name}/{no_kemekuji_seed:08X}.png'), width = 480)
            tables.append(img)
            tables.append(soup.new_tag('br'))
        elif stage_name == 'CH2-2':
            tables.append('地形とタマゴムシ')
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
            tables.append(table)

            tables.append(soup.new_tag('p', style = 'margin:20px'))
            
            tables.append('タマゴムシの確率 (B1とB2の合計)')
            b1_mitites_probs = [calc_mitites_prob(2, mitites) for mitites in range(3)]
            b2_mitites_probs = [0] + [
                sum(result[f'{{room: {room}, mitites: {mitites}}}'] 
                    for room in ['circle', 'circle_s', 'crescent']) / num_to_generate 
                    for mitites in [1, 2]]
            mitites_probs = [0] * (len(b1_mitites_probs) + len(b2_mitites_probs) - 1)
            for i in range(len(b1_mitites_probs)):
                for j in range(len(b2_mitites_probs)):
                    mitites_probs[i + j] += b1_mitites_probs[i] * b2_mitites_probs[j] 
            table = create_mitites_table(soup, mitites_probs = mitites_probs)
            tables.append(table)
        elif stage_name == 'CH5-2':
            tables.append('タマゴ出現数')
            max_eggs: int = max(yaml.safe_load(k)['eggs'] for k in result.keys())
            eggs = [result.get(f'{{eggs: {egg}}}', 0) for egg in range(max_eggs + 1)]
            table = create_count_table(soup, eggs)
            tables.append(table)

            tables.append(soup.new_tag('p', style = 'margin:20px'))

            tables.append('タマゴムシの確率 (B1とB2の合計)')
            b1_mitites_probs = [calc_mitites_prob(8, mitites) for mitites in range(9)]
            b2_mitites_probs = [
                sum(result.get(f'{{eggs: {eggs}}}', 0) / num_to_generate * calc_mitites_prob(eggs, mitites) 
                for eggs in range(2)) for mitites in range(2)
            ]
            mitites_probs = [0] * (len(b1_mitites_probs) + len(b2_mitites_probs) - 1)
            for i in range(len(b1_mitites_probs)):
                for j in range(len(b2_mitites_probs)):
                    mitites_probs[i + j] += b1_mitites_probs[i] * b2_mitites_probs[j]
            table = create_mitites_table(soup, mitites_probs = mitites_probs)
            tables.append(table)
        elif stage_name == 'CH8':
            tables.append('コチャ出現数')
            max_kochas: int = max(yaml.safe_load(k)['kocha'] for k in result.keys())
            kochas = [result.get(f'{{kocha: {kocha}}}', 0) for kocha in range(max_kochas + 1)]
            table = create_count_table(soup, kochas)
            tables.append(table)
        elif stage_name == 'CH18-1':
            tables.append('ヤキチャッピー出現率')
            counts = [result['{yakicha: true}'], result['{yakicha: false}']]
            table = create_true_false_table(soup, counts)
            tables.append(table)

            tables.append(soup.new_tag('p', style = 'margin:20px'))

            tables.append('タマゴ出現数')
            max_eggs: int = max(yaml.safe_load(k).get('eggs', -1) for k in result.keys())
            eggs = [result.get(f'{{eggs: {egg}}}', 0) for egg in range(max_eggs + 1)]
            table = create_count_table(soup, eggs)
            tables.append(table)

            tables.append(soup.new_tag('p', style = 'margin:20px'))

            tables.append('タマゴムシの確率')
            egg_probs = [result.get(f'{{eggs: {eggs}}}', 0) / num_to_generate for eggs in range(max_eggs + 1)]
            table = create_mitites_table(soup, egg_probs = egg_probs)
            tables.append(table)
        elif stage_name in ['CH20-1', 'CH29']:
            tables.append('タマゴ出現数')
            max_eggs: int = max(yaml.safe_load(k)['eggs'] for k in result.keys())
            eggs = [result.get(f'{{eggs: {egg}}}', 0) for egg in range(max_eggs + 1)]
            table = create_count_table(soup, eggs)
            tables.append(table)

            tables.append(soup.new_tag('p', style = 'margin:20px'))

            tables.append('タマゴムシの確率')
            egg_probs = [result.get(f'{{eggs: {eggs}}}', 0) / num_to_generate for eggs in range(max_eggs + 1)]
            table = create_mitites_table(soup, egg_probs = egg_probs)
            tables.append(table)
        elif stage_name == 'CH28':
            tables.append('タマゴ出現数')
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
            tables.append(table)

            tables.append(soup.new_tag('p', style = 'margin:20px'))

            tables.append('タマゴムシの確率（キショイグモあり）')
            egg_probs = [result.get(f'{{eggs: {eggs}, elec: true}}', 0) / num_to_generate for eggs in range(6)]
            table = create_mitites_table(soup, egg_probs = egg_probs)
            tables.append(table)
        else:
            raise NotImplementedError
    
        tables.append(soup.new_tag('br'))
        soup.append(tables)

    return flask.Markup(soup.prettify())