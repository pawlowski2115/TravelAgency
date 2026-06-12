from flask import Blueprint, jsonify, request, abort
from db.repository import (
    get_all_destinations, get_destination_by_id, get_trip_by_id,
    insert_trip, update_trip, delete_trip
)
from services.external_api import get_currency_rate, get_current_weather

api_bp = Blueprint("api", __name__)

@api_bp.route("/api/destinations", methods=["GET"])
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

@api_bp.route("/api/trips", methods=["POST"])
def api_create_trip():
    data = request.get_json()
    
    required_fields = ["destination_id", "departure_date", "return_date", "departure_place", "price_local"]
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": "Brak wymaganych pól w formacie JSON"}), 400

    dest = get_destination_by_id(int(data["destination_id"]))
    if not dest:
        return jsonify({"error": "Nie znaleziono kierunku o podanym ID"}), 404

    rate = get_currency_rate(dest["currency_code"])
    price_pln = round(float(data["price_local"]) * rate, 2)

    insert_trip(
        int(data["destination_id"]), data["departure_date"], data["return_date"],
        data["departure_place"], float(data["price_local"]), price_pln
    )
    return jsonify({"success": True, "message": "Wycieczka została pomyślnie dodana przez API"}), 211

@api_bp.route("/api/trips/<int:trip_id>", methods=["PUT"])
def api_update_trip(trip_id):
    trip = get_trip_by_id(trip_id)
    if not trip:
        return jsonify({"error": "Nie znaleziono wycieczki o podanym ID"}), 404

    data = request.get_json()
    required_fields = ["departure_date", "return_date", "departure_place", "price_local"]
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": "Brak wymaganych pól do edycji"}), 400

    dest = get_destination_by_id(trip["destination_id"])
    rate = get_currency_rate(dest["currency_code"])
    price_pln = round(float(data["price_local"]) * rate, 2)

    update_trip(
        trip_id, data["departure_date"], data["return_date"],
        data["departure_place"], float(data["price_local"]), price_pln
    )
    return jsonify({"success": True, "message": f"Wycieczka o ID {trip_id} została zaktualizowana przez API"}), 200

@api_bp.route("/api/trips/<int:trip_id>", methods=["DELETE"])
def api_delete_trip(trip_id):
    if not get_trip_by_id(trip_id):
        return jsonify({"error": "Nie znaleziono wycieczki o podanym ID"}), 404

    delete_trip(trip_id)
    return jsonify({"success": True, "message": f"Wycieczka o ID {trip_id} została pomyślnie usunięta"}), 200