import requests
import pandas as pd


class PriceHistory:
    """
    Description:
        GuruFocus api call to historical price data
    Args:
        token (string): GuruFocus API Token
        ticker (string): Stock Ticker

    Returns:
        api_data (list): raw api output from api call
    """

    def __init__(self, **kwargs):
        self.token = kwargs.get('token', 'error')
        self.ticker = kwargs.get('ticker', 'error')
        self.price_data = self._price_api_data()

    def _price_api_data(self):
        return requests.get(f'https://api.gurufocus.com/public/user/{str(self.token)}/stock/{str(self.ticker)}/price').json()

    def price_df(self, **kwargs):
        """
        Description:
            Transformed DataFrame Object
        Args:
            index_date (boolean):
                True (default): Date set to Index
                False: integer index
        Returns:
            Pandas Dataframe of Indexed Price History
        """
        self.index_exdate = kwargs.get('index_date', True)
        price_list = self.price_data
        price_df = pd.DataFrame(price_list, columns=['Date', 'SharePrice'])
        price_df['Date'] = pd.to_datetime(price_df['Date'])


        if self.index_exdate == True:
            price_df.set_index('Date', inplace=True)
        else:
            price_df


        return price_df


