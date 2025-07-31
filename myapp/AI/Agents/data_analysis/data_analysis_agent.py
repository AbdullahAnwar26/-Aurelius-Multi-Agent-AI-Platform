def sample_data_analysis_agent_response(nlp_query: str):
    """
    Simulated response from the Data Analysis Agent.
    Demonstrates the structure of the agent's output based on a natural language query.

    Args:
        nlp_query (str): The user's natural language query (e.g., "Generate me a plot")

    Returns:
        dict: A fixed sample output showing what the backend can expect
    """

    return {
            "analysis_summary": "Here are the first 2 rows of the dataset.",
            "generated_code": "df.head(2)",
            "plot_image_path": None,
            "dataframe_preview": [
                {"InvoiceNo": "536365", "StockCode": "85123A", "Description": "WHITE HANGING HEART", "Quantity": 6, "Price": 2.55},
                {"InvoiceNo": "536365", "StockCode": "71053", "Description": "WHITE METAL LANTERN", "Quantity": 6, "Price": 3.39}
            ]
        }

