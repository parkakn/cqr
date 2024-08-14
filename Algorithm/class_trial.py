import yfinance as yf
import pandas as pd
import numpy as np

class StockData:
    def __init__(self):
        pass

    def download_data(self, ticker, start_date, end_date, int):
        """
        Downloads historical stock data for the given ticker between start_date and end_date.
        """
        data = yf.download(ticker, 
                                start=start_date, end=end_date,
                                interval = int, 
                                group_by = 'column')
        return data
    
    # Get monthly price 
    def get_monthly(self,data):
        if isinstance(data.Close, pd.Series) == False:
            price = data.Close.dropna(thresh = len(data.Close.columns))
        else:
            price = data.Close
        pr = price.reset_index()
        self.monthly_pr = pr[(pr.Date.dt.month - pr.Date.shift(-1).dt.month).isin([0,np.nan]) == False]
        self.monthly_pr.set_index("Date",inplace=True)
        return self.monthly_pr

    # Get daily return 
    def clean(self,data):
        """ Clean Data """
        self.df = data.Close.dropna(thresh = 7)
        self.df = (self.df.pct_change()+1)      # Output as returns
        self.df.replace(np.nan, 1, inplace = True)
        self.df = self.df.reset_index()
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        self.df.insert(1, 'month', self.df.Date.dt.month)
        self.df.insert(1, 'year', self.df.Date.dt.year)
        self.df.insert(1, 'end of month', 
                     (self.df.Date.dt.month - self.df.Date.shift(-1).dt.month).isin([0,np.nan]))
        self.df.set_index('Date',inplace= True)


        """" Returns Dataframe"""
        self.ret = self.df.iloc[:,3:]   
        return self.df, self.ret

    def algo1(self,initial_cash,odd_buy,odd_hold,even_buy,even_hold):  # 11 - 4, 5 - 10 
        # Halloween Adjusted 짝수 홀수 11 - 4 월 (아빠)
        """ Without the assumption of starting cash"""

        """ Weights """
        odd_stock_w = 0.7
        odd_bond_w = 0.3
        even_stock_w = 0.5
        even_bond_w = 0.5
        even_passive_stock_w = 0.3
        even_passive_bond_w = 0.7

        #odd_buy = np.array([0.4*odd_stock_w, (1/3*odd_bond_w), 0.0*odd_stock_w, 0.0*odd_stock_w, (1/3*odd_bond_w), (1/3*odd_bond_w), 0.6*odd_stock_w])          # Even 11 - Odd 4
        #odd_hold = np.array([0.4*odd_stock_w, (1/3*odd_bond_w), 0.0*odd_stock_w, 0.0*odd_stock_w, (1/3*odd_bond_w), (1/3*odd_bond_w), 0.3*odd_stock_w])         # Odd 5 - Odd 10
        #even_buy = np.array([0.4*even_stock_w, (1/3*even_bond_w), 0.0*even_stock_w, 0.0*even_stock_w, (1/3*even_bond_w), (1/3*even_bond_w), 0.6*even_stock_w])  # Odd 11 - Even 4. NOTE: Here, we shift Kospi weight to Nasdaq instead of S&P 500 to be consistent with our logic that 11-4 should be more aggressive than 5-10. 
        #even_hold = np.array([0.5*even_passive_stock_w, (1/3*even_passive_bond_w), 0.0*even_passive_stock_w, 0.0*even_passive_stock_w, (1/3*even_passive_bond_w), (1/3*even_passive_bond_w), 0.5*even_passive_stock_w])  # Even 5 - Even 10
        
        port_list = [initial_cash]  # Seed money 
        port = port_list[0]

        self.shares = []              # record shares 
        self.mkt_val = []             # mkt value of assets
        self.cash_rem = []            # cash remaining 
        self.strat = []               # aggressive/defensive 

        self.rebal = []

        # Indicator for whether we have entered the market or not
        invested = False

        # Start Backtest! 
        for i in range(len(self.df)):
            
            if invested == False: 
                # We are not yet invested in any assets. All Cash 
                pass
            else: 
                # Now, we assume that we have # of shares, mkt value of each asset (i.e. we are invested)
                #print("Print daily return", test1['Date'][i])
                new_mkt_value = mkt_value*(self.ret.iloc[i,:]) # Record returns over the previous period 
                # NOTE: For daily returns, each asset return should be equal to the returns matrix. But, portfolio value may be unique. 
                port = np.sum(new_mkt_value) + cash_remaining # Record new portfolio value 
                port_list.append(new_mkt_value)

                # Daily (Record daily changes in mkt value, shares, and remaining cash)
                # Remaining cash, shares - constant. Mkt value - changing. 
                # Portfolio mkt value - changing (recorded above). 
                if bool(self.df['end of month'][i]) == True:
                    #shares.append(s.values)
                    self.cash_rem.append(cash_remaining)
                    self.strat.append(x)
                    self.mkt_val.append(new_mkt_value.values)
                    mkt_value = new_mkt_value
                    self.rebal.append(False)

            # When to rebalance (Rebalance at last trading day of month)
                    
            if i == 0: # 첫 계정 오픈 날!
                if bool(self.df['end of month'][i]) == False:  # If we start at end of the month
                    if ((self.df.month.values[i] in [10,11,12]) & (self.df.year.values[i]%2 == 0)) or ((self.df.month.values[i] in [1,2,3]) & (self.df.year.values[i]%2 == 1)): # Halloween strategy. Ex) 2016.10 말 - 2017.3월말. 
                        X = odd_buy 
                        x = "odd aggressive"
                        self.strat.append(x)
                    elif (self.df.month.values[i] in [4,5,6,7,8,9]) & (self.df.year.values[i]%2 == 1): 
                        X = odd_hold 
                        x = "odd passive"
                        self.strat.append(x)
                    elif ((self.df.month.values[i] in [10,11,12]) & (self.df.year.values[i]%2 == 1)) or ((self.df.month.values[i] in [1,2,3]) & (self.df.year.values[i]%2 == 0)): # ex) 2017.10 - 2018.3
                        X = even_buy 
                        x = "even aggressive"
                        self.strat.append(x)
                    elif (self.df.month.values[i] in [4,5,6,7,8,9]) & (self.df.year.values[i]%2 == 0): 
                        X = even_hold
                        x = "even passive"
                        self.strat.append(x)
                else:    # If we don't start at end of the month
                    if ((self.df.month.values[i] in [11,12]) & (self.df.year.values[i]%2 == 0)) or ((self.df.month.values[i] in [1,2,3,4]) & (self.df.year.values[i]%2 == 1)): 
                        X = odd_buy 
                        x = "odd aggressive"
                        self.strat.append(x)
                    elif (self.df.month.values[i] in [5,6,7,8,9,10]) & (self.df.year.values[i]%2 == 1): 
                        X = odd_hold 
                        x = "odd passive"
                        self.strat.append(x)
                    elif ((self.df.month.values[i] in [11,12]) & (self.df.year.values[i]%2 == 1)) or ((self.df.month.values[i] in [1,2,3,4]) & (self.df.year.values[i]%2 == 0)): 
                        X = even_buy 
                        x = "even aggressive"
                        self.strat.append(x)
                    elif (self.df.month.values[i] in [5,6,7,8,9,10]) & (self.df.year.values[i]%2 == 0): 
                        X = even_hold
                        x = "even passive"
                        self.strat.append(x)
                
                # Execute rebalance (# of shares of each asset, mkt value of each asset, cash remaining)
                mkt_value = X*port  # Market value (share X price) of each asset we will be holding 
                self.mkt_val.append(mkt_value)
                cash_remaining = port - np.sum(mkt_value) # Remaining cash in our portfolio 
                self.cash_rem.append(cash_remaining)
                
                # Tell indicator that we are invested
                invested = True
                
                # Indicate: Rebalance date
                self.rebal.append(True)

            else: # 첫 오픈 이후 only rebalance at end of month! 
                if bool(self.df['end of month'][i]) == False: # If end of month, we balance. 
                    #print("Rebalance", test1["Date"][i])
                    # Determine which strategy to use
                    if ((self.df.month.values[i] in [10,11,12]) & (self.df.year.values[i]%2 == 0)) or ((self.df.month.values[i] in [1,2,3]) & (self.df.year.values[i]%2 == 1)): # Halloween strategy
                        X = odd_buy 
                        x = "aggressive"
                        self.strat.append(x)
                    elif (self.df.month.values[i] in [4,5,6,7,8,9]) & (self.df.year.values[i]%2 == 1): 
                        X = odd_hold 
                        x = "odd passive"
                        self.strat.append(x)
                    elif ((self.df.month.values[i] in [10,11,12]) & (self.df.year.values[i]%2 == 1)) or ((self.df.month.values[i] in [1,2,3]) & (self.df.year.values[i]%2 == 0)): 
                        X = even_buy 
                        x = "even aggressive"
                        self.strat.append(x)
                    elif (self.df.month.values[i] in [4,5,6,7,8,9]) & (self.df.year.values[i]%2 == 0): 
                        X = even_hold
                        x = "even passive"
                        self.strat.append(x)
                    # Execute rebalance (# of shares of each asset, mkt value of each asset, cash remaining)
                    #s = np.floor_divide((X*port),test1.iloc[i,4:]) # Determine number of shares for each asset! 
                    #shares.append(s.values)
                    mkt_value = X*port  # Market value (share X price) of each asset we will be holding 
                    self.mkt_val.append(mkt_value)
                    cash_remaining = port - np.sum(mkt_value) # Remaining cash in our portfolio 
                    self.cash_rem.append(cash_remaining)
                    
                    # Indicate: Rebalance date
                    self.rebal.append(True)
                # No else because if not end of month, we don't do anything. 
                    
        return self.shares, self.cash_rem, self.mkt_val,self.strat

    def results(self):
        """ Organize results """
        # 1. Shares, Market Value, Portfolio Value 
            #res = pd.DataFrame(self.shares)
            #res.columns = self.ret.columns + ' shares'
        self.result = pd.DataFrame(self.mkt_val)
        self.result.columns = self.ret.columns + ' mkt val'
        self.result.index = self.ret.index[-len(self.result):]
        self.result['cash_rem'] = self.cash_rem
        self.result['port_val'] = self.result.iloc[:, :].sum(axis=1)
        self.result['strat'] = self.strat

        # 2. Portfolio Weights (%)
        self.res_pct = self.result[self.result.columns[:-1]].div(self.result[self.result.columns[-2]], axis=0)
        self.res_pct['strat'] = self.strat

        return self.result, self.res_pct

    # 1. 일별수익률추이
    def daily_ret(self):
        report = self.result.copy()
        report['일별수익률'] = self.result['port_val'].pct_change()
        report['누적수익률'] = self.result['port_val']/self.result['port_val'][0]-1
        report.replace(np.nan, 0, inplace = True)
        del report['strat']
        self.report1 = report
        return self.report1
    
    # 2. 월별수익률추이
    def monthly_ret(self):
        self.report2 = self.report1[(self.report1.reset_index().index == 0) |(self.report1.reset_index().index == (len(self.report1)-1) ) | ~(self.report1.reset_index().Date.dt.month - \
                    self.report1.reset_index().Date.shift(-1).dt.month).isin([0,np.nan]).values].iloc[:,:-2]
        #self.report2.columns = ['월별수익률']
        self.report2['월별수익률'] = self.report2['port_val'].pct_change()
        self.report2.replace(np.nan, 0, inplace = True)
        self.report2['누적수익률'] = self.report2['port_val']/self.report2['port_val'][0]-1
        return self.report2
    
    # (Function to be used for #3)
    def to_percentage(self, value):
        return f"{value * 100:.2f}%"

    # 3. 자산별투자비중추이
    def portfolio_by_asset_class(self):
        risk_level = [3, 1, 3, 2, 1, 1, 5]  # 코덱스, 3년, 나스닥, s&p, 단기채권, 단기통안채, 코스
        asset_perc = pd.DataFrame([self.res_pct.iloc[:,[6]].sum(axis = 1),
            self.res_pct.iloc[:,[0,2]].sum(axis = 1),
            self.res_pct.iloc[:,[3]].sum(axis = 1),
            self.res_pct.iloc[:,[1,4,5]].sum(axis = 1),
            self.res_pct.iloc[:,[7]].sum(axis = 1),],
            index = [5,3,2,1,0]).T
        asset_perc['total'] = asset_perc.sum(axis = 1)
        asset_perc['위험자산비중'] = asset_perc[[5]]

        self.max_asset_weight = asset_perc.iloc[:,:5].max().max()   # 개별 자산비중 최고치
        self.X = asset_perc.applymap(self.to_percentage)
        self.X['rebal'] = self.rebal
        return self.max_asset_weight, self.X
    
    # 4. 종목별투자비중추이
    def portfolio_by_ind_assets(self):
        self.X1 = self.res_pct.iloc[:,:-1].applymap(self.to_percentage)
        return self.X1
    
    # 5. 리밸런싱발생내역
    def rebalance_history(self):
        self.X_rebal = self.X[self.X.rebal == True]
        return self.X_rebal
    