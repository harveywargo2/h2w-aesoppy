import pandas as pd
import aesoppy.aesop as aesop
from datetime import date


class DividendPerShareCy:

    def __init__(self, **kwargs):
        self.dividend_df = kwargs.get('dividend_df', 'error')
        self.frequency = kwargs.get('div_frequency', 4)
        self.lookback = kwargs.get('lookback', 21)
        self.pershare_div_cy_growth_df = self._pershare_div_cy_growth_df()
        self.current_year = aesop.aesop_now.year

    def _pershare_div_cy_growth_df(self):
        divgro_cy_df1 = self.dividend_df
        divgro_cy_df1.index = pd.to_datetime(divgro_cy_df1.index)

        divgro_cy_df2 = divgro_cy_df1.groupby(divgro_cy_df1.index.year).agg(
            dividend_amount_cy=pd.NamedAgg('dividend_amount', aggfunc='sum')
        )

        divgro_cy_df2['divgro_cy'] = divgro_cy_df2['dividend_amount_cy'].pct_change()

        return divgro_cy_df2


class DividendGrowthAnalysis:

    def __init__(self, **kwargs):
        self.dividend_df = kwargs.get('pershare_div_cy_df', 'error')
        self.financials_df = kwargs.get('pershare_div_fy_df', 'error')
        self.frequency = kwargs.get('div_frequency', 4)
        self.lookback = kwargs.get('lookback', 21)

