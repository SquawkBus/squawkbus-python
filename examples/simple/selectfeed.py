import asyncio
from asyncio import Event
import json
import logging
import random
from signal import SIGINT, SIGTERM
from typing import (
    Any,
    AsyncIterator,
    Literal,
    MutableMapping,
    NamedTuple,
    Protocol,
    Sequence,
    TypedDict,
)

from squawkbus import DataPacket, SocketClient

LOGGER = logging.getLogger("quote_simulator")


class BroadcastFeed[DataT: MutableMapping](Protocol):

    def start(
            self,
            stop_event: Event
    ) -> AsyncIterator[tuple[str, DataT]]:
        ...


class Company(NamedTuple):
    ticker: str
    name: str
    last_price: float


class MarketData(TypedDict):
    ticker: str
    name: str
    bid: float
    ask: float


class Quote(TypedDict, total=False):
    bid: float
    ask: float


def nudge_price(price: float, lower: float = -1.0, upper: float = 1.0) -> float:
    price_change = random.uniform(lower, upper) / 100
    return round(price + price * price_change, 2)


class MarketSimulator:

    def __init__(
            self,
            companies: Sequence[Company],
            min_delay: float,
            max_delay: float
    ) -> None:
        self._min_delay = min_delay
        self._max_delay = max_delay
        self._market_data: dict[str, MarketData] = {
            company.ticker: {
                'ticker': company.ticker,
                'name': company.name,
                'bid': nudge_price(company.last_price, upper=0.0),
                'ask': nudge_price(company.last_price, lower=0.0),
            }
            for company in companies
        }
        self._tickers = tuple(self._market_data.keys())

    def _make_random_change(self) -> tuple[str, MarketData]:
        ticker = random.choice(self._tickers)
        side: Literal['bid', 'ask'] = random.choice(['bid', 'ask'])
        data = self._market_data[ticker]
        data[side] = nudge_price(data[side])

        if data['bid'] > data['ask']:
            if side == 'bid':
                data['ask'] = nudge_price(data['bid'], lower=0.0)
            else:
                data['bid'] = nudge_price(data['ask'], upper=0.0)

        return ticker, data

    async def start(
            self,
            stop_event: Event
    ) -> AsyncIterator[tuple[str, MarketData]]:
        while not stop_event.is_set():
            sleep_seconds = random.uniform(self._min_delay, self._max_delay)
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=sleep_seconds)
            except asyncio.TimeoutError:
                ticker, data = self._make_random_change()
                yield ticker, data.copy()


def _changes[DataT: MutableMapping](a: DataT | None, b: DataT) -> MutableMapping[str, Any]:
    return b if a is None else {
        key: value
        for key, value in a.items()
        if a[key] != b[key]
    }


