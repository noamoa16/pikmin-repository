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

def create_count_table2d(
        soup: BeautifulSoup, 
        counts: list[list[int]] | np.ndarray, 
        xlabels: list[Any],
        ylabels: list[Any],
        *,
        title: str | None = None,
        xsum: bool = True,
        ysum: bool = True,
        ):
    '''
    `counts`を縦横に並べた表を作成
    '''
    counts = np.array(counts)
    num_to_generate = int(counts.sum())
    xlabels = list(map(str, xlabels))
    ylabels = list(map(str, ylabels))
    rows = 3 * counts.shape[0] + 1
    cols = counts.shape[1] + 1
    if ysum: rows += 3
    if xsum: cols += 1
    array = np.full((rows, cols), '', dtype = object)
    if title is not None: array[0, 0] = title
    array[1:, 0] = '↓'
    array[3 * np.arange(counts.shape[0]) + 1, 0] = ylabels
    if xsum: array[0, -1] = '合計'
    if ysum: array[-3, 0] = '合計'
    array[0, 1: 1 + counts.shape[1]] = xlabels
    for i in range(counts.shape[0]):
        for j in range(counts.shape[1]):
            array[3 * i + 1: 3 * i + 4, j + 1] = get_count_prob_tuple(counts[i, j], num_to_generate)
        if xsum:
            array[3 * i + 1: 3 * i + 4, -1] = get_count_prob_tuple(counts[i, :].sum(), num_to_generate)
    if ysum:
        for j in range(counts.shape[1]):
            array[-3:, j + 1] = get_count_prob_tuple(counts[:, j].sum(), num_to_generate)
    if xsum and ysum:
        array[3 * counts.shape[0] + 1: 3 * counts.shape[0] + 4, counts.shape[1] + 1] = get_count_prob_tuple(num_to_generate, num_to_generate)
    background_color = np.full(array.shape, '', dtype = object)
    background_color[0, :] = '#d0d0d0'
    background_color[3 * np.arange(rows // 3) + 1, :] = '#e0e0e0'
    table = create_table(soup, array, background_color = background_color)
    return table

def create_true_false_table_from_counts(soup: BeautifulSoup, counts: list[int]) -> bs4.Tag:
    '''
    ありかなしかの2択を表す表を作成
    '''
    return create_count_table(soup, counts, labels = ['あり', 'なし'])

def create_true_false_table_from_result(soup: BeautifulSoup, result: dict[str, Any], name: str) -> bs4.Tag:
    counts = [result[f'{{{name}: true}}'], result[f'{{{name}: false}}']]
    return create_true_false_table_from_counts(soup, counts)

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

def load_cavegen_image(soup: BeautifulSoup, stage_name_full: str, seed: int) -> bs4.Tag:
    img_src = '..' + flask.url_for('static', filename = f'images/CaveGen/{stage_name_full}/{seed:08X}.png')
    img = soup.new_tag('img', src = img_src, width = 480, decoding = "async", alt = f'{stage_name_full} - 0x{seed:08X}')
    return img

def parse_data(data_str: str):
    data: dict[str, Any] = yaml.safe_load(data_str)
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
        stage_name_full = stage_name if '-' in stage_name else (stage_name + '-1')
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

        if stage_name in ['FC-4', 'BK-6', 'GK-5', 'SR-5']:
            tables.append('ムラサキポンガシ出現率')
            table = create_true_false_table_from_result(soup, result, 'murasakipom')
            tables.append(table)
        elif stage_name in ['FC-7', 'SC-4']:
            tables.append('オオガネモチ出現率')
            table = create_true_false_table_from_result(soup, result, 'oogane')
            tables.append(table)
        elif stage_name == 'SCx-4':
            tables.append('シロポンガシ出現数')
            counts = [result.get(f'{{whitepom: {i}}}', 0) for i in range(4)]
            table = create_count_table(soup, counts)
            tables.append(table)
        elif stage_name == 'SCx-7':
            tables.append('固定タマコキン出現率')
            table = create_true_false_table_from_result(soup, result, 'fixedTamakokin')
            tables.append(table)
        elif stage_name == 'BK-4':
            tables.append('ムラサキポンガシ出現数')
            counts = [result.get(f'{{murasakipom: {i}}}', 0) for i in range(3)]
            table = create_count_table(soup, counts)
            tables.append(table)
        elif stage_name == 'CoS-3':
            tables.append('ポポガシグサ出現率')
            table = create_true_false_table_from_result(soup, result, 'popogashi')
            tables.append(table)
        elif stage_name == 'CoS-4':
            tables.append('お宝持ちシャコモドキ出現率')
            table = create_true_false_table_from_result(soup, result, 'chocolate')
            tables.append(table)
        elif stage_name == 'GK-3':
            tables.append('カスタネット出現率')
            table = create_true_false_table_from_result(soup, result, 'castanets')
            tables.append(table)

            tables.append(soup.new_tag('p', style = 'margin:20px'))

            tables.append('キイロポンガシ出現率')
            table = create_true_false_table_from_result(soup, result, 'yellowpom')
            tables.append(table)
        elif stage_name == 'SR-6':
            tables.append('オナラシ出現率')
            table = create_true_false_table_from_result(soup, result, 'onarashi')
            tables.append(table)
        elif stage_name == 'SR-7':
            tables.append('ケメクジ出現率')
            table = create_true_false_table_from_result(soup, result, 'kemekuji')
            tables.append(table)

            tables.append(soup.new_tag('p', style = 'margin:20px'))

            no_kemekuji_seed: int = data[stage_name]['seeds']['no_kemekuji']
            tables.append(f'ケメクジのいない地形 (シード値 = 0x{no_kemekuji_seed:08X})')
            tables.append(soup.new_tag('br'))
            img = load_cavegen_image(soup, stage_name_full, no_kemekuji_seed)
            tables.append(img)
            tables.append(soup.new_tag('br'))
        elif stage_name == 'CH2-2':
            tables.append('地形とタマゴムシ')
            counts = np.zeros((3, 2), dtype = np.int64)
            for i, room in enumerate(['circle', 'circle_s', 'crescent']):
                for j, mitites in enumerate([1, 2]):
                    counts[i, j] = result[f'{{room: {room}, mitites: {mitites}}}']
            table = create_count_table2d(
                soup, 
                counts, 
                [1, 2], 
                ['丸部屋', '丸部屋 (S字)', '三日月'], 
                title = '地形＼タマゴムシ',
            )
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
        elif stage_name == 'CH7-2':
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
        elif stage_name == 'CH8':
            tables.append('コチャ出現数')
            max_kochas: int = max(yaml.safe_load(k)['kocha'] for k in result.keys())
            kochas = [result.get(f'{{kocha: {kocha}}}', 0) for kocha in range(max_kochas + 1)]
            table = create_count_table(soup, kochas)
            tables.append(table)
        elif stage_name == 'CH18-1':
            tables.append('ヤキチャッピー出現率')
            table = create_true_false_table_from_result(soup, result, 'yakicha')
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

            tables.append(soup.new_tag('p', style = 'margin:20px'))

            _8eggs_seed: int = data[stage_name]['seeds']['8eggs']
            tables.append(f'タマゴ8個の地形 (シード値 = 0x{_8eggs_seed:08X})')
            tables.append(soup.new_tag('br'))
            img = load_cavegen_image(soup, stage_name_full, _8eggs_seed)
            tables.append(img)
            tables.append(soup.new_tag('br'))
        elif stage_name == 'CH20-1':
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

            tables.append(soup.new_tag('p', style = 'margin:20px'))

            best_seed: int = data[stage_name]['seeds']['best']
            tables.append(f'タマゴ5個の地形(一例) (シード値 = 0x{best_seed:08X})')
            tables.append(soup.new_tag('br'))
            img = load_cavegen_image(soup, stage_name_full, best_seed)
            tables.append(img)
            tables.append(soup.new_tag('br'))
        elif stage_name == 'CH21-1':
            tables.append('敵の数 (ウジンコ♂, ウジンコ♀, トビンコ)')
            counts = []
            labels = []
            for key, count in result.items():
                enemy_dict: dict[str, int] = yaml.safe_load(key)
                label = (enemy_dict['ujiosu'], enemy_dict['ujimesu'], enemy_dict['tobinko'])
                labels.append(label)
                counts.append(count)
            labels, counts = zip(*sorted(
                zip(labels, counts), 
                key = lambda t: t[0][0] * 87 + t[0][1] * 86 + t[0][2] * 62
            ))
            labels = list(map(str, labels))
            table = create_count_table(soup, counts, labels = labels)
            tables.append(table)
        elif stage_name == 'CH26-3':
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

            tables.append(soup.new_tag('p', style = 'margin:20px'))

            _10eggs_seed: int = data[stage_name]['seeds']['10eggs']
            tables.append(f'タマゴ10個の地形 (シード値 = 0x{_10eggs_seed:08X})')
            tables.append(soup.new_tag('br'))
            img = load_cavegen_image(soup, stage_name_full, _10eggs_seed)
            tables.append(img)
            tables.append(soup.new_tag('br'))
        elif stage_name == 'CH28':
            tables.append('間欠泉出現率')
            table = create_true_false_table_from_result(soup, result, 'geyser')
            tables.append(table)

            tables.append(soup.new_tag('p', style = 'margin:20px'))

            tables.append('タマゴ出現数')
            counts = np.zeros((2, 6), dtype = np.int64)
            for i, elec in enumerate(['true', 'false']):
                for j, eggs in enumerate(range(6)):
                    counts[i, j] = result.get(f'{{eggs: {eggs}, elec: {elec}}}', 0)
            table = create_count_table2d(
                soup, 
                counts, 
                list(range(6)), 
                ['エレキショイグモあり', 'エレキショイグモなし'], 
                title = 'タマゴ',
                ysum = False,
            )
            tables.append(table)

            tables.append(soup.new_tag('p', style = 'margin:20px'))

            tables.append('タマゴムシの確率（キショイグモあり）')
            egg_probs = [result.get(f'{{eggs: {eggs}, elec: true}}', 0) / num_to_generate for eggs in range(6)]
            table = create_mitites_table(soup, egg_probs = egg_probs)
            tables.append(table)
        elif stage_name == 'CH29':
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

            tables.append(soup.new_tag('p', style = 'margin:20px'))

            _7eggs_seed: int = data[stage_name]['seeds']['7eggs']
            tables.append(f'タマゴ7個の地形 (シード値 = 0x{_7eggs_seed:08X})')
            tables.append(soup.new_tag('br'))
            img = load_cavegen_image(soup, stage_name_full, _7eggs_seed)
            tables.append(img)
            tables.append(soup.new_tag('br'))
        else:
            raise NotImplementedError
    
        tables.append(soup.new_tag('br'))
        soup.append(tables)

    return flask.Markup(soup.prettify())