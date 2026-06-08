from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from db.repository import (
    get_all_destinations, get_destination_by_id, get_trips_by_destination, 
    get_trip_by_id, insert_trip, update_trip, delete_trip, toggle_trip_sold_out, get_trip_stats
)
from services.external_api import get_currency_rate, get_current_weather

web_bp = Blueprint("web", __name__)

@web_bp.route("/", methods=["GET"])
def index():
    destinations = get_all_destinations()
    destinations_data = []
    for dest in destinations:
        weather = get_current_weather(dest["weather_city"])
        rate = get_currency_rate(dest["currency_code"])
        trips = get_trips_by_destination(dest["id"])
        
        destinations_data.append({
            "id": dest["id"], "country_name": dest["country_name"], "weather": weather,
            "currency_code": dest["currency_code"], "exchange_rate_to_pln": rate, "trips": trips
        })
    stats = get_trip_stats()
    return render_template("index.html", destinations_data=destinations_data, stats=stats)

@web_bp.route("/trips/add", methods=["GET", "POST"])
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
        return redirect(url_for("web.index"))
        
    destinations = get_all_destinations()
    return render_template("add_trip.html", destinations=destinations)

@web_bp.route("/trips/<int:trip_id>/edit", methods=["GET", "POST"])
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
        return redirect(url_for("web.index"))
    return render_template("edit_trip.html", trip=trip)

@web_bp.route("/web/trips/<int:trip_id>/toggle", methods=["POST"])
def web_toggle_sold_out(trip_id):
    trip = get_trip_by_id(trip_id)
    if trip:
        toggle_trip_sold_out(trip_id, trip["is_sold_out"])
        flash("Zmieniono status dostępności oferty.", "info")
    return redirect(url_for("web.index"))

@web_bp.route("/web/trips/<int:trip_id>/delete", methods=["POST"])
def web_delete_trip(trip_id):
    if get_trip_by_id(trip_id):
        delete_trip(trip_id)
        flash("Oferta została pomyślnie usunięta.", "success")
    return redirect(url_for("web.index"))