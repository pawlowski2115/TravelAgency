from flask import Flask, jsonify, request, abort
from db.init import init_db_command_init, seed_db_command_init, close_db 
from db.repository import (
    get_all_destinations, 
    get_destination_by_id, 
    get_trips_by_destination, 
    get_trip_by_id, 
    insert_trip, 
    update_trip, 
    delete_trip,
    toggle_trip_sold_out
)
from services.external_api import get_currency_rate, get_current_weather

app = Flask(__name__)
app.teardown_appcontext(close_db)

init_db_command_init(app)
seed_db_command_init(app)

@app.route("/destinations", methods=["GET"])
def api_get_destinations():
    destination = get_all_destinations()
    result = []

    for dest in destination:
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

@app.route("/destinations/<int:dest_id>/trips", methods=["GET"])
def api_get_trips(dest_id):
    if not get_destination_by_id(dest_id):
        abort(404, description="Destination not found")
        
    trips = get_trips_by_destination(dest_id)
    return jsonify([dict(t) for t in trips])

@app.route("/trips", methods=["POST"])
def api_add_trip():
    data = request.get_json()
    if not data or not all(k in data for k in ("destination_id", "departure_date", "return_date", "departure_place", "price_local")):
        abort(400, description="Missing required fields")
        
    dest = get_destination_by_id(data["destination_id"])
    if not dest:
        abort(404, description="Destination country not found")
        
    rate = get_currency_rate(dest["currency_code"])
    price_pln = round(float(data["price_local"]) * rate, 2)
    
    new_trip_id = insert_trip(
        destination_id=data["destination_id"],
        departure_date=data["departure_date"],
        return_date=data["return_date"],
        departure_place=data["departure_place"],
        price_local=float(data["price_local"]),
        price_pln=price_pln
    )
    
    return jsonify({
        "message": "Trip added successfully", 
        "trip_id": new_trip_id, 
        "price_pln": price_pln
    }), 201

@app.route("/trips/<int:trip_id>/toggle-sold-out", methods=["POST"])
def api_toggle_sold_out(trip_id):
    trip = get_trip_by_id(trip_id)
    if not trip:
        abort(404, description="Trip not found")
        
    toggle_trip_sold_out(trip_id, trip["is_sold_out"])
    return jsonify({"message": "Trip status updated successfully"})

@app.route("/trips/<int:trip_id>", methods=["DELETE"])
def api_delete_trip(trip_id):
    if not get_trip_by_id(trip_id):
        abort(404, description="Trip not found")
        
    delete_trip(trip_id)
    return "", 204

if __name__ == "__main__":
    app.run(debug=True)

