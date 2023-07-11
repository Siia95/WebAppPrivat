import aiohttp
import asyncio


class ApiClient:
    API_URL = 'https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5'

    async def get_exchange_rates(self, currency_codes, days):
        if days > 10:
            raise ValueError('Number of days cannot exceed 10.')

        async with aiohttp.ClientSession() as session:
            tasks = [self._fetch_exchange_rates(session, currency_code, days) for currency_code in currency_codes]
            results = await asyncio.gather(*tasks)
        return results

    async def _fetch_exchange_rates(self, session, currency_code, days):
        url = f'{self.API_URL}&ccy={currency_code}'
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f'Failed to fetch exchange rates for {currency_code}.')

            data = await response.json()

        rates = {}
        for currency_data in data:
            date = currency_data['date']
            if date <= days:
                sale_rate = float(currency_data['sale'])
                purchase_rate = float(currency_data['buy'])
                rates[date] = {'sale': sale_rate, 'purchase': purchase_rate}

        return {currency_code: rates}


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
    async def run(self, base_currency, target_currencies, days):
        currency_codes = [base_currency] + target_currencies

        api_client = ApiClient()
        try:
            exchange_rates = await api_client.get_exchange_rates(currency_codes, days)
        except Exception as e:
            print(f'Error: {e}')
            return

        for rates in exchange_rates:
            for currency_code, data in rates.items():
                print(f'{currency_code}:')
                for date, rates in data.items():
                    print(f'  {date}:')
                    print(f'    sale: {rates["sale"]}')
                    print(f'    purchase: {rates["purchase"]}')
                    print()

            print()

        # Приклад конвертації
        amount = 100
        from_currency = base_currency
        to_currency = target_currencies[0]

        try:
            converted_amount = CurrencyConverter.convert_amount(amount, from_currency, to_currency, exchange_rates[0])
            print(f'{amount} {from_currency} = {converted_amount} {to_currency}')
        except Exception as e:
            print(f'Conversion error: {e}')


if __name__ == '__main__':
    base_currency = 'USD'
    target_currencies = ['EUR', 'GBP']
    days = 10

    app = ConsoleApp()
    asyncio.run(app.run(base_currency, target_currencies, days))
