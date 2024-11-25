import requests
from bs4 import BeautifulSoup as bs
import json
import click
import time
import yfinance as yf
from datetime import datetime

def get_stock_info_as_of_date(symbol, start_date, end_date, info):
    """retrieves stock info as of specific date provided"""
    # Load the ticker
    stock = yf.Ticker(symbol)

    result = dict()
    # Fetch historical data
    history = stock.history(start=start_date, end=end_date)

    # Extract data for the given date
    if start_date in history.index:
        row = history.loc[start_date]
        for key in info.keys():
            result[key] = round(row[info[key]], 2)
    else:
        return {"error": f"No data found for {symbol} on {start_date}"}
    
    return result

def get_stock_info(symbol, start_date=False, end_date=False):
    """uses the yahoo finance API to retrieve the current market price and previous close"""

    stock = yf.Ticker(symbol)
    info = {
        "current_price": "currentPrice",
        "day_low": "dayLow",
        "day_high": "dayHigh",
        "volume": "volume",
        "previous_close": "previousClose",
        "shares_short": "sharesShort",
    }
    result = dict()
    if not start_date and not end_date:
        
        for key in info.keys():
            result[key] = stock.info.get(info[key])
    else:
        info = {
            "current_price": "Close",
            "day_low": "Low",
            "day_high": "High",
            "volume": "Volume",
            "previous_close": "Open" # This could be a bug...
        }
        
        start_date = datetime.fromtimestamp(start_date).strftime("%Y-%m-%d")
        end_date = datetime.fromtimestamp(int(end_date) + 86401).strftime("%Y-%m-%d")

        result = get_stock_info_as_of_date(symbol, start_date, end_date, info)
    return result


def score_comments(comments_data, record_users=False):
    "Takes the data from conversation API and scores it returning a result object"

    result = dict(
        bears=0,
        bear_users=list(),
        bulls=0,
        bull_users=list(),
        neutral=0,
        score=0,
        oldest_comment_ts=None,
        newest_comment_ts=None,
    )
    for comment in comments_data:
        try:
            labels = comment["additional_data"]["labels"]["ids"]
        except:
            labels = list()

        if "BEARISH" in labels:
            if record_users:
                result['bear_users'].append(comment['user_id'])
            result["bears"] = result["bears"] + 1
        if "BULLISH" in labels:
            if record_users:
                result['bull_users'].append(comment['user_id'])
            result["bulls"] = result["bulls"] + 1
        if "BEARISH" not in labels and "BULLISH" not in labels:
            result["neutral"] = result["neutral"] + 1

        if (
            not result["oldest_comment_ts"]
            or comment["time"] < result["oldest_comment_ts"]
        ):
            result["oldest_comment_ts"] = comment["time"]

        if (
            not result["newest_comment_ts"]
            or comment["time"] > result["newest_comment_ts"]
        ):
            result["newest_comment_ts"] = comment["time"]

    try:
        result["oldest_comment_ts"] = datetime.fromtimestamp(
            result["oldest_comment_ts"]
        ).strftime("%Y-%m-%d %H:%M:%S")
        result["newest_comment_ts"] = datetime.fromtimestamp(
            result["newest_comment_ts"]
        ).strftime("%Y-%m-%d %H:%M:%S")
    except:
        pass

    result["score"] = result["bulls"] - result["bears"]

    return result


def get_conversation_info(symbol):
    url = f"https://finance.yahoo.com/quote/{symbol}/community"
    response = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0"
        },
    )
    soup = bs(response.text, features="html.parser")
    data = json.loads(soup.select_one("#spotim-config").get_text(strip=True))["config"]

    return data


def _get_comments_block(conversation_info, offset):
    url = "https://api-2-0.spot.im/v1.0.0/conversation/read"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0",
        "Content-Type": "application/json",
        "x-spot-id": conversation_info["spotId"],
        "x-post-id": conversation_info["uuid"].replace("_", "$"),
    }

    payload = json.dumps(
        {
            "conversation_id": conversation_info["spotId"]
            + conversation_info["uuid"].replace("_", "$"),
            "count": 100,
            "offset": offset,
        }
    )

    response = requests.post(url, headers=headers, data=payload)
    conversation_data = response.json()

    return conversation_data["conversation"]


def get_comment_data(
    conversation_info, start_date, end_date, offset, comments_data=list()
):
    conversation_data = _get_comments_block(conversation_info, offset)
    len_comments = len(conversation_data["comments"])
    i = 0
    for comment in conversation_data["comments"]:
        i += 1
        if comment["time"] >= end_date:
            pass
        if comment["time"] <= start_date:
            pass
        if comment["time"] >= start_date and comment["time"] <= end_date:
            comments_data.append(comment)
        if i == len_comments:
            if comment["time"] <= start_date:
                break
            if conversation_data["has_next"]:
                offset = offset + i
                conversation_data = get_comment_data(
                    conversation_info,
                    start_date,
                    end_date,
                    offset,
                    comments_data=comments_data,
                )
    return comments_data


def get_start_of_day(the_date=""):
    if not the_date:
        now = datetime.now()
        start_of_day = datetime(now.year, now.month, now.day, 0, 0, 0)
    else:
        try:
            start_of_day = datetime.strptime(the_date, "%Y-%m-%d")
            start_of_day = datetime(
                start_of_day.year, start_of_day.month, start_of_day.day, 0, 0, 0
            )
        except ValueError:
            raise ValueError(
                f"Invalid date format: {the_date}. Expected format: YYYY-MM-DD."
            )
    return int(start_of_day.timestamp())


def get_end_of_day(the_date=""):
    if not the_date:
        now = datetime.now()
        end_of_day = datetime(now.year, now.month, now.day, 23, 59, 59)
    else:
        try:
            end_of_day = datetime.strptime(the_date, "%Y-%m-%d")
            end_of_day = datetime(
                end_of_day.year, end_of_day.month, end_of_day.day, 23, 59, 59
            )
        except ValueError:
            raise ValueError(
                f"Invalid date format: {the_date}. Expected format: YYYY-MM-DD."
            )

    return int(end_of_day.timestamp())


@click.command()
@click.option("--symbol", default="QBTS", help="Symbol to score")
@click.option("--record_users", default=False, help="If True record the user ids of bulls and bears")
@click.option("--start_date", default="", help="Starting Date to check %Y-%m-%d; if blank uses today")
@click.option("--end_date", default="", help="Ending Date %Y-%m-%d; if blank use today")
def main(symbol, record_users, start_date, end_date):
    processing_start_time = time.time()

    start_date = get_start_of_day(start_date)

    end_date = get_end_of_day(end_date)

    conversation_data = get_conversation_info(symbol)

    comments_data = get_comment_data(conversation_data, start_date, end_date, offset=0)

    comment_result = score_comments(comments_data, record_users=record_users)
    price_result = get_stock_info(symbol, start_date=start_date, end_date=end_date)

    result = {**comment_result, **price_result}
    result["symbol"] = symbol
    result["start_date"] = start_date
    result["end_date"] = end_date
    result["processing_start_time"] = processing_start_time
    result["processing_end_time"] = int(time.time())

    print(json.dumps(result))

    return result


if __name__ == "__main__":
    main()
