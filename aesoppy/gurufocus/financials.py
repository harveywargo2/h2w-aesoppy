import requests
import pandas as pd


class Financials:
    """
    Description:
        GuruFocus api call to historical financial data
        Historical data includes annual and quarterly
    Args:
        token (string): GuruFocus API Token
        ticker (string): Stock Ticker
    Returns:
        api_data (object): raw api output from api call
        fin_annual_data (dataframe): annual data
        fin_quarterly_data (dataframe)
    """
    def __init__(self, **kwargs):
        self.token = kwargs.get('token', 'error')
        self.ticker = kwargs.get('ticker', 'error')
        self.fin_data = self._fin_api_data()
        self.fin_annual_data = self._fin_annual_api_data()
        self.fin_quarterly_data = self._fin_quarterly_api_data()


    def _fin_api_data(self):
        return requests.get(f'https://api.gurufocus.com/public/user/{str(self.token)}/stock/{str(self.ticker)}/financials').json()


    def _fin_annual_api_data(self):
        annual_df1 = pd.DataFrame.from_dict(self.fin_data)
        x_loc = 0
        annual_df2 = pd.json_normalize(annual_df1.loc['annuals'])
        annual_df3 = pd.DataFrame()

        for item, values in annual_df2.items():
            series_expand = pd.Series(values, name=item).explode(ignore_index=True)
            series_df = series_expand.to_frame()
            annual_df3 = pd.concat([annual_df3, series_df], axis=1)
            x_loc += 1

        annual_df4 = annual_df3.convert_dtypes()

        return annual_df4


    def _fin_quarterly_api_data(self):
        qtr_df1 = pd.DataFrame.from_dict(self.fin_data)
        x_loc = 0
        qtr_df2 = pd.json_normalize(qtr_df1.loc['quarterly'])
        qtr_df3 = pd.DataFrame()

        for item, values in qtr_df2.items():
            series_expand = pd.Series(values, name=item).explode(ignore_index=True)
            series_df = series_expand.to_frame()
            qtr_df3 = pd.concat([qtr_df3, series_df], axis=1)
            x_loc += 1

        qtr_df4 = qtr_df3.convert_dtypes()

        return qtr_df4



