import yfinance as yf
import pandas as pd
import numpy as np

class data_prep:
    def __init__(self):
        pass

    def download_data( ticker, start_date, end_date, int):
        """
        Downloads historical stock data for the given ticker between start_date and end_date.
        """
        data = yf.download(ticker, 
                                start=start_date, end=end_date,
                                interval = int, 
                                group_by = 'column')
        return data
    
    