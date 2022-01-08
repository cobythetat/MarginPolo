import json


def read_keys():
    with open('api_credentials.txt') as file:
        api_key = file.readline().strip()
        api_secret = file.readline().strip()
        return api_key, api_secret


def dump_json_to_file(file_path, json_data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)


def calculate_avg_true_range(candles):
    true_ranges = []
    previous_candle = None
    for i in range(len(candles)):
        if i == 0:
            previous_candle = candles[i]
            continue
        x = float(candles[i]['high']) - float(candles[i]['low'])
        y = abs(float(candles[i]['high']) - float(previous_candle['close']))
        z = abs(float(candles[i]['low']) - float(previous_candle['close']))
        true_ranges.append(max([x, y, z]))
        previous_candle = candles[i]
        i += 1
    return sum(true_ranges) / len(true_ranges)


def aggregate_trades(trades):
    aggregated = {
        "amount": 0,
        "date": None,
        "rate": 0,
        "total": 0,
        "type": None,
        "adjustment": 0
    }
    rates = []
    for t in trades:
        aggregated['amount'] += float(t['amount'])
        aggregated['date'] = t['date']
        rates.append(float(t['rate']))
        aggregated['total'] += float(t['total'])
        aggregated['type'] = t['type']
        if 'takerAdjustment' in t:
            aggregated['adjustment'] += float(t['takerAdjustment'])
        if 'makerAdjustment' in t:
            aggregated['adjustment'] += float(t['makerAdjustment'])
    aggregated['rate'] = sum(rates) / len(rates)
    return aggregated
