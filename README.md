# Quick Start

1. Setup A python 3.8 virtualenv

   
    ```
    pip install virtualenv
    python -m venv .trading_data
    . .trading_data/bin/activate
    ```

2. Clone this repo locally

    ```
    git clone https://github.com/vonnetworking/trading_data.git
    cd trading_data
    ```

3. Install requirements

    ```
    pip install -r requirements.txt
    ```

4. Run the script tests and help to make sure its working

    ```
    python -m pytest
    python src/get_yahoo_comments.py --help
    ```

5. See examples below

### Run with defaults for a symbol (gets current days price and comment info)

```
python src/get_yahoo_comments.py --symbol=QBTS | jq               
{
  "bears": 1,
  "bear_users": [],
  "bulls": 10,
  "bull_users": [],
  "neutral": 5,
  "score": 9,
  "oldest_comment_ts": "2024-11-24 04:29:06",
  "newest_comment_ts": "2024-11-24 21:58:09",
  "current_price": 2.93,
  "day_low": 1.97,
  "day_high": 3,
  "volume": 80597290,
  "previous_close": 1.97,
  "shares_short": 16101927,
  "symbol": "QBTS",
  "start_date": 1732424400,
  "end_date": 1732510799,
  "processing_start_time": 1732510635.510057,
  "processing_end_time": 1732510637
}

```
### Run For a prior day 

```
python src/get_yahoo_comments.py --symbol=QBTS --start_date=2024-11-18 --end_date=2024-11-18 | jq
{
  "bears": 7,
  "bear_users": [],
  "bulls": 12,
  "bull_users": [],
  "neutral": 15,
  "score": 5,
  "oldest_comment_ts": "2024-11-18 06:51:44",
  "newest_comment_ts": "2024-11-18 19:44:08",
  "current_price": 1.44,
  "day_low": 1.41,
  "day_high": 1.67,
  "volume": 12548200,
  "previous_close": 1.66,
  "symbol": "QBTS",
  "start_date": 1731906000,
  "end_date": 1731992399,
  "processing_start_time": 1732510725.023048,
  "processing_end_time": 1732510729
}
```

### Add a list of bull and bear users in the output

```
python src/get_yahoo_comments.py --symbol=QBTS --record_users=True --start_date=2024-11-21 --end_date=2024-11-21 | jq
{
  "bears": 2,
  "bear_users": [
    "u_2EARYmES0GcV7LffXArpQpzbLfp",
    "u_CYLxbGal5th5"
  ],
  "bulls": 4,
  "bull_users": [
    "u_bgoe1qcR42ke",
    "u_7CXHwbLTTXKw",
    "u_bgoe1qcR42ke"
  ],
  "neutral": 23,
  "score": 39,
  "oldest_comment_ts": "2024-11-21 06:39:07",
  "newest_comment_ts": "2024-11-21 23:07:18",
  "current_price": 1.97,
  "day_low": 1.71,
  "day_high": 2.04,
  "volume": 33057500,
  "previous_close": 1.81,
  "symbol": "QBTS",
  "start_date": 1732165200,
  "end_date": 1732251599,
  "processing_start_time": 1732510920.0744278,
  "processing_end_time": 1732510924
}
```

### NOTE: the further back in history you go - especially for active securities, the longer the script will take to run

```
for DATE in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23; do
    python src/get_yahoo_comments.py --symbol=QBTS --start_date=2024-11-${DATE} --end_date=2024-11-${DATE}
done
```