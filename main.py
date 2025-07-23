from flask import Flask, request, jsonify
import swisseph as swe
from datetime import datetime, timedelta
import math
import pytz
from geopy.geocoders import Nominatim

app = Flask(__name__)

# Swiss Ephemeris path
swe.set_ephe_path('./sweph')

def get_coordinates(location_name):
    """Convert location name to coordinates"""
    try:
        geolocator = Nominatim(user_agent="horary_astrology_app")
        location = geolocator.geocode(location_name)
        if location:
            return location.latitude, location.longitude
        else:
            # Default to Istanbul if location not found
            return 41.0082, 28.9784
    except:
        return 41.0082, 28.9784

def calculate_julian_day(date_str, time_str, timezone_offset=3):
    """Calculate Julian Day Number"""
    try:
        # Parse date and time
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        time_obj = datetime.strptime(time_str, '%H:%M').time()
        
        # Combine date and time
        dt = datetime.combine(date_obj.date(), time_obj)
        
        # Convert to UTC (subtract timezone offset)
        dt_utc = dt - timedelta(hours=timezone_offset)
        
        # Calculate Julian Day
        jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, 
                       dt_utc.hour + dt_utc.minute/60.0)
        return jd
    except Exception as e:
        print(f"Julian Day calculation error: {e}")
        return None

def get_planet_positions(julian_day):
    """Calculate planet positions"""
    planets = {
        'sun': swe.SUN,
        'moon': swe.MOON,
        'mercury': swe.MERCURY,
        'venus': swe.VENUS,
        'mars': swe.MARS,
        'jupiter': swe.JUPITER,
        'saturn': swe.SATURN,
        'uranus': swe.URANUS,
        'neptune': swe.NEPTUNE,
        'pluto': swe.PLUTO
    }
    
    positions = {}
    
    for planet_name, planet_id in planets.items():
        try:
            # Calculate planet position
            result = swe.calc_ut(julian_day, planet_id)
            longitude = result[0][0]  # Longitude in degrees
            
            # Convert to zodiac sign and degree
            sign_num = int(longitude // 30)
            degree = longitude % 30
            
            signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
            
            positions[planet_name] = {
                'longitude': round(longitude, 2),
                'sign': signs[sign_num],
                'degree': round(degree, 2),
                'sign_degree': f"{round(degree)}° {signs[sign_num]}"
            }
            
        except Exception as e:
            print(f"Error calculating {planet_name}: {e}")
            positions[planet_name] = {
                'longitude': 0,
                'sign': 'Unknown',
                'degree': 0,
                'sign_degree': 'Error'
            }
    
    return positions

def calculate_houses(julian_day, latitude, longitude):
    """Calculate astrological houses"""
    try:
        # Calculate houses using Placidus system
        houses = swe.houses(julian_day, latitude, longitude, b'P')
        
        house_positions = {}
        signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
        
        for i in range(12):
            house_longitude = houses[0][i]
            sign_num = int(house_longitude // 30)
            degree = house_longitude % 30
            
            house_positions[f'house_{i+1}'] = {
                'longitude': round(house_longitude, 2),
                'sign': signs[sign_num],
                'degree': round(degree, 2),
                'sign_degree': f"{round(degree)}° {signs[sign_num]}"
            }
        
        # Calculate Ascendant, MC, etc.
        ascendant = houses[1][0]  # Ascendant
        mc = houses[1][1]  # Midheaven
        
        asc_sign_num = int(ascendant // 30)
        asc_degree = ascendant % 30
        
        mc_sign_num = int(mc // 30)
        mc_degree = mc % 30
        
        house_positions['ascendant'] = {
            'longitude': round(ascendant, 2),
            'sign': signs[asc_sign_num],
            'degree': round(asc_degree, 2),
            'sign_degree': f"{round(asc_degree)}° {signs[asc_sign_num]}"
        }
        
        house_positions['midheaven'] = {
            'longitude': round(mc, 2),
            'sign': signs[mc_sign_num],
            'degree': round(mc_degree, 2),
            'sign_degree': f"{round(mc_degree)}° {signs[mc_sign_num]}"
        }
        
        return house_positions
        
    except Exception as e:
        print(f"House calculation error: {e}")
        return {}

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Swiss Ephemeris API is running',
        'version': '1.0.0'
    })

@app.route('/api/horoscope', methods=['GET', 'POST'])
def calculate_horoscope():
    """Main endpoint for horoscope calculation"""
    try:
        if request.method == 'POST':
            data = request.get_json()
        else:
            data = request.args.to_dict()
        
        # Extract required parameters
        birth_date = data.get('birth_date')
        birth_time = data.get('birth_time')
        latitude = float(data.get('latitude', 41.0082))
        longitude = float(data.get('longitude', 28.9784))
        timezone_offset = int(data.get('timezone_offset', 3))
        
        # Validate required fields
        if not birth_date or not birth_time:
            return jsonify({
                'success': False,
                'error': 'birth_date and birth_time are required',
                'example': {
                    'birth_date': '1990-01-01',
                    'birth_time': '12:00',
                    'latitude': 41.0082,
                    'longitude': 28.9784
                }
            }), 400
        
        # Calculate Julian Day
        from datetime import timedelta
        julian_day = calculate_julian_day(birth_date, birth_time, timezone_offset)
        
        if julian_day is None:
            return jsonify({
                'success': False,
                'error': 'Invalid date or time format'
            }), 400
        
        # Calculate planet positions
        planets = get_planet_positions(julian_day)
        
        # Calculate houses
        houses = calculate_houses(julian_day, latitude, longitude)
        
        # Prepare result
        result = {
            'success': True,
            'message': 'Horoscope calculated successfully',
            'input_data': {
                'birth_date': birth_date,
                'birth_time': birth_time,
                'latitude': latitude,
                'longitude': longitude,
                'timezone_offset': timezone_offset,
                'julian_day': round(julian_day, 6)
            },
            'planets': planets,
            'houses': houses,
            'chart_info': {
                'calculation_time': datetime.now().isoformat(),
                'ephemeris': 'Swiss Ephemeris',
                'house_system': 'Placidus'
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Calculation error: {str(e)}',
            'input_data': data if 'data' in locals() else {}
        }), 500

if __name__ == '__main__':
    print("Starting Swiss Ephemeris API...")
    print("Swiss Ephemeris version:", swe.version)
    app.run(host='0.0.0.0', port=8080, debug=False)
