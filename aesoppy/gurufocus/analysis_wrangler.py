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
        dy_df1 = self.div_yield_analysis_cy

        dy_df2 = dy_df1.groupby(dy_df1.index.year).agg(
            {'SharePrice': ['min', 'max', 'mean', 'median'],
             'FwdDivYield': ['min', 'max', 'mean', 'median'],
             'Dividend': ['sum']})

        return dy_df2


class AnnualFinAnalysis:
    def __init__(self, **kwargs):
        self.token = kwargs.get('token', 'error')
        self.ticker = kwargs.get('ticker', 'error')
        self.analysis_raw_data = gf.Financials(token=self.token, ticker=self.ticker).annual_data
        self.analysis_raw_data_reit = gf.Financials(token=self.token, ticker=self.ticker).reit
        self.analysis_norm_data = self._analysis_data_normalization()
        self.analysis_fy_cash_flow = self._analysis_fy_cash_flow()
        self.analysis_fy_cost_flow = self._analysis_fy_cost_flow()
        self.analysis_fy_debt = self._analysis_fy_debt()
        self.analysis_fy_owner = self._analysis_fy_owner()
        self.analysis_fy_growth = self._analysis_fy_growth()
        self.analysis_per_share = self._analysis_fy_pershare()




    def _analysis_data_normalization(self):
        fy_df1 = self.analysis_raw_data
        fy_pattern = r"([\d]{4})-"
        month_pattern = r"-([\d]{2})"

        # Drop TTM Data
        fy_df1 = fy_df1.loc[fy_df1['Fiscal Year'] != 'TTM']

        fy_df1['FiscalYear'] = fy_df1['Fiscal Year'].str.extract(fy_pattern)
        fy_df1['FyMonthEnd'] = fy_df1['Fiscal Year'].str.extract(month_pattern)

        fy_df1.set_index('FiscalYear', inplace=True)

        # Create Normalized DataFrame
        fy_df2 = pd.DataFrame(index=fy_df1.index)

        if any(fy_df1.columns == 'income_statement.Revenue'):
            fy_df2['Revenue'] = fy_df1['income_statement.Revenue'].astype(float)
        else:
            fy_df2 # Do Nothing

        if any(fy_df1.columns == 'income_statement.Cost of Goods Sold'):
            fy_df2['COGS'] = fy_df1['income_statement.Cost of Goods Sold'].astype(float)
        else:
            fy_df2 # Do Nothing

        if any(fy_df1.columns == 'income_statement.Gross Profit'):
            fy_df2['GrossProfit'] = fy_df1['income_statement.Gross Profit'].astype(float)
        else:
            fy_df2 # Do Nothing

        if any(fy_df1.columns == 'income_statement.Selling, General, & Admin. Expense'):
            fy_df2['SGA'] = fy_df1['income_statement.Selling, General, & Admin. Expense'].astype(float)
        else:
            fy_df2 # Do Nothing

        if any(fy_df1.columns == 'income_statement.Research & Development'):
            fy_df2['RND'] = fy_df1['income_statement.Research & Development'].astype(float)
        else:
            fy_df2 # Do Nothing

        if any(fy_df1.columns == 'income_statement.Total Operating Expense'):
            fy_df2['OperatingExpense'] = fy_df1['income_statement.Total Operating Expense'].astype(float)
        else:
            fy_df2 # Do Nothing

        if any(fy_df1.columns == 'income_statement.Operating Income'):
            fy_df2['OperatingIncome'] = fy_df1['income_statement.Operating Income'].astype(float)
        else:
            fy_df2 # Do Nothing

        if any(fy_df1.columns == 'income_statement.Tax Provision'):
            fy_df2['TaxPaid'] = fy_df1['income_statement.Tax Provision'].astype(float)
        else:
            fy_df2 # Do Nothing

        if any(fy_df1.columns == 'income_statement.Net Income'):
            fy_df2['NetIncome'] = fy_df1['income_statement.Net Income'].astype(float)
        else:
            fy_df2 # Do Nothing

        if any(fy_df1.columns == 'balance_sheet.Cash and Cash Equivalents'):
            fy_df2['CashEquivalents'] = fy_df1['balance_sheet.Cash and Cash Equivalents'].astype(float)
        else:
            fy_df2 # Do Nothing

        if any(fy_df1.columns == 'balance_sheet.Marketable Securities'):
            fy_df2['MarketSecurities'] = fy_df1['balance_sheet.Marketable Securities'].astype(float)
        else:
            fy_df2 # Do Nothing

        if any(fy_df1.columns == 'balance_sheet.Total Current Assets'):
            fy_df2['CurrentAssets'] = fy_df1['balance_sheet.Total Current Assets'].astype(float)
        else:
            fy_df2 # Do Nothing

        if any(fy_df1.columns == 'balance_sheet.Total Long-Term Assets'):
            fy_df2['LongAssets'] = fy_df1['balance_sheet.Total Long-Term Assets'].astype(float)
        else:
            fy_df2 # Do Nothing

        if any(fy_df1.columns == 'balance_sheet.Total Current Liabilities'):
            fy_df2['CurrentLiabilities'] = fy_df1['balance_sheet.Total Current Liabilities'].astype(float)
        else:
            fy_df2 # Do Nothing

        if any(fy_df1.columns == 'balance_sheet.Total Long-Term Liabilities'):
            fy_df2['LongLiabilities'] = fy_df1['balance_sheet.Total Long-Term Liabilities'].astype(float)
        else:
            fy_df2 # Do Nothing

        if any(fy_df1.columns == 'balance_sheet.Treasury Stock'):
            fy_df2['TreasuryStock'] = fy_df1['balance_sheet.Treasury Stock'].astype(float)
        else:
            fy_df2 # Do Nothing

        if any(fy_df1.columns == 'balance_sheet.Common Stock'):
            fy_df2['CommonStock'] = fy_df1['balance_sheet.Common Stock'].astype(float)
        else:
            fy_df2 # Do Nothing

        if any(fy_df1.columns == 'cashflow_statement.Cash Flow from Operations'):
            fy_df2['CashFromOperations'] = fy_df1['cashflow_statement.Cash Flow from Operations'].astype(float)
        else:
            fy_df2 # Do Nothing

        if any(fy_df1.columns == 'cashflow_statement.Cash Flow for Dividends'):
            fy_df2['CashForDividends'] = fy_df1['cashflow_statement.Cash Flow for Dividends'].astype(float)
        else:
            fy_df2 # Do Nothing

        if any(fy_df1.columns == 'cashflow_statement.Capital Expenditure'):
            fy_df2['CAPEX'] = fy_df1['cashflow_statement.Capital Expenditure'].astype(float)
        else:
            fy_df2 # Do Nothing

        if any(fy_df1.columns == 'cashflow_statement.Free Cash Flow'):
            fy_df2['FreeCashFlow'] = fy_df1['cashflow_statement.Free Cash Flow'].astype(float)
        else:
            fy_df2 # Do Nothing

        if any(fy_df1.columns == 'cashflow_statement.Payments of Debt'):
            fy_df2['CashPaidToDebt'] = fy_df1['cashflow_statement.Payments of Debt'].astype(float)
        else:
            fy_df2 # Do Nothing

        if any(fy_df1.columns == 'cashflow_statement.Issuance of Stock'):
            fy_df2['StockIssuance'] = fy_df1['cashflow_statement.Issuance of Stock'].astype(float)
        else:
            fy_df2 # Do Nothing

        if any(fy_df1.columns == 'cashflow_statement.Repurchase of Stock'):
            fy_df2['StockRepurchase'] = fy_df1['cashflow_statement.Repurchase of Stock'].astype(float)
        else:
            fy_df2 # Do Nothing

        if any(fy_df1.columns == 'valuation_and_quality.Market Cap'):
            fy_df2['MarketCap'] = fy_df1['valuation_and_quality.Market Cap'].astype(float)
        else:
            fy_df2 # Do Nothing

        if any(fy_df1.columns == 'valuation_and_quality.Highest Stock Price'):
            fy_df2['StockPriceHigh'] = fy_df1['valuation_and_quality.Highest Stock Price'].astype(float)
        else:
            fy_df2 # Do Nothing

        if any(fy_df1.columns == 'valuation_and_quality.Lowest Stock Price'):
            fy_df2['StockPriceLow'] = fy_df1['valuation_and_quality.Lowest Stock Price'].astype(float)
        else:
            fy_df2 # Do Nothing

        if any(fy_df1.columns == 'income_statement.Shares Outstanding (Diluted Average)'):
            fy_df2['SharesOutDiluted'] = fy_df1['income_statement.Shares Outstanding (Diluted Average)'].astype(float)
        else:
            fy_df2 # Do Nothing

        if any(fy_df1.columns == 'valuation_and_quality.Shares Outstanding (Basic Average)'):
            fy_df2['SharesOutBasic'] = fy_df1['valuation_and_quality.Shares Outstanding (Basic Average)'].astype(float)
        else:
            fy_df2 # Do Nothing

        if any(fy_df1.columns == 'per_share_data_array.Revenue per Share'):
            fy_df2['PerShareRevenue'] = fy_df1['per_share_data_array.Revenue per Share'].astype(float)
        else:
            fy_df2 # Do Nothing

        if any(fy_df1.columns == 'per_share_data_array.Earnings per Share (Diluted)'):
            fy_df2['PerShareEpsDiluted'] = fy_df1['per_share_data_array.Earnings per Share (Diluted)'].astype(float)
        else:
            fy_df2 # Do Nothing

        if any(fy_df1.columns == 'per_share_data_array.Earnings per Share (Diluted)'):
            fy_df2['PerShareEpsDiluted'] = fy_df1['per_share_data_array.Earnings per Share (Diluted)'].astype(float)
        else:
            fy_df2 # Do Nothing

        if any(fy_df1.columns == 'per_share_data_array.Dividends per Share'):
            fy_df2['PerShareDividends'] = fy_df1['per_share_data_array.Dividends per Share'].astype(float)
        else:
            fy_df2 # Do Nothing

        if any(fy_df1.columns == 'per_share_data_array.Free Cash Flow per Share'):
            fy_df2['PerShareFcf'] = fy_df1['per_share_data_array.Free Cash Flow per Share'].astype(float)
        else:
            fy_df2 # Do Nothing

        if any(fy_df1.columns == 'per_share_data_array.Earnings per Share (Diluted)'):
            fy_df2['PerShareEarnings'] = fy_df1['per_share_data_array.Earnings per Share (Diluted)'].astype(float)
        else:
            fy_df2 # Do Nothing

        return fy_df2

    def _analysis_fy_cash_flow(self):
        cash_df1 = self.analysis_norm_data
        cash_df2 = pd.DataFrame(index=cash_df1.index)

        cash_df2 = cash_df1[['Revenue', 'GrossProfit', 'OperatingIncome', 'NetIncome', 'CashFromOperations',
                             'FreeCashFlow']]

        return cash_df2

    def _analysis_fy_cost_flow(self):
        cost_df1 = self.analysis_norm_data
        cost_df2 = pd.DataFrame(index=cost_df1.index)

        cost_df2 = cost_df1[['Revenue', 'COGS', 'SGA', 'RND', 'OperatingExpense',
                             'TaxPaid', 'CAPEX']]

        return cost_df2

    def _analysis_fy_debt(self):
        debt_df1 = self.analysis_norm_data
        debt_df2 = pd.DataFrame(index=debt_df1.index)

        debt_df2 = debt_df1[['Revenue', 'CashFromOperations', 'FreeCashFlow', 'CashEquivalents', 'MarketSecurities',
                             'TreasuryStock', 'CurrentAssets', 'LongAssets', 'CurrentLiabilities', 'LongLiabilities',
                             'CashPaidToDebt']]

        return debt_df2

    def _analysis_fy_owner(self):
        owner_df1 = self.analysis_norm_data
        owner_df2 = pd.DataFrame(index=owner_df1.index)

        owner_df2 = owner_df1[['Revenue', 'FreeCashFlow', 'CashEquivalents', 'MarketSecurities',
                               'TreasuryStock', 'CashForDividends', 'StockIssuance', 'StockRepurchase']]

        return owner_df2

    def _analysis_fy_growth(self):
        growth_df1 = self.analysis_norm_data
        growth_df2 = pd.DataFrame(index=growth_df1.index)

        growth_df2 = growth_df1[['Revenue', 'CashEquivalents', 'MarketSecurities', 'SharesOutBasic', 'SharesOutDiluted',
                                 'CashForDividends']]

        return growth_df2

    def _analysis_fy_pershare(self):
        ps_df1 = self.analysis_norm_data
        ps_df2 = pd.DataFrame(index=ps_df1.index)

        ps_df2 = ps_df1[['PerShareRevenue', 'PerShareEarnings', 'PerShareFcf', 'PerShareDividends',
                         'StockPriceHigh', 'StockPriceLow']]

        return ps_df2













