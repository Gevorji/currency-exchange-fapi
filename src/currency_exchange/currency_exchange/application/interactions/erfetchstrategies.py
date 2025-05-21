from enum import Flag, auto


class ExchangeRateFetchStrategy(Flag):
	BY_STRAIGHT_RATE = auto()
	BY_REVERSED_RATE = auto()
	BY_COMMON_CURRENCY = auto()
