from random import randint

import yfinance as yf

def execute_function(name, arguments):
    funcs = {"get_stock_price": get_stock_price, "buy_or_sell": buy_or_sell, "dummy" : dummy}
    if name in funcs.keys():
        func = funcs[name]
        return func(**arguments)
    else: return ""
        #raise Exception(f"Unknown function: {name}")

def get_stock_price(symbol: str) -> float:
    stock = yf.Ticker(symbol)
    price = stock.history(period="1d")['Close'].iloc[-1]
    return price

def buy_or_sell(symbol:str, price:str):
    score = randint(1, 3)
    match score:
        case 1 : return "buy"
        case 2 : return "sell"
        case 3 : return "hold"

def dummy():
    return ""


