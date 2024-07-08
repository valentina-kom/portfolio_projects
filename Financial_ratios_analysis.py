import pandas as pd
import requests
import matplotlib.pyplot as plt

#function to get company data from EDGAR
def fetch_company_data(ticker, headers):
    companyTickers = requests.get("https://www.sec.gov/files/company_tickers.json", headers=headers)
    companyCIK = pd.DataFrame.from_dict(companyTickers.json(), orient='index')
    companyCIK['cik_str'] = companyCIK['cik_str'].astype(str).str.zfill(10)
    cik = companyCIK[companyCIK['ticker'].str.lower() == ticker.lower()]['cik_str'].iloc[0]
    companyData = requests.get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json", headers=headers)
    return companyData.json()

#Filter for annual data, convert dates to datetime, get one row of most recent data for the year
def filter_and_process(df, key_columns, date_columns, freq=['10-K', '10-K/A'], start_month=1, end_month=12):
    for date_column in date_columns:
        if date_column in df.columns:
            df[date_column] = pd.to_datetime(df[date_column])
    
    df_filtered = df[df['form'].isin(freq)]
    
    if 'start' in df.columns:
        df_filtered = df_filtered[
            (df_filtered['start'].dt.month == start_month) &
            (df_filtered['end'].dt.month == end_month) &
            (df_filtered['start'].dt.year == df_filtered['end'].dt.year)
        ]
    else:
        df_filtered = df_filtered[
            (df_filtered['end'].dt.month == end_month)
        ]
    
    df_sorted = df_filtered.sort_values(by=key_columns, ascending=[False, False])
    df_unique = df_sorted.drop_duplicates(subset='end', keep='first').reset_index(drop=True)
    return df_unique

def process_company(ticker, headers):
    # Fetch company data
    company_data = fetch_company_data(ticker, headers)
    
    # Initialize DataFrame to store the results
    ratios_df = pd.DataFrame()
    
    # Define a list of columns that are not needed for the analysis
    columns_to_drop = ['fp', 'filed', 'frame', 'form', 'accn', 'fy']

    # Helper function to process each financial metric
    def process_metric(metric_key, rename_to, alternative_key=None):
        # Check if the metric key exists, if not and there is an alternative, use it
        if metric_key not in company_data['facts']['us-gaap']:
            if alternative_key and alternative_key in company_data['facts']['us-gaap']:
                metric_key = alternative_key
            else:
                print(f"Data for {metric_key} not found, even in alternative key.")
                return pd.DataFrame()

        df = filter_and_process(
            pd.DataFrame(company_data['facts']['us-gaap'][metric_key]['units']['USD']).rename(columns={"val": rename_to}),
            ['end', 'filed'], ['end', 'filed', 'start']
        )
        return df.drop(columns=[col for col in columns_to_drop if col in df.columns], errors='ignore')

    # Process financial metrics and drop unnecessary columns
    net_income_df = process_metric("NetIncomeLoss", "net_income")
    shareholders_equity_df = process_metric("StockholdersEquity", "s_equity")
    current_assets_df = process_metric("AssetsCurrent", "current_assets")
    current_liabilities_df = process_metric("LiabilitiesCurrent", "current_liabilities")
    inventories_df = process_metric("InventoryNet", "inventories")
    
    # Process Revenue - handle the case for 2022 specifically
    revenue_df_standard = process_metric("Revenues", "revenue")
    revenue_df_alternative = process_metric("RevenueFromContractWithCustomerExcludingAssessedTax", "revenue")

    # Combine revenue data, prioritizing standard revenue, but filling in with alternative where standard is missing
    revenue_df = pd.concat([revenue_df_standard, revenue_df_alternative]).groupby('end').first().reset_index()
    
    total_liabilities_df = process_metric("Liabilities", "total_liabilities")

    # Merging DataFrames for ratio calculations
    merged_df = pd.merge(net_income_df, shareholders_equity_df, on="end", how="outer")
    data_frames = [current_assets_df, current_liabilities_df, inventories_df, revenue_df, total_liabilities_df]
    for df in data_frames:
        merged_df = pd.merge(merged_df, df, on="end", how="inner")

    # Calculate financial ratios
    merged_df['Current_Ratio'] = merged_df['current_assets'] / merged_df['current_liabilities']
    merged_df['Quick_Ratio'] = (merged_df['current_assets'] - merged_df['inventories']) / merged_df['current_liabilities']
    merged_df['Net_Profit_Margin'] = merged_df['net_income'] / merged_df['revenue']
    merged_df['ROE'] = merged_df['net_income'] / merged_df['s_equity']
    merged_df['Debt_to_Equity_Ratio'] = merged_df['total_liabilities'] / merged_df['s_equity']
    
    # Add company identifier
    merged_df['company'] = ticker.upper()
    
    # Select relevant columns
    final_columns = ['company', 'end', 'Current_Ratio', 'Quick_Ratio', 'Net_Profit_Margin', 'ROE', 'Debt_to_Equity_Ratio']
    merged_df = merged_df[final_columns]
    
    return merged_df


# Define constants
HEADERS = {"User-Agent": "vkomarova@seattleu.edu"}

# Define the tickers 
tickers = ['TSLA', 'GOOG']  

# Initialize an empty DataFrame to store the combined results in wide format
wide_format_results = None

for ticker in tickers:
    company_results = process_company(ticker, HEADERS)
    
    company_results = company_results.drop(columns=['company'])
    company_results = company_results.rename(lambda x: x if x == 'end' else f"{x}_{ticker}", axis='columns')
    
    if wide_format_results is None:
        wide_format_results = company_results
    else:
        wide_format_results = pd.merge(
            wide_format_results, 
            company_results, 
            on="end", 
            how="inner"
        )

# Display the combined results in wide format
print(wide_format_results)
#wide_format_results.to_csv('Midretm_ratios.csv')


wide_format_results['end'] = pd.to_datetime(wide_format_results['end'])


# Define a list of ratios for plotting
ratios_to_plot = ['Current_Ratio', 'Quick_Ratio', 'Net_Profit_Margin', 'ROE', 'Debt_to_Equity_Ratio']

# Loop through each ratio and create a separate plot
for ratio in ratios_to_plot:
    plt.figure(figsize=(10, 6))
    
    # Extract data for Google and Tesla for the ratio that is being plotted
    google_data = wide_format_results[['end', f'{ratio}_GOOG']]
    tesla_data = wide_format_results[['end', f'{ratio}_TSLA']]
    
    # Plot Google's ratio
    plt.plot(google_data['end'], google_data[f'{ratio}_GOOG'], label='Google', marker='o')
    
    # Plot Tesla's ratio
    plt.plot(tesla_data['end'], tesla_data[f'{ratio}_TSLA'], label='Tesla', marker='o')
    
    # Add labels and title
    plt.xlabel('Year-End Date')
    plt.ylabel(ratio)
    plt.title(f'{ratio} Comparison: Google vs. Tesla')
    
    # Add legend
    plt.legend()
    
    # Show grid lines
    plt.grid(True)
    
    # Save the plot as an image 
   # plt.savefig(f'{ratio}_comparison.png', bbox_inches='tight')
    
    # Show the plot
    plt.show()
