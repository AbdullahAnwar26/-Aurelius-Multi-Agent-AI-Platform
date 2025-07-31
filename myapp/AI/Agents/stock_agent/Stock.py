def get_sample_stock_data(query:str):
    """
    This is a mock version of get_stock_data() returning static analysis.
    Later, it can be updated to fetch live data using Yahoo Finance or similar APIs.

    Parameters:
        query (str): A natural language query like "which stock should I buy Stock_1 or Stock_2?"

    Returns:
        Investment report and visualization file path.
    """

    # response generated using different agents
    response = """
    # Final Investment Report:

    ## Summary of Stock Performance
    The 6-month performance of the given stocks is as follows:
    * NVDA has a 14.75% change,
    * GOOG has a -7.27% change,
    * TSLA has a -22.47% change.

    ## Key Company Insights
    * *GOOG*: Alphabet Inc. is a leading company in the Communication Services sector, with a market cap of over 2 trillion USD, operating through various segments including Google Services, Google Cloud, and Other Bets.
    * *NVDA*: NVIDIA Corporation is a technology company providing graphics and compute and networking solutions, with a market cap of 3847144079360, headquartered in Santa Clara, California.
    * *TSLA*: Tesla, Inc. is a leading player in the electric vehicle and clean energy industries, with a market capitalization of over $1 trillion, offering a diversified range of products and services.

    ## Risk–Reward Assessment
    The risk-reward assessment is partially hindered by the lack of recent news headlines for the companies. However, based on the available data, NVDA appears to have a strong position in the technology industry, while GOOG and TSLA have negative 6-month performances.

    ## Final Recommendation
    Based on the data, *NVDA* is the top recommended stock to invest in, due to its highest 6-month performance and strong position in the technology industry.  

    ### Stock Ranking
    NVDA > GOOG > TSLA
"""

    # path of the plot
    Plot = r"C:\\Users\\devra\\Desktop\\AI\\Agents\\stock_agent\\stock_performance_plot.png"
    
    return response, Plot