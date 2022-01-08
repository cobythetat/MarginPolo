
# REMEMBER TO MAKE A FILE CALLED api_credentials.txt
# AND PUT IN API KEY FIRST LINE
# API SECRET ON SECOND LINE

TICK_RATE = 10  # seconds between querying price, and updating/accelerating stop loss/stop distance
CANDLE_PERIOD = 1800  # timeframe for chart. For valid inputs, see Poloniex Documentation for pulling chart data
ATR_PERIOD = 14  # last n candles to use for calculating the ATR value
STOP_LOSS = 2  # ATR is multiplied by this number, and subtracted/added to base price to give us stop loss
ACCELERATE = 1  # +% profits are subtracted from the stop loss distance after being multiplied by this number
TRADES_FOLDER_PATH = 'trades'  # folder for saving .json trade data
