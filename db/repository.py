from db.init import get_db

def get_all_destinations():
    db = get_db()
    return db.execute("SELECT id, country_name, weather_city, currency_code FROM destinations").fetchall()

def get_destination_by_id(destination_id):
    db = get_db()
    return db.execute("SELECT id, country_name, weather_city, currency_code FROM destinations WHERE id = ?", 
        [destination_id]).fetchone()

def get_trips_by_destination(destination_id):
    db = get_db()
    return db.execute("SELECT id, destination_id, departure_date, return_date, departure_place, price_local, price_pln, is_sold_out "
        "FROM trips WHERE destination_id = ? ORDER BY departure_date ASC",[destination_id]).fetchall()

def get_trip_by_id(trip_id):
    db = get_db()
    return db.execute("SELECT id, destination_id, departure_date, return_date, departure_place, price_local, price_pln, is_sold_out "
        "FROM trips WHERE id = ?",[trip_id]).fetchone()

def insert_trip(destination_id, departure_date, return_date, departure_place, price_local, price_pln):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO trips (destination_id, departure_date, return_date, departure_place, price_local, price_pln) "
        "VALUES (?, ?, ?, ?, ?, ?)",[destination_id, departure_date, return_date, departure_place, price_local, price_pln]
    )
    db.commit()
    return cursor.lastrowid

def update_trip(trip_id, departure_date, return_date, departure_place, price_local, price_pln):
    db = get_db()
    db.execute(
        "UPDATE trips SET departure_date = ?, return_date = ?, departure_place = ?, price_local = ?, price_pln = ? "
        "WHERE id = ?",[departure_date, return_date, departure_place, price_local, price_pln, trip_id]
    )
    db.commit()

def toggle_trip_sold_out(trip_id, current_status):
    db = get_db()
    new_status = 1 if current_status == 0 else 0
    db.execute("UPDATE trips SET is_sold_out = ? WHERE id = ?", [new_status, trip_id])
    db.commit()

def delete_trip(trip_id):
    db = get_db()
    db.execute("DELETE FROM trips WHERE id = ?", [trip_id])
    db.commit()

def get_trip_stats():
    db = get_db()
    stats = db.execute("""
        SELECT 
            COUNT(*) as total_trips,
            COALESCE(ROUND(AVG(price_pln), 2), 0.00) as avg_price
        FROM trips
    """).fetchone()
    return stats