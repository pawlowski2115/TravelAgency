from flask import Blueprint, jsonify
from db.repository import get_all_destinations
from services.external_api import get_currency_rate, get_current_weather

api_bp = Blueprint("api", __name__)

@api_bp.route("/destinations", methods=["GET"])
def api_get_destinations():
    destinations = get_all_destinations()
    result = []
    for dest in destinations:
        weather = get_current_weather(dest["weather_city"])
        rate = get_currency_rate(dest["currency_code"])
        result.append({
            "id": dest["id"],
            "country_name": dest["country_name"],
            "weather": weather,
            "currency_code": dest["currency_code"],
            "exchange_rate_to_pln": rate
        })
    return jsonify(result)