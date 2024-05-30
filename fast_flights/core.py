from typing import Any, Optional
import requests
from selectolax.lexbor import LexborHTMLParser, LexborNode

from .flights_impl import TFSData
from .schema import Flight, Result
from .helper import *
import time

ua = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0"
)


def request_flights(tfs: TFSData, **kwargs: Any) -> requests.Response:
    try:
        r = requests.get(
            "https://www.google.com/travel/flights",
            params={
                "tfs": tfs.as_b64(),
                "hl": "en",
                "tfu": "EgQIABABIgA",  # show all flights and prices condition
            },
            headers={"user-agent": ua, "accept-language": "en"},
            **kwargs
        )
        r.raise_for_status()
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print(e)
        return -1
#     print("http time: ",r.elapsed.total_seconds())
    print(r)
    return r

def request_flights_http(tfs: TFSData, **kwargs: Any) -> requests.Response:
    r = requests.get(
        "https://www.google.com/travel/flights",
        params={
            "tfs": tfs.as_b64(),
            "hl": "en",
            "tfu": "EgQIABABIgA",  # show all flights and prices condition
        },
        headers={"user-agent": ua, "accept-language": "en"},
        **kwargs
    )
    r.raise_for_status()
    return r


def parse_response(r: requests.Response) -> Result:
    class _blank:
        def text(self, *_, **__):
            return ""

        def iter(self):
            return []

    blank = _blank()

    def safe(n: Optional[LexborNode]):
        return n or blank

    parser = LexborHTMLParser(r.text)
    flights = []

    for i, fl in enumerate(parser.css('div[jsname="IWWDBc"], div[jsname="YdtKid"]')):
        is_best_flight = i == 0

        for item in fl.css("ul.Rk10dc li")[:-1]:  # <-- last one would crash
            # Flight name
            name = safe(item.css_first("div.sSHqwe.tPgKwe.ogfYpf")).text(
                strip=True
            )
            name = process_name(name)

            # Get departure & arrival time
            dp_ar_node = item.css("span.mv1WYe div")
            departure_time = dp_ar_node[0].text(strip=True)
            arrival_time = dp_ar_node[1].text(strip=True)

            # Get arrival time ahead
            time_ahead = safe(item.css_first("span.bOzv6")).text()

            # Get duration
            duration = safe(item.css_first("li div.Ak5kof div")).text()

            # Get flight stops
            stops = safe(item.css_first(".BbR8Ec .ogfYpf")).text()
            stops_text = safe(item.css_first(".BbR8Ec .sSHqwe.tPgKwe.ogfYpf")).attributes["aria-label"]

            # Get delay
            delay = safe(item.css_first(".GsCCve")).text() or None
            price = safe(item.css_first(".YMlIz.FpEdX")).text()

            flights.append(
                {
                    "is_best": is_best_flight,
                    "name": name,
                    "departure": " ".join(departure_time.split()),
                    "arrival": " ".join(arrival_time.split()),
                    "arrival_time_ahead": time_ahead,
                    "duration": duration,
                    "stops": 0 if stops == "Nonstop" else int(stops.split(" ", 1)[0]),
                    "stops_text": stops_text,
                    "delay": delay,
                    "price": price,
                }
            )

    # Get current price
    current_price = safe(parser.css_first("span.gOatQ")).text()

    return Result(current_price=current_price, flights=[Flight(**fl) for fl in flights])  # type: ignore


def get_flights(tfs: TFSData, **kwargs: Any) -> Result:
#     start = time.time()
    rs = request_flights(tfs, **kwargs)
    if rs==-1:
        return []
#     mid = time.time()
    with open("new1.html","w") as f:
        f.write(rs.text)
    results = parse_response(rs)
#     end = time.time()
#     print("Request function call: ",mid-start)
#     print("Parse function call: ",end-mid)

    return results
