
def read_keys_from_file():
    with open('api_credentials.txt') as file:
        api_key = file.readline().strip()
        api_secret = file.readline().strip()
        return api_key, api_secret


def dump_json_to_file(file_path, json_data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)


def calculate_avg_true_range(candle_chart, period=14):
    true_ranges = []
    previous_candle = None
    candles = candle_chart[-abs(period):]
    for i in range(len(candles)):
        if i == 0:
            previous_candle = candles[i]
        x = float(candles[i]['high']) - float(candles[i]['low'])
        y = abs(float(candles[i]['high']) - float(previous_candle['close']))
        z = abs(float(candles[i]['low']) - float(previous_candle['close']))
        true_ranges.append(max([x, y, z]))
        previous_candle = candles[i]
        i += 1
    return sum(true_ranges) / len(true_ranges)
