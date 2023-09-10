from typing import List, Optional
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from datetime import datetime
import random
import uuid
from faker import Faker

app = FastAPI()

fake = Faker()

# Mocked database
class TradeDB:
    def __init__(self):
        self.trades = []

    def add_trade(self, trade):
        """
        Add a trade to the database.

        Args:
            trade (Trade): The trade object to add.
        """
        self.trades.append(trade)

    def get_trade_by_id(self, trade_id):
        """
        Retrieve a trade by its ID.

        Args:
            trade_id (str): The ID of the trade to retrieve.

        Returns:
            Trade: The trade object if found, None otherwise.
        """
        for trade in self.trades:
            if trade.trade_id == trade_id:
                return trade
        return None

    def search_trades(self, query):
        """
        Search trades based on a query.

        Args:
            query (str): The search query.

        Returns:
            List[Trade]: List of trades matching the query.
        """
        query_lower = query.lower()
        result = []
        for trade in self.trades:
            if (
                query_lower in trade.instrument_id.lower()
                or query_lower in trade.instrument_name.lower()
                or query_lower in trade.counterparty.lower()
                or query_lower in trade.trader.lower()
            ):
                result.append(trade)
        return result

    def filter_trades(
        self,
        asset_classes=None,
        start=None,
        end=None,
        min_price=None,
        max_price=None,
        trade_type=None,
    ):
        """
        Filter trades based on optional parameters.

        Args:
            asset_classes (List[str]): List of asset classes to filter by.
            start (datetime): Minimum trade date-time.
            end (datetime): Maximum trade date-time.
            min_price (float): Minimum trade price.
            max_price (float): Maximum trade price.
            trade_type (str): Trade type (BUY or SELL).

        Returns:
            List[Trade]: List of filtered trades.
        """
        result = []
        for trade in self.trades:
            if (
                (asset_classes is None or trade.asset_class in asset_classes)
                and (start is None or trade.trade_date_time >= start)
                and (end is None or trade.trade_date_time <= end)
                and (min_price is None or trade.trade_details.price >= min_price)
                and (max_price is None or trade.trade_details.price <= max_price)
                and (trade_type is None or trade.trade_details.buySellIndicator == trade_type)
            ):
                result.append(trade)
        return result

class TradeDetails(BaseModel):
    buySellIndicator: str
    price: float
    quantity: int

class Trade(BaseModel):
    asset_class: Optional[str] = None
    counterparty: Optional[str] = None
    instrument_id: str
    instrument_name: str
    trade_date_time: datetime
    trade_details: TradeDetails
    trade_id: Optional[str] = None
    trader: str

def generate_random_trade_id():
    """
    Generate a random trade ID using UUID.

    Returns:
        str: The generated trade ID.
    """
    return str(uuid.uuid4())

