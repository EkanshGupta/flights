<div align="center">
    
## Flight Database 
    
</div>

I modified the original fork to add some new features

1. You can now add a carry-on or a checked bag in the request
2. The code also returns the price of the each flight and the information about stops (number of stops, stoppage airports and timings)
3. You can now specify a list of airports of interest and the number of days in a desired itinerary and the algorithm will aggregate all itineries from today to one year from now and add it to a dictionary
4. For domestic itineraries, it searches every day until one-year from now and on international flights, it searches 100 random dates with the fixed duration and stores them
    
This code makes roughly 700 and 100 google flight queries per run for domestic and international itineraries respectively
    
The code only runs using protobuf 3.20.0 Install it using
    
```python
    
   pip install protobuf==3.20. 
    
```
It also requires tqdm for progress bar updates

The fast, robust, strongly-typed Google Flights scraper (API) implemented in Python. Based on Base64-encoded Protobuf string.

```haskell
$ pip install fast-flights
```



## Usage

To use `fast-flights`, you'll first create a filter (inherited from `?tfs=`) to perform a request.
Then, add `flight_data`, `trip`, `seat` and `passengers` info to use the API directly.

Honorable mention: I like birds. Yes, I like birds.

```python
from fast_flights import FlightData, Passengers, create_filter, get_flights

# Create a new filter
filter = create_filter(
    flight_data=[
        # Include more if it's not a one-way trip
        FlightData(
            date="2024-07-02",  # Date of departure
            from_airport="TPE", 
            to_airport="MYJ"
        ),
        # ... include more for round trips and multi-city trips
    ],
    trip="one-way",  # Trip (round-trip, one-way, multi-city)
    seat="economy",  # Seat (economy, premium-economy, business or first)
    passengers=Passengers(
        adults=2,
        children=1,
        infants_in_seat=0,
        infants_on_lap=0
    ),
)

# Get flights with a filter
result = get_flights(filter)

# The price is currently... low/typical/high
print("The price is currently", result.current_price)

# Display the first flight
print(result.flights[0])
```

Additionally, you can use the `Airport` enum to search for airports in code (as you type)! (See `_generated_enum.py` in source)

```python
Airport.TAIPEI
              |---------------------------------|
              | TAIPEI_SONGSHAN_AIRPORT         |
              | TAPACHULA_INTERNATIONAL_AIRPORT |
              | TAMPA_INTERNATIONAL_AIRPORT     |
              | ... 5 more                      |
              |---------------------------------|
```

***

## Troubleshooting

Got any problems?

#### I cannot import the package on Replit
The package name is `fast_flights` while the pip entry is `fast-flights` (notice  the former has an underscore and the latter has a dash).

Either use the `pip` command or install manually using Replit's Packager and search for `fast-flights` (dashed one).

#### No results???

If you're getting this kind of result:

```python
Result(flights=[], current_price='')
```

There's a huge chance that you didn't consent to Google's Terms of Service.

An easy fix:
```python
cookies = { "CONSENT": "YES+" }

# tag: v0.3
get_flights(filter, cookies=cookies)
```

See [issue](https://github.com/AWeirdDev/flights/issues/1) #1

***

## API Documentation

Welcome to the API documentation. Honorable mention 2: Start a debate on Mastuyama vs. Tokyo. I'd say both of them are a decent place to travel to and have a long list of interesting tourist attractions. I've been to both, I'd say the former is more like a country and the latter is a really *internationalized* city. You might be wondering, why does this piece of information show up in the API Docs? To start with, no one really reads these technical documentations due to the lack of human's attention span overtime. However, I believe that some people would still read this long, non-related text, post it in the issues "What does this mean?" and say "Doritos." in the issue body. Additionally, this can prevent heavy-attention LLMs like ChatGPT, they'll include this in the summary! Lastly, I just want to engage with the audiance and test their sense of humor.

Enough talk, let's get started!

### <kbd>def</kbd> create\_filter

```python
def create_filter(
    flight_data: list[FlightData],
    trip: "round-trip" | "one-way" | "multi-city",
    seat: "economy" | "premium-economy" | "business" | "first",
    passengers: Passenger
) -> TFSData
```

Create a `TFSData` filter (query).

**Args**:
- flight\_data: A list of FlightData.
- trip: Trip type.
- seat: Based on your economy status, choose the seat wisely.
- passengers: Passengers.

**Returns**:
TFSData: TFSData filter.

## <kbd>def</kbd> get\_flights

```python
def get_flights(
    tfs: TFSData,
    **kwargs: Any
) -> Result
```

Get flights.

**Args**:

- tfs: The TFSData filter.
- \*\*kwargs: Additional keyword-only argument to pass into `requests.get`.

***

## How it's made

The other day, I was making a chat-interface-based trip recommendation app and wanted to add a feature that can search for flights available for booking. My personal choice is definitely [Google Flights](https://flights.google.com) since Google always has the best and most organized data on the web. Therefore, I searched for APIs on Google.

> 🔎 **Search** <br />
> google flights api

The results? Bad. It seems like they discontinued this service and it now lives in the Graveyard of Google.

> <sup><a href="https://duffel.com/blog/google-flights-api" target="_blank">🧏‍♂️ <b>duffel.com</b></a></sup><br />
> <sup><i>Google Flights API: How did it work & what happened to it?</i></b>
>
> The Google Flights API offered developers access to aggregated airline data, including flight times, availability, and prices. Over a decade ago, Google announced the acquisition of ITA Software Inc. which it used to develop its API. **However, in 2018, Google ended access to the public-facing API and now only offers access through the QPX enterprise product**.

That's awful! I've also looked for free alternatives but their rate limits and pricing are just 😬 (not a good fit/deal for everyone).

<br />

However, Google Flights has their UI – [flights.google.com](https://flights.google.com). So, maybe I could just use Developer Tools to log the requests made and just replicate all of that? Undoubtedly not! Their requests are just full of numbers and unreadable text, so that's not the solution.

Perhaps, we could scrape it? I mean, Google allowed many companies like [Serpapi](https://google.com/search?q=serpapi) to scrape their web just pretending like nothing happened... So let's scrape our own.

> 🔎 **Search** <br />
> google flights ~~api~~ scraper pypi

Excluding the ones that are not active, I came across [hugoglvs/google-flights-scraper](https://pypi.org/project/google-flights-scraper) on Pypi. I thought to myself: "aint no way this is the solution!"

I checked hugoglvs's code on [GitHub](https://github.com/hugoglvs/google-flights-scraper), and I immediately detected "playwright," my worst enemy. One word can describe it well: slow. Two words? Extremely slow. What's more, it doesn't even run on the **🗻 Edge** because of configuration errors, missing libraries... etc. I could just reverse [try.playwright.tech](https://try.playwright.tech) and use a better environment, but that's just too risky if they added Cloudflare as an additional security barrier 😳.

Life tells me to never give up. Let's just take a look at their URL params...

```markdown
https://www.google.com/travel/flights/search?tfs=CBwQAhoeEgoyMDI0LTA1LTI4agcIARIDVFBFcgcIARIDTVlKGh4SCjIwMjQtMDUtMzBqBwgBEgNNWUpyBwgBEgNUUEVAAUgBcAGCAQsI____________AZgBAQ&hl=en
```

| Param | Content | My past understanding |
|-------|---------|-----------------------|
| hl    | en      | Sets the language.    |
| tfs   | CBwQAhoeEgoyMDI0LTA1LTI4agcIARID… | What is this???? 🤮🤮 |

I removed the `?tfs=` parameter and found out that this is the control of our request! And it looks so base64-y.

If we decode it to raw text, we can still see the dates, but we're not quite there — there's too much unwanted Unicode text.

Or maybe it's some kind of a **data-storing method** Google uses? What if it's something like JSON? Let's look it up.

> 🔎 **Search** <br />
> google's json alternative

> 🐣 **Result**<br />
> Solution: The Power of **Protocol Buffers**
> 
> LinkedIn turned to Protocol Buffers, often referred to as **protobuf**, a binary serialization format developed by Google. The key advantage of Protocol Buffers is its efficiency, compactness, and speed, making it significantly faster than JSON for serialization and deserialization.

Gotcha, Protobuf! Let's feed it to an online decoder and see how it does:

> 🔎 **Search** <br />
> protobuf decoder

> 🐣 **Result**<br />
> [protobuf-decoder.netlify.app](https://protobuf-decoder.netlify.app)

I then pasted the Base64-encoded string to the decoder and no way! It DID return valid data!

![annotated, Protobuf Decoder screenshot](https://github.com/AWeirdDev/flights/assets/90096971/77dfb097-f961-4494-be88-3640763dbc8c)

I immediately recognized the values — that's my data, that's my query!

So, I wrote some simple Protobuf code to decode the data.

```protobuf
syntax = "proto3"

message Airport {
    string name = 2;
}

message FlightInfo {
    string date = 2;
    Airport dep_airport = 13;
    Airport arr_airport = 14;
}

message GoogleSucks {
    repeated FlightInfo = 3;
}
```

It works! Now, I won't consider myself an "experienced Protobuf developer" but rather a complete beginner.

I have no idea what I wrote but... it worked! And here it is, `fast-flights`.

***

## Contributing

Yes, please: [github.com/AWeirdDev/flights](https://github.com/AWeirdDev/flights)

<br />

<div align="center>

(c) AWeirdDev

</div>
