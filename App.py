import aiohttp
import asyncio
from datetime import datetime


class ApiClient:
    BASE_URL = 'https://api.privatbank.ua/p24api/'
    EXCHANGE_RATES_ENDPOINT = 'pubinfo?json&exchange&coursid=5'

    def __init__(self):
        self.api_url = f'{self.BASE_URL}{self.EXCHANGE_RATES_ENDPOINT}'

    async def get_exchange_rates(self, currency_codes, days):
        if days > 10:
            raise ValueError('Number of days cannot exceed 10.')

        async with aiohttp.ClientSession() as session:
            tasks = [self._fetch_exchange_rates(session, currency_code, days) for currency_code in currency_codes]
            results = await asyncio.gather(*tasks)
        return results

    async def _fetch_exchange_rates(self, session, currency_code, days):
        url = self._build_url(currency_code)
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f'Failed to fetch exchange rates for {currency_code}.')

            data = await response.json()

        rates = self._create_rates_dict(data, days)
        return {currency_code: rates}

    def _build_url(self, currency_code):
        return f'{self.api_url}&ccy={currency_code}'

    def _create_rates_dict(self, data, days):
        rates = {}
        for currency_data in data:
            if 'date' in currency_data:
                date_str = currency_data['date']
                try:
                    date = datetime.strptime(date_str, '%d.%m.%Y')
                    if (datetime.now() - date).days <= days:
                        sale_rate = float(currency_data['sale'])
                        purchase_rate = float(currency_data['buy'])
                        rates[date.strftime('%d.%m.%Y')] = {'sale': sale_rate, 'purchase': purchase_rate}
                except ValueError:
                    print(f'Invalid date format: {date_str}')
            else:
                print('Date field not found in currency data:', currency_data)
        return rates


class CurrencyConverter:
    @staticmethod
    def convert_amount(amount, from_currency, to_currency, exchange_rates):
        if from_currency == to_currency:
            return amount

        if from_currency not in exchange_rates or to_currency not in exchange_rates:
            raise Exception('Invalid currency code.')

        from_rates = exchange_rates[from_currency]
        to_rates = exchange_rates[to_currency]

        if 'purchase' not in from_rates or 'purchase' not in to_rates:
            raise Exception('Invalid exchange rates data.')

        converted_amount = amount / from_rates['purchase'] * to_rates['purchase']
        return converted_amount


class ConsoleApp:
    def __init__(self):
        self.base_currency = 'USD'
        self.target_currencies = ['EUR', 'GBP']
        self.days = 10
        self.api_client = ApiClient()

    async def run(self):
        currency_codes = [self.base_currency] + self.target_currencies

        try:
            exchange_rates = await self.api_client.get_exchange_rates(currency_codes, self.days)
        except Exception as e:
            print(f'Error: {e}')
            return

        response_data = []
        for rates in exchange_rates:
            currency_data = {}
            for currency_code, data in rates.items():
                currency_rates = {}
                for date, rates in data.items():
                    currency_rates[date] = {'sale': rates['sale'], 'purchase': rates['purchase']}
                currency_data[currency_code] = currency_rates
            response_data.append(currency_data)

        print(response_data)


if __name__ == '__main__':
    app = ConsoleApp()
    asyncio.run(app.run())
