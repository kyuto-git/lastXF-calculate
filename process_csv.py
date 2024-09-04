import pandas as pd
import os

# CSVファイルの読み込み（Shift-JISエンコーディング）
df = pd.read_csv('202408racerap.csv', encoding='shift_jis', skip_blank_lines=True)

def process_1(df):
    df['ワーク1計算'] = df['ワーク1'].apply(
        lambda x: round(sum(map(float, x.split('-')[-2:])), 1) if isinstance(x, str) else None)
    df['計算結果'] = df.apply(
        lambda row: round(row['ワーク1計算'] + row['着差'], 1) if row['着順'] >= 2 else row['ワーク1計算'], axis=1)
    for date, group in df.groupby('日付S'):
        date_str = str(date).replace('.0', '')
        filename = f'2F/{date_str}_2F.csv'
        group[['レースID(新)', '計算結果']].to_csv(filename, index=False, encoding='shift_jis')

def process_2(df):
    # 「ワーク1」列の右から1番目の数値を取得
    df['ワーク1計算'] = df['ワーク1'].apply(
        lambda x: round(float(x.split('-')[-1]), 1) if isinstance(x, str) else None)
    
    # クラス名による補正値を加算
    class_map = {'1勝': 0.1, '2勝': 0.2, '3勝': 0.3, 'ｵｰﾌﾟﾝ': 0.4, 'OP(L)': 0.4, 'Ｇ３': 0.5, 'Ｇ２': 0.6, 'Ｇ１': 0.7}
    df['計算結果'] = df.apply(
        lambda row: round(row['ワーク1計算'] + class_map.get(row['クラス名'], 0), 1) if row['着順'] <= 3 and row['補正'] >= 85 else None, axis=1)
    
    # 年齢限定による調整
    def adjust_age(row):
        if row['年齢限定'] == '２歳':
            return round(row['計算結果'] - 0.2, 1)
        elif row['年齢限定'] == '３歳':
            return round(row['計算結果'] - 0.1, 1)
        else:
            return row['計算結果']
    
    df['計算結果'] = df.apply(adjust_age, axis=1)
    
    # 日付ごとにファイルを保存
    for date, group in df.groupby('日付S'):
        date_str = str(date).replace('.0', '')
        filename = f'1F/{date_str}_1F.csv'
        group[['レースID(新)', '計算結果']].to_csv(filename, index=False, encoding='shift_jis')


def process_3(df):
    df['ワーク1計算'] = df['ワーク1'].apply(
        lambda x: round(sum(map(float, x.split('-')[-4:])), 1) if isinstance(x, str) else None)
    df['計算結果'] = df.apply(
        lambda row: round(row['ワーク1計算'] + (row['着差'] if row['着順'] >= 2 else 0), 1), axis=1)

    def subtract_race_mark(row):
        try:
            if isinstance(row['レース印２'], str):
                race_mark_value = float(row['レース印２'].replace('±', '').strip())
            else:
                race_mark_value = float(row['レース印２'])
        except ValueError:
            race_mark_value = 0
        if row['レース印２'] == '不能':
            return round(row['計算結果'] + 3.5, 1)
        else:
            return round(row['計算結果'] - race_mark_value, 1)

    df['計算結果'] = df.apply(subtract_race_mark, axis=1)

    distance_map = {
        '芝': {1000: 43.8, 1200: 45.8, 1400: 46.8, 1500: 47.7, 1600: 47.6, 1800: 48.8, 2000: 48.8, 2200: 49.2, 2300: 49.9, 2400: 49.9, 2500: 49.6, 2600: 50.1, 3000: 50.4, 3200: 50.0, 3400: 50.5, 3600: 50.5},
        'ダ': {1000: 47.5, 1150: 48.1, 1200: 48.8, 1300: 49.3, 1400: 49.4, 1600: 49.9, 1700: 50.5, 1800: 50.8, 1900: 50.7, 2000: 50.6, 2100: 51.1, 2400: 51.4, 2500: 51.1}
    }

    def adjust_distance(row):
        if row['芝・ダ'] in distance_map and row['距離'] in distance_map[row['芝・ダ']]:
            adjusted_value = round(distance_map[row['芝・ダ']][row['距離']] - row['計算結果'], 1)
        else:
            adjusted_value = row['計算結果']
        # 48.0から計算された値を引いた結果を返す
        final_result = round(48.0 - adjusted_value, 1)
        return final_result

    df['計算結果'] = df.apply(adjust_distance, axis=1)

    for date, group in df.groupby('日付S'):
        date_str = str(date).replace('.0', '')
        filename = f'4F/{date_str}_4F.csv'
        group[['レースID(新)', '計算結果']].to_csv(filename, index=False, encoding='shift_jis')

# 処理の実行
process_1(df)
process_2(df)
process_3(df)
