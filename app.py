from flask import Flask, jsonify, request, abort, render_template, redirect, url_for, flash
from db.init import init_db_command_init, seed_db_command_init, close_db
import secrets

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

app.config["SECRET_KEY"] = secrets.token_urlsafe(16)

init_db_command_init(app)
seed_db_command_init(app)


@app.route("/", methods=["GET"])
def index():
    destinations = get_all_destinations()
    destinations_data = []
    
    for dest in destinations:
        weather = get_current_weather(dest["weather_city"])
        rate = get_currency_rate(dest["currency_code"])
        
        trips = get_trips_by_destination(dest["id"])
        
        destinations_data.append({
            "id": dest["id"],
            "country_name": dest["country_name"],
            "weather": weather,
            "currency_code": dest["currency_code"],
            "exchange_rate_to_pln": rate,
            "trips": trips
        })
        
    return render_template("index.html", destinations_data=destinations_data)


@app.route("/trips/add", methods=["GET", "POST"])
def web_add_trip():
    if request.method == "POST":
        dest_id = int(request.form["destination_id"])
        departure_date = request.form["departure_date"]
        return_date = request.form["return_date"]
        departure_place = request.form["departure_place"]
        price_local = float(request.form["price_local"])
        
        dest = get_destination_by_id(dest_id)
        rate = get_currency_rate(dest["currency_code"])
        price_pln = round(price_local * rate, 2)
        
        insert_trip(dest_id, departure_date, return_date, departure_place, price_local, price_pln)
        flash("Pomyślnie dodano nową ofertę wyjazdu!", "success")
        return redirect(url_for("index"))
        
    destinations = get_all_destinations()
    return render_template("add_trip.html", destinations=destinations)


@app.route("/trips/<int:trip_id>/edit", methods=["GET", "POST"])
def web_edit_trip(trip_id):
    trip = get_trip_by_id(trip_id)
    if not trip:
        abort(404, description="Nie znaleziono takiej wycieczki.")
        
    if request.method == "POST":
        departure_date = request.form["departure_date"]
        return_date = request.form["return_date"]
        departure_place = request.form["departure_place"]
        price_local = float(request.form["price_local"])
        
        dest = get_destination_by_id(trip["destination_id"])
        rate = get_currency_rate(dest["currency_code"])
        price_pln = round(price_local * rate, 2)
        
        update_trip(trip_id, departure_date, return_date, departure_place, price_local, price_pln)
        flash("Oferta została pomyślnie zaktualizowana.", "success")
        return redirect(url_for("index"))
        
    return render_template("edit_trip.html", trip=trip)


@app.route("/web/trips/<int:trip_id>/toggle", methods=["POST"])
def web_toggle_sold_out(trip_id):
    trip = get_trip_by_id(trip_id)
    if trip:
        toggle_trip_sold_out(trip_id, trip["is_sold_out"])
        flash("Zmieniono status dostępności oferty.", "info")
    return redirect(url_for("index"))


@app.route("/web/trips/<int:trip_id>/delete", methods=["POST"])
def web_delete_trip(trip_id):
    if get_trip_by_id(trip_id):
        delete_trip(trip_id)
        flash("Oferta została pomyślnie usunięta.", "success")
    return redirect(url_for("index"))


@app.route("/destinations", methods=["GET"])
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


if __name__ == "__main__":
    app.run(debug=True)