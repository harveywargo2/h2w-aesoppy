import requests
import pandas as pd


class DividendHistory:

    def __init__(self, **kwargs):
        self.token = kwargs.get('token', 'error')
        self.ticker = kwargs.get('ticker', 'error')
        self.api_data = self._div_api_data()


    def _div_api_data(self):
        return requests.get(f'https://api.gurufocus.com/public/user/{str(self.token)}/stock/{str(self.ticker)}/dividend').json()


    def div_df(self, **kwargs):
        self.column_normalize = kwargs.get('column_normalize', True)
        self.index_exdate = kwargs.get('index_exdate', True)

        div_list = self.api_data
        div_df = pd.DataFrame(div_list)
        div_df['ex_date'] = pd.to_datetime(div_df['ex_date'])
        div_df['amount'] = div_df['amount'].astype(float)


        if self.column_normalize == True:
            div_df.rename(columns={'amount': 'Dividend',
                                   'ex_date': 'ExDate',
                                   'record_date': 'RecordDate',
                                   'pay_date': 'PayDate',
                                   'type': 'DividendType',
                                   'currency': 'Currency'}, inplace=True)
        else:
            div_df #Do Nothing


        if self.index_exdate == True:
            if any(div_df.columns == 'ExDate'):
                div_df.set_index('ExDate', inplace=True)
            elif any(div_df.columns == 'ex_date'):
                div_df.set_index('ex_date', inplace=True)
            else:
                div_df # Do Nothing
        else:
            div_df # Do Nothing


        return div_df

