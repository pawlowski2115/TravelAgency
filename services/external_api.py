import requests

WEATHER_API_KEY = "22e007806268489f3af8430a0d0a3301"

def get_current_weather(city_name):
    """Pobiera aktualną pogodę z OpenWeatherMap API."""
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={WEATHER_API_KEY}&units=metric"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            temp = round(data['main']['temp'])
            icon = data['weather'][0]['icon']
            return {"temp": temp, "icon": icon}
        else:
            return {"temp": 21, "icon": "01d"}
            
    except requests.RequestException:
        return {"temp": 20, "icon": "02d"}

def get_currency_rate(currency_code):
    if currency_code == "PLN":
        return 1.0
    try:
        url = f"https://api.nbp.pl/api/exchangerates/rates/a/{currency_code}/?format=json"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            rate = data['rates'][0]['mid']
            return float(rate)
        else:
            return get_fallback_rate(currency_code)
            
    except requests.RequestException:
        return get_fallback_rate(currency_code)

def get_fallback_rate(currency_code):
    rates = {
        "EUR": 4.30,
        "USD": 4.00,
        "JPY": 0.026
    }
    return rates.get(currency_code, 1.0)