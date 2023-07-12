import sys
import datetime
import asyncio
import aiohttp


async def fetch_exchange_rates(session, date):
    url = f"https://api.privatbank.ua/p24api/exchange_rates?json&date={date}"
    async with session.get(url) as response:
        if response.status == 200:
            data = await response.json()
            return data
        else:
            return None


async def get_exchange_rates(dates):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_exchange_rates(session, date) for date in dates]
        results = await asyncio.gather(*tasks)
        return results


def format_exchange_rate(currency, sale, purchase):
    return {
        currency: {
            "sale": sale,
            "purchase": purchase
        }
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <days>")
        return

    try:
        days = int(sys.argv[1])
        if days > 10:
            print("Error: Maximum number of days allowed is 10.")
            return
    except ValueError:
        print("Error: Invalid number of days.")
        return

    dates = [(datetime.date.today() - datetime.timedelta(days=i)).strftime("%d.%m.%Y") for i in range(1, days + 1)]

    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(get_exchange_rates(dates))

    formatted_results = []
    for i, result in enumerate(results):
        date = dates[i]
        if result is not None:
            array = []

            for el in result.get("exchangeRate"):
                if el.get("currency") == "USD" or el.get("currency") == "EUR":
                    array.append(format_exchange_rate(el.get("currency"), el.get("saleRate"), el.get("purchaseRate")))


            if len(array) > 0:
                formatted_results.append({date: array})

    print(formatted_results)


if __name__ == "__main__":
    main()