class SelectFeed[DataT: MutableMapping]:

    def __init__(
            self,
            socket_client: SocketClient,
            broadcast_feed: BroadcastFeed[DataT],
            prefix: str
    ) -> None:
        self._socket_client = socket_client
        self._broadcast_feed = broadcast_feed
        self._prefix = prefix
        self._index_topic = f"{self._prefix}.#topics"
        self._data = dict[str, DataT]()
        self._ticker_subscriptions = dict[str, set[str]]()
        self._index_subscriptions = set[str]()

    def _to_data_packets(self, data: Any | None) -> list[DataPacket]:
        return [] if data is None else [
            DataPacket(
                {0},
                {b"content-type": b"application/json"},
                json.dumps(data).encode('utf-8')
            )
        ]

    def _to_topics_data_packet(self) -> list[DataPacket]:
        return self._to_data_packets(
            [f"{self._prefix}{topic}" for topic in self._data.keys()]
        )

    async def _publish(
            self,
            topic: str,
            client_id: str | None,
            data: Any
    ) -> None:
        LOGGER.debug("Publishing to \"%s\" with %s", topic, data)

        data_packets = self._to_data_packets(data)
        if client_id is not None:
            await self._socket_client.send(client_id, topic, data_packets)
        else:
            await self._socket_client.publish(topic, data_packets)

    async def _publish_index(self, client_id: str | None) -> None:
        await self._publish(
            self._index_topic,
            client_id,
            [f"{self._prefix}.{topic}" for topic in self._data.keys()]
        )

    async def _publish_data(
            self,
            client_id: str | None,
            ticker: str,
            data: Any | None
    ) -> None:
        await self._publish(
            f"{self._prefix}.{ticker}",
            client_id,
            data
        )

    async def _handle_index_request(
            self,
            client_id: str,
            count: int,
    ) -> None:
        if count > 0:
            self._index_subscriptions.add(client_id)
            await self._publish_index(client_id)
        else:
            self._index_subscriptions.discard(client_id)

    async def _handle_ticker_request(
            self,
            client_id: str,
            ticker: str,
            count: int,
    ) -> None:
        if count > 0:
            if ticker not in self._ticker_subscriptions:
                self._ticker_subscriptions[ticker] = set()
            self._ticker_subscriptions[ticker].add(client_id)
            await self._publish_data(client_id, ticker, self._data.get(ticker, {}))
        else:
            if ticker in self._ticker_subscriptions:
                self._ticker_subscriptions[ticker].discard(client_id)
                if not self._ticker_subscriptions[ticker]:
                    del self._ticker_subscriptions[ticker]

    async def _handle_notification(
            self,
            client_id: str,
            _user: str,
            _host: str,
            topic: str,
            count: int
    ) -> None:
        LOGGER.debug("Received subscription on topic \"%s\"", topic)

        try:
            prefix, sep, ticker = topic.partition('.')
            if prefix != self._prefix or not sep:
                raise ValueError(f"Unknown topic \"{topic}\"")

            if ticker == "#index":
                await self._handle_index_request(client_id, count)
            else:
                await self._handle_ticker_request(client_id, ticker, count)

        except:  # pylint: disable=bare-except
            LOGGER.exception("Failed to unpack topic request on %s", topic)
            return

    async def start(
            self,
            stop_event: Event
    ) -> None:
        self._socket_client.notification_handlers.append(
            self._handle_notification
        )

        await self._socket_client.add_notification("quote.XNAS.*")

        async for ticker, data in self._broadcast_feed.start(stop_event):

            # LOGGER.debug(
            #     "Received market data for ticker \"%s\": %s",
            #     ticker,
            #     data
            # )

            prev = self._data.get(ticker)

            if ticker in self._ticker_subscriptions:
                await self._publish_data(None, ticker, _changes(prev, data))

            if ticker not in self._data:
                self._data[ticker] = data
                if self._index_subscriptions:
                    await self._publish_index(None)
            else:
                self._data[ticker].update(data)


def _create_stop_event() -> Event:
    loop = asyncio.get_running_loop()
    stop_event = Event()
    for signal in [SIGINT, SIGTERM]:
        loop.add_signal_handler(signal, stop_event.set)

    return stop_event


async def main(
        companies: Sequence[Company],
        min_delay: float,
        max_delay: float,
        prefix: str,
        host: str,
        port: int
) -> None:
    LOGGER.info("Starting quote simulator")

    LOGGER.debug("Connecting to squawkbus on %s:%s", host, port)
    squawkbus = await SocketClient.create(host, port)
    LOGGER.debug("Connected as %s", squawkbus.client_id)

    select_feed = SelectFeed(
        squawkbus,
        MarketSimulator(companies, min_delay, max_delay),  # type: ignore
        prefix
    )
    await select_feed.start(_create_stop_event())

    LOGGER.debug("Closing squawkbus")
    squawkbus.close()
    await squawkbus.wait_closed()


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    LOGGER.setLevel(logging.DEBUG)

    COMPANIES = (
        Company('XNAS.AAPL', 'Apple', 262.82),
        Company('XNAS.GOOGL', 'Alphabet', 259.92),
        Company('XNAS.MSFT', 'Microsoft', 523.61),
        Company('XNAS.AMZN', 'Amazon', 224.21),
        Company('XNAS.NVDA', 'Nvidia', 186.26),
        Company('XNAS.META', 'Meta', 738.76),
        Company('XNAS.INTC', 'Intel', 38.28),
        Company('XNAS.AMD', 'Advanced Micro Devices', 292.82),
    )
    MIN_DELAY, MAX_DELAY = 0.1, 2.0
    HOST, PORT = "localhost", 8558
    PREFIX = "quote"
    asyncio.run(main(COMPANIES, MIN_DELAY, MAX_DELAY, PREFIX, HOST, PORT))
