from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from datetime import datetime, timedelta
import pymysql

app = Flask(__name__)
app.secret_key = "super-secret"

# ---- Database Connection ----
def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="masterarun1",
        database="airlines",
        cursorclass=pymysql.cursors.DictCursor
    )

# ---- Fetch Flights ----
def fetch_flights():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, flight_id, flight_name, departure, arrival, route FROM flights")
            return cursor.fetchall()
    finally:
        conn.close()

# ---- Check User ----
def check_user(username, password):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
            return cursor.fetchone()
    finally:
        conn.close()

# ---- Login ----
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = check_user(username, password)
        if user:
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

# ---- Logout ----
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ---- Index ----
# ---- Index ----
@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Fetch adjusted flight data
    flights = calculate_delays()

    return render_template(
        'index.html',
        flights=flights,
        role=session['role']
    )


def calculate_delays():
    flights = fetch_flights()
    fmt = "%H:%M"
    delay_time = timedelta(minutes=5)

    # Convert strings to datetime objects and initialize delay flag
    for f in flights:
        f['arrival_dt'] = datetime.strptime(f['arrival'], fmt)
        f['departure_dt'] = datetime.strptime(f['departure'], fmt)
        f['delayed'] = False

    # Group flights by route
    routes = {}
    for f in flights:
        route = f['route']
        if route not in routes:
            routes[route] = []
        routes[route].append(f)

    # Apply delay logic within each route
    for route, group in routes.items():

        # Step 1: Same departure → delay only second flight
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                if group[i]['departure_dt'] == group[j]['departure_dt']:
                    group[j]['departure_dt'] += delay_time
                    group[j]['arrival_dt'] += delay_time
                    group[j]['delayed'] = True

        # Step 2: Same arrival → delay only second flight
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                if group[i]['arrival_dt'] == group[j]['arrival_dt']:
                    group[j]['arrival_dt'] += delay_time
                    group[j]['delayed'] = True

        # Step 3: Departure = another arrival → delay only the flight that departs
        for i in range(len(group)):
            for j in range(len(group)):
                if i != j and group[i]['departure_dt'] == group[j]['arrival_dt']:
                    group[i]['departure_dt'] += delay_time
                    group[i]['arrival_dt'] += delay_time
                    group[i]['delayed'] = True

    # Prepare the final result (temporary, not saved)
    result = []
    for f in flights:
        result.append({
            "flight_id": f['flight_id'],
            "flight_name": f['flight_name'],
            "route": f['route'],
            "original_departure": f['departure'],
            "original_arrival": f['arrival'],
            "adjusted_departure": f['departure_dt'].strftime(fmt),
            "adjusted_arrival": f['arrival_dt'].strftime(fmt),
            "delayed": f['delayed']
        })

    return result

# ---- Apply Adjusted Delays to Database (Admin only) ----
@app.route('/apply_delays', methods=['POST'])
def apply_delays():
    if session.get("role") != "admin":
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    # Calculate current adjusted delays
    adjusted_flights = calculate_delays()

    # Only update flights that were delayed
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            for f in adjusted_flights:
                if f['delayed']:
                    sql = """
                        UPDATE flights
                        SET departure=%s, arrival=%s
                        WHERE flight_id=%s
                    """
                    cursor.execute(sql, (
                        f['adjusted_departure'],
                        f['adjusted_arrival'],
                        f['flight_id']
                    ))
        conn.commit()
        return jsonify({"success": True, "message": "Adjusted times applied to DB"})
    finally:
        conn.close()


@app.route('/calculate_delay', methods=['POST'])
def calculate_delay():
    result = calculate_delays()   # list
    return jsonify(result)        # jsonify here only

# ---- Add Flight (Admin only) ----
@app.route('/add_flight', methods=['POST'])
def add_flight():
    if session.get("role") != "admin":
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    data = request.json
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO flights (flight_id, flight_name, departure, arrival, route) 
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                data['flight_id'],
                data['flight_name'],
                data['departure'],
                data['arrival'],
                data['route']
            ))
        conn.commit()
        return jsonify({"success": True})
    finally:
        conn.close()

# ---- View Flight Details ----
@app.route('/flight_details/<flight_id>')
def flight_details(flight_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM flights WHERE flight_id=%s", (flight_id,))
            flight = cursor.fetchone()
        if not flight:
            return jsonify({"error": "Flight not found"}), 404
        return jsonify(flight)
    finally:
        conn.close()

# ---- Reports Page ----
@app.route('/reports')
def reports():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('reports.html', role=session['role'])

if __name__ == "__main__":
    app.run(debug=True)
