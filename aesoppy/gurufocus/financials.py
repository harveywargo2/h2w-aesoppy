import requests
import pandas as pd



class GuruFinancials:
    def __init__(self, **kwargs):
        self.token = kwargs.get('token', 'error')
        self.ticker = kwargs.get('ticker', 'error')
        self.api_data = self._api_data()

    def _api_data(self):
        return requests.get(f'https://api.gurufocus.com/public/user/{str(self.token)}/stock/{str(self.ticker)}/financials').json()


class GuruStockAnnualTenK:

    def __init__(self, **kwargs):
        self.token = kwargs.get('token', 'error')
        self.ticker = kwargs.get('ticker', 'error')
        self.api_data = self._api_data()
        self.api_data_type = type(self.api_data)
        self.aesop_fin_df = self._aesop_normalized()
        self.aesop_pershare_df = self._aesop_pershare()


    def _api_data(self):
        fin_data_json = requests.get(f'https://api.gurufocus.com/public/user/{str(self.token)}/stock/{str(self.ticker)}/financials').json()
        an_df1 = pd.DataFrame.from_dict(fin_data_json)
        an_df2 = pd.json_normalize(an_df1.loc['annuals'])
        x_loc = 0
        an_df3 = pd.DataFrame()

        for item, values in an_df2.items():
            series_expand = pd.Series(values, name=item).explode(ignore_index=True)
            series_df = series_expand.to_frame()
            an_df3 = pd.concat([an_df3, series_df], axis=1)
            x_loc += 1

        return an_df3


    def _aesop_normalized(self):
        df1 = self.api_data
        df2 = pd.DataFrame()

        # Build New Dataframe with Normalized Column names

        if any(df1.columns == 'Fiscal Year'):
            df2['fiscal_year'] = df1['Fiscal Year']

        # Income Statement Items

        if any(df1.columns == 'income_statement.Revenue'):
            df2['revenue'] = df1['income_statement.Revenue']

        if any(df1.columns == 'income_statement.Gross Profit'):
            df2['gross_profit'] = df1['income_statement.Gross Profit']

        if any(df1.columns == 'income_statement.Operating Income'):
            df2['operating_income'] = df1['income_statement.Operating Income']

        if any(df1.columns == 'income_statement.Tax Provision'):
            df2['taxes_paid'] = df1['income_statement.Tax Provision']

        if any(df1.columns == 'income_statement.Net Income'):
            df2['net_income'] = df1['income_statement.Net Income']


        # Balance Sheet Items

        if any(df1.columns == 'balance_sheet.Cash and Cash Equivalents'):
            df2['cash_equivalents'] = df1['balance_sheet.Cash and Cash Equivalents']

        if any(df1.columns == 'balance_sheet.Marketable Securities'):
            df2['market_securites'] = df1['balance_sheet.Marketable Securities']

        if any(df1.columns == 'balance_sheet.Total Current Assets'):
            df2['current_assets'] = df1['balance_sheet.Total Current Assets']

        if any(df1.columns == 'balance_sheet.Total Long-Term Assets'):
            df2['long_assets'] = df1['balance_sheet.Total Long-Term Assets']

        if any(df1.columns == 'balance_sheet.Short-Term Debt'):
            df2['short_debt'] = df1['balance_sheet.Short-Term Debt']

        if any(df1.columns == 'balance_sheet.Total Current Liabilities'):
            df2['current_liabilities'] = df1['balance_sheet.Total Current Liabilities']

        if any(df1.columns == 'balance_sheet.Long-Term Debt'):
            df2['long_debt'] = df1['balance_sheet.Long-Term Debt']

        if any(df1.columns == 'balance_sheet.Total Long-Term Liabilities'):
            df2['long_liabilities'] = df1['balance_sheet.Total Long-Term Liabilities']

        if any(df1.columns == 'balance_sheet.Treasury Stock'):
            df2['treasury_stock'] = df1['balance_sheet.Treasury Stock']

        if any(df1.columns == 'income_statement.Shares Outstanding (Diluted Average)'):
            df2['shares_outstanding_diluted'] = df1['income_statement.Shares Outstanding (Diluted Average)']

        if any(df1.columns == 'valuation_and_quality.Shares Outstanding (EOP)'):
            df2['shares_outstanding_eop'] = df1['valuation_and_quality.Shares Outstanding (EOP)']


        # Cash Flow Statement Items

        if any(df1.columns == 'cashflow_statement.Cash Flow from Operations'):
            df2['cash_from_ops'] = df1['cashflow_statement.Cash Flow from Operations']

        if any(df1.columns == 'cashflow_statement.FFO'):
            df2['funds_from_ops'] = df1['cashflow_statement.FFO']

        if any(df1.columns == 'cashflow_statement.Cash Flow for Dividends'):
            df2['cash_for_dividends'] = df1['cashflow_statement.Cash Flow for Dividends']

        if any(df1.columns == 'cashflow_statement.Capital Expenditure'):
            df2['capex'] = df1['cashflow_statement.Capital Expenditure']

        if any(df1.columns == 'cashflow_statement.Free Cash Flow'):
            df2['free_cash_flow'] = df1['cashflow_statement.Free Cash Flow']

        if any(df1.columns == 'cashflow_statement.Issuance of Stock'):
            df2['stock_issues'] = df1['cashflow_statement.Issuance of Stock']

        if any(df1.columns == 'cashflow_statement.Repurchase of Stock'):
            df2['stock_buyback'] = df1['cashflow_statement.Repurchase of Stock']


        # Drop TTM Data
        df2 = df2.loc[df2['fiscal_year'] != 'TTM']

        # Normalize Fiscal Year
        fy_pattern = r"([\d]{4})-"
        month_pattern = r"-([\d]{2})"

        df2['fiscal_year'] = df1['Fiscal Year'].str.extract(fy_pattern)
        df2['fiscal_month'] = df1['Fiscal Year'].str.extract(month_pattern)

        return df2


    def _aesop_pershare(self):

        df1 = self.api_data
        df2 = pd.DataFrame()

        # Build New Dataframe with Normalized Column names

        if any(df1.columns == 'Fiscal Year'):
            df2['fiscal_year'] = df1['Fiscal Year']

        if any(df1.columns == 'per_share_data_array.Revenue per Share'):
            df2['pershare_revenue'] = df1['per_share_data_array.Revenue per Share']

        if any(df1.columns == 'per_share_data_array.Earnings per Share (Diluted)'):
            df2['pershare_earnings'] = df1['per_share_data_array.Earnings per Share (Diluted)']

        if any(df1.columns == 'per_share_data_array.Dividends per Share'):
            df2['pershare_dividends'] = df1['per_share_data_array.Dividends per Share']

        if any(df1.columns == 'per_share_data_array.Free Cash Flow per Share'):
            df2['pershare_fcf'] = df1['per_share_data_array.Free Cash Flow per Share']

        if any(df1.columns == 'per_share_data_array.FFO per Share'):
            df2['pershare_ffo'] = df1['per_share_data_array.FFO per Share']

        # Drop TTM Data
        df2 = df2.loc[df2['fiscal_year'] != 'TTM']

        # Normalize Fiscal Year
        fy_pattern = r"([\d]{4})-"
        month_pattern = r"-([\d]{2})"

        df2['fiscal_year'] = df1['Fiscal Year'].str.extract(fy_pattern)
        df2['fiscal_month'] = df1['Fiscal Year'].str.extract(month_pattern)

        return df2