def generate_random_trades(num_trades):
    """
    Generate random trade data.

    Args:
        num_trades (int): Number of random trades to generate.

    Returns:
        List[Trade]: List of randomly generated trades.
    """
    asset_classes = [
        "Equities (Stocks)",
        "Fixed Income (Bonds)",
        "Cash and Cash Equivalents",
        "Real Estate Investment Trusts (REITs)",
        "Alternative Investments",
        "Foreign Exchange (Forex)",
        "Cryptocurrencies",
        "Private Equity",
        "Venture Capital",
        "Collectibles and Tangible Assets",
        "Infrastructure Investments",
        "Emerging Markets",
        "Precious Metals",
        "Government Bonds",
        "Corporate Bonds",
        "Convertible Bonds",
        "Mortgage-Backed Securities (MBS)",
        "Energy Commodities",
        "Agricultural Commodities",
        "Industrial Metals",
        "Environmental, Social, and Governance (ESG) Investments"
    ]
    counterparties = ["Counterparty1", "Counterparty2", "Counterparty3", "Counterparty4", "Counterparty5"]
    instruments = [
        "TSLA (Tesla, Inc. stock)",
        "GOOG (Alphabet Inc. stock)",
        "AMZN (Amazon.com, Inc. stock)",
        "AAPL (Apple Inc. stock)",
        "FB (Meta Platforms, Inc. stock)",
        "MSFT (Microsoft Corporation stock)",
        "Amazon (AMZN stock)",
        "Tesla (TSLA stock)",
        "Alibaba Group Holding Ltd (BABA stock)",
        "NASDAQ Composite Index (Equity Index)",
        "Dow Jones Industrial Average (Equity Index)",
        "EURUSD (Euro/US Dollar forex pair)",
        "EURGBP (Euro/British Pound forex pair)",
        "USDJPY (US Dollar/Japanese Yen forex pair)",
        "GBPUSD (British Pound/US Dollar forex pair)",
        "EURJPY (Euro/Japanese Yen forex pair)",
        "AUDUSD (Australian Dollar/US Dollar forex pair)",
        "GOLD (Gold commodity)",
        "SILVER (Silver commodity)",
        "NATGAS (Natural Gas commodity)",
        "WTI Crude Oil (OIL commodity)",
        "Bitcoin (BTC cryptocurrency)",
        "Ethereum (ETH cryptocurrency)",
        "Ripple (XRP cryptocurrency)",
        "Bonds (Fixed Income)",
        "10-Year US Treasury Note (Government Bond)",
        "30-Year US Treasury Bond (Government Bond)",
        "Cryptocurrencies",
        "Stocks (Equities)"
    ]
    buy_sell_indicators = ["BUY", "SELL"]

    random_trades = []

    # Ensure at least one trader has the name "John Smith"
    has_john_smith = False

    for _ in range(num_trades):
        if not has_john_smith and random.randint(0, 1) == 0:
            # Generate a trade with the name "John Smith"
            trader_name = "John Smith"
            has_john_smith = True
        else:
            # Generate a random name using Faker
            trader_name = fake.name()

        trade = Trade(
            asset_class=random.choice(asset_classes),
            counterparty=random.choice(counterparties),
            instrument_id=random.choice(instruments),
            instrument_name="Random Instrument",
            trade_date_time=datetime.now(),
            trade_details=TradeDetails(
                buySellIndicator=random.choice(buy_sell_indicators),
                price=random.uniform(50, 5000),
                quantity=random.randint(1, 1000),
            ),
            trader=trader_name,
            trade_id=generate_random_trade_id(),
        )
        random_trades.append(trade)

    return random_trades

# Create an instance of TradeDB
trade_db = TradeDB()

# Add random trades to the TradeDB
num_random_trades = 10
random_trades = generate_random_trades(num_random_trades)
for trade in random_trades:
    trade_db.add_trade(trade)

# Combined endpoint to list trades with filtering and pagination
@app.get("/trades/", response_model=List[Trade])
async def list_trades(
    asset_classes: Optional[str] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    trade_type: Optional[str] = None,
    trader: Optional[str] = None,
    page: int = Query(1, description="Page number for pagination"),
    page_size: int = Query(10, description="Number of trades per page"),
    sort_by: List[str] = Query(["trade_date_time"], description="Fields to sort by (default is trade_date_time)"),
    search: Optional[str] = None,
    exclude_traders: Optional[List[str]] = Query([], description="List of traders to exclude")
):
    # Search trades
    if search:
        filtered_trades = trade_db.search_trades(search)
    else:
        filtered_trades = trade_db.trades

    # Apply filters
    filtered_trades = trade_db.filter_trades(
        asset_classes, start, end, min_price, max_price, trade_type
    )

    # Filter out trades with specified traders to exclude
    filtered_trades = [trade for trade in filtered_trades if trade.trader not in exclude_traders]

    # Filter trades by specific trader if trader parameter is provided
    if trader:
        filtered_trades = [trade for trade in filtered_trades if trade.trader == trader]

    # Sort trades
    sorted_trades = filtered_trades
    for field in sort_by:
        reverse_sort = field.startswith("-")
        sort_field = field.lstrip("-")
        sorted_trades = sorted(sorted_trades, key=lambda x: getattr(x, sort_field), reverse=reverse_sort)

    # Paginate trades
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    trades = sorted_trades[start_idx:end_idx]

    return trades

# Endpoint to get a single trade by ID
@app.get("/trades/{trade_id}", response_model=Trade)
async def get_trade_by_id(trade_id: str):
    trade = trade_db.get_trade_by_id(trade_id)
    if trade:
        return trade
    else:
        raise HTTPException(status_code=404, detail="Trade not found")

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
