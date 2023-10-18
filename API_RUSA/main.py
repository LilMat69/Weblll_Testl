# Call external libraries
import psycopg2
import locale
from flask import Flask, jsonify, abort, make_response, request

# Create default flask application
locale.setlocale(locale.LC_ALL, "es")
app = Flask(__name__)

# ================================================================
# D A T A A C C E S S C O D E
# ================================================================
# Function to execute data modification sentence
def execute(auxsql):
    data = None
    try:
        # Create data access object
        conex = psycopg2.connect(host='localhost',
                                 database='demo',
                                 user='postgres',
                                 password='Samo8908')
        # Create local cursor to SQL executor
        cur = conex.cursor()

        # Execute SQL sentence
        cur.execute(auxsql)

        # Retrieve data if exists
        data = cur.fetchall()

        # close cursor
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conex is not None:
            conex.close()
            print('Close connection.')

    # Return data
    return data
current_idio = 'en'
# ================================================================
#                 A P I R E S T F U L S E R V I C E
# ================================================================
# -----------------------------------------------------
# Error support section
# -----------------------------------------------------
@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request....!'}), 400)

@app.errorhandler(401)
def unauthorized(error):
    return make_response(jsonify({'error': 'Unauthorized....!'}), 401)

@app.errorhandler(403)
def forbiden(error):
    return make_response(jsonify({'error': 'Forbidden....!'}), 403)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found....!'}), 404)

#Chaging Idiom
@app.route('/set-language/<idio>', methods=['POST'])
def set_language(idio):
    global current_idio
    if idio in ['en', 'ru']:
        current_idio = idio
        return jsonify({'message': f'Language Set to {idio}'}), 200
    else:
        return jsonify({'error': 'Invalid Language'}), 400


# Get Aircraft
@app.route('/aircraft', methods=['GET'])
def get_aircraft():
    global current_idio
    resu = execute(f"select ad.aircraft_code, ad.model->'{current_idio}', ad.range from aircrafts_data ad")
    if resu != None:
         salida = {"status_code": 200,
                   "status": "OK",
                   "data":[]
                  }
         for cod, modelo, rango in resu:
             salida["data"].append({
                 "code": cod,
                 "model": modelo,
                "range": rango
                 })
    else:
        abort(404)
    return jsonify({'data': salida}), 200

# Codigo aeropueto
@app.route('/airports', methods=['GET'])
def get_airportsByCode():
    resu = execute(f"select airport_code, airport_name, city->'{current_idio}', coordinates, timezone from airports_data ab")
    if resu != None:
        salida = {"status_code": 200,
                  "status": "OK",
                  "data": []
                  }
        for cod,nombre, ciudad,coordinates1,timezone1 in resu:
            salida["data"].append({
                "code": cod,
                "name": nombre,
                "city": ciudad,
                "coordinates": coordinates1,
                "timezone": timezone1,
            })
    else:
        abort(404)
    return jsonify({'data': salida}), 200


# Passengers data and flight data
@app.route('/ppl', methods=['GET'])
def get_airportsByPersona():
    resu = execute("SELECT flights.flight_id, ticket_flights.ticket_no, tickets.passenger_id,tickets.passenger_name,tickets.contact_data,"
    "ticket_flights.fare_conditions, flights.departure_airport, flights.arrival_airport,flights.actual_departure, flights.actual_arrival FROM tickets INNER JOIN ticket_flights ON tickets.ticket_no = ticket_flights.ticket_no "
    "INNER JOIN flights ON ticket_flights.flight_id = flights.flight_id WHERE flights.flight_id =2666;;")
    if resu != None:
        salida = {"status_code": 200,
                  "status": "OK",
                  "data": []
                  }
        for flig_id, ticket_no, pasgId, pasgNm, contData, far_conditions, depart_airp, arr_airport, act_dept, act_arr in resu:
            salida["data"].append({
                "Flight ID": flig_id,
                "Number of Ticker": ticket_no,
                "Passenger ID": pasgId,
                "Passenger Name": pasgNm,
                "Contact": contData,
                "Class": far_conditions,
                "Departure airport": depart_airp,
                "Arrival airport": arr_airport,
                "Actual Departure": act_dept,
                "Actual Arrival": act_arr
            })
    else:
        abort(404)
    return jsonify({'data': salida}), 200


# Get Fligh Ocupation
@app.route('/ocupation', methods=['GET'])
def get_ocupation():
    resu = execute("SELECT aircrafts_data.aircraft_code, range as all_sits, fare_conditions as flghtClass, "
                   "COUNT(seat_no) AS occupied_Seats, (range - COUNT(seat_no)) as available_Seats"
                   " FROM bookings.aircrafts_data INNER JOIN seats ON seats.aircraft_code=aircrafts_data.aircraft_code "
                   "GROUP BY aircrafts_data.aircraft_code, all_sits, flghtClass;")
    if resu != None:
         salida = {"status_code": 200,
                   "status": "OK",
                   "data":[]
                  }
         for cod, sits, flightClass, OCC_Seats, AVA_seats in resu:
             salida["data"].append({
                 "code": cod,
                 "Total Sits": sits,
                 "Class": flightClass,
                 "Occupied Sits": OCC_Seats,
                 "Available Seats": AVA_seats
                 })
    else:
        abort(404)
    return jsonify({'data': salida}), 200

# -----------------------------------------------------
# Create thread app
# -----------------------------------------------------
if __name__ == '__main__':
 app.run(host='localhost', port=5001, debug=True)