from typing import Literal, List
from .flights_impl import FlightData, Passengers, TFSData, Bags


def create_filter(
    *,
    flight_data: List[FlightData],
    bags: Bags,
    trip: Literal["round-trip", "one-way", "multi-city"],
    passengers: Passengers,
    seat: Literal["economy", "premium-economy", "business", "first"],
) -> TFSData:
    """Create a filter. (``?tfs=``)

    Args:
        flight_data (list[FlightData]): Flight data as a list.
        trip ("one-way" | "round-trip" | "multi-city"): Trip type.
        passengers (Passengers): Passengers.
        seat ("economy" | "premium-economy" | "business" | "first"): Seat.
    """
    return TFSData.from_interface(
        flight_data=flight_data, bags=bags, trip=trip, passengers=passengers, seat=seat
    )
