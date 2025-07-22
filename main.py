from flask import Flask, request, jsonify
import swisseph as swe
from datetime import datetime
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
        
        # Test response for now
        result = {
            'success': True,
            'message': 'Swiss Ephemeris API is working!',
            'input_data': data
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("Starting Swiss Ephemeris API...")
    app.run(host='0.0.0.0', port=8080, debug=False)
