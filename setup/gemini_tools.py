from vertexai.generative_models._generative_models import Tool, FunctionDeclaration

gemini_tools = Tool(function_declarations=[
    FunctionDeclaration(
        name="get_stock_price",
        description="Get the current stock price of a given company",
        parameters={
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Stock ticker symbol"
                }
            }
        },
    ),
    FunctionDeclaration(
        name="buy_or_sell",
        description="Make a decision on buying or selling a stock, given it's symbol and price",
        parameters={
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "The ticker symbol of the stock"
                },
                "price": {
                    "type": "string",
                    "description": "The price of the stock"
                }
            }
        },
    )
])
