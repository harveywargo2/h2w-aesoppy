import requests
import pandas as pd


class GuruDividendHistory:

    def __init__(self, **kwargs):
        self.token = kwargs.get('token', 'error')
        self.ticker = kwargs.get('ticker', 'error')
        self.api_data = self._api_data()
        self.api_data_type = type(self.api_data)
        self.api_data_df = self._api_data_df()
        self.api_data_df_ex_date_index = self._api_data_df_ex_date_index()


    def _api_data(self):
        return requests.get(f'https://api.gurufocus.com/public/user/{str(self.token)}/stock/{str(self.ticker)}/dividend').json()


    def _api_data_df(self):
        div_list = self.api_data
        div_df = pd.DataFrame(div_list)

        return div_df


    def _api_data_df_ex_date_index(self):

        div_list = self.api_data
        div_df = pd.DataFrame(div_list)
        div_df['ex_date'] = pd.to_datetime(div_df['ex_date'])
        div_df['amount'] = div_df['amount'].astype(float)
        div_df.set_index('ex_date', inplace=True)
        div_df.rename(columns={
            'amount': 'dividend_amount',
            'type': 'dividend_type'
        })

        return div_df

