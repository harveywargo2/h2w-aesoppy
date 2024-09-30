import pandas as pd
import aesoppy.gurufocus as gf
from datetime import date


class DivYieldAnalysis:

    def __init__(self, **kwargs):
        self.token = kwargs.get('token', 'error')
        self.ticker = kwargs.get('ticker', 'error')
        self.frequency = kwargs.get('frequency', 4)
        self.div_data = gf.DividendHistory(token=self.token, ticker=self.ticker).div_df()
        self.price_data = gf.PriceHistory(token=self.token, ticker=self.ticker).price_df()
        self.div_yield_analysis_cy = self._div_yield_analysis_df()
        self.div_yield_analysis_aggr_cy = self._div_yield_analysis_aggregate_df()


    def _div_yield_analysis_df(self):
        div_df1 = self.div_data
        price_df1 = self.price_data
        div_var = 0.0

        # Trim out unwanted columns in div_data
        div_df1 = div_df1.loc[div_df1['DividendType'] != 'Special Div.']
        div_df1 = div_df1.drop(['RecordDate', 'PayDate', 'Currency'], axis=1)

        # Join Price and Dividend Data
        dy_df1 = price_df1.join(div_df1)
        dy_df1['Dividend'].fillna(0, inplace=True)
        dy_df1['DivPay'] = dy_df1['Dividend']

        for index, row in dy_df1.iterrows():
            if row['DivPay'] > 0:
                div_var = row['DivPay']
            else:
                dy_df1.at[index, 'DivPay'] = div_var

        # Trim data set to 30 years
        current_year = date.today().year

        for date_index, row in dy_df1.iterrows():
            if current_year - date_index.year >= 30:
                dy_df1.drop(date_index, inplace=True)

        # Add Fwd Div
        dy_df1['DivPeriod'] = self.frequency
        dy_df1['FwdDiv'] = dy_df1['DivPay'] * self.frequency
        dy_df1['FwdDivYield'] = dy_df1['FwdDiv'] / dy_df1['SharePrice']

        # Use dy_df1 to troubleshoot dropping all unused columns
        dy_df2 = dy_df1.drop(['DividendType', 'DivPeriod', 'DivPay'], axis=1)

        return dy_df2


    def _div_yield_analysis_aggregate_df(self):
        dy_df1 = self.div_yield_analysis

        dy_df2 = dy_df1.groupby(dy_df1.index.year).agg(
            {'SharePrice': ['min', 'max', 'mean', 'median'],
             'FwdDivYield': ['min', 'max', 'mean', 'median'],
             'Dividend': ['sum']})

        return dy_df2










