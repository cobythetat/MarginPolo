# [MarginPolo](https://poloniex.com/signup?c=2E28D52D)

## Easy-to-use Python bot for managing [Poloniex](https://poloniex.com/signup?c=2E28D52D) Margin Positions

#### How it works

Bot will loop through open margin positions, and set an initial stop loss `ATR*n` from base price.
After setting the stop loss, the distance to the base price is monitored, and will be accelerated
everytime the position is recorded in profit.

After getting latest price, the stop loss trails price at the current distance if price moved in favor of the trade,
and stays put if the move is closer to the stop loss.

Everytime the position is recorded as positive % profit, the distance is multiplied by `1 - (%profit * n)`

#### Example output
Conole output example, when running:

```python
[USDT_TRX LONG]
-- Base price    : 0.07750198 USDT
-- Current price : 0.07728653 USDT
-- stop loss     : 0.07680618 USDT (distance: 0.00069580 USDT)
-- P/L: -0.21521508 USDT (-0.28 %)
```

#### How to run
Open the folder in an IDE or in a terminal window after downloading or cloning, and make sure you got your api_credentials.txt file made, with api key on 
first line and api secret on second line. Run the main.py file:

```python
python main.py
```




