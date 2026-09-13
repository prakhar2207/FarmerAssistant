from typing import Dict, Any, Optional, Tuple
from app.config import DEFAULT_LATITUDE, DEFAULT_LONGITUDE, DEFAULT_DISTRICT, DEFAULT_STATE
from app.modules.weather.provider import default_weather_provider

# Comprehensive Pan-Indian Agricultural District Geocoordinates
DISTRICT_COORDS = {
    # Uttar Pradesh
    'lucknow': (26.8467, 80.9462, 'Lucknow', 'Uttar Pradesh'),
    'kanpur': (26.4499, 80.3319, 'Kanpur', 'Uttar Pradesh'),
    'varanasi': (25.3176, 82.9739, 'Varanasi', 'Uttar Pradesh'),
    'prayagraj': (25.4358, 81.8463, 'Prayagraj', 'Uttar Pradesh'),
    'meerut': (28.9845, 77.7064, 'Meerut', 'Uttar Pradesh'),
    'gorakhpur': (26.7606, 83.3732, 'Gorakhpur', 'Uttar Pradesh'),
    'bareilly': (28.3670, 79.4304, 'Bareilly', 'Uttar Pradesh'),
    'aligarh': (27.8974, 78.0880, 'Aligarh', 'Uttar Pradesh'),
    'moradabad': (28.8350, 78.7747, 'Moradabad', 'Uttar Pradesh'),
    'ayodhya': (26.7922, 82.1998, 'Ayodhya', 'Uttar Pradesh'),
    'jhansi': (25.4484, 78.5685, 'Jhansi', 'Uttar Pradesh'),
    'agra': (27.1767, 78.0081, 'Agra', 'Uttar Pradesh'),
    'mathura': (27.4924, 77.6737, 'Mathura', 'Uttar Pradesh'),
    'sitapur': (27.5684, 80.6829, 'Sitapur', 'Uttar Pradesh'),
    'barabanki': (26.9272, 81.1843, 'Barabanki', 'Uttar Pradesh'),
    # Bihar
    'patna': (25.5941, 85.1376, 'Patna', 'Bihar'),
    'muzaffarpur': (26.1209, 85.3647, 'Muzaffarpur', 'Bihar'),
    'gaya': (24.7955, 85.0002, 'Gaya', 'Bihar'),
    'bhagalpur': (25.2425, 86.9842, 'Bhagalpur', 'Bihar'),
    'purnia': (25.7771, 87.4753, 'Purnia', 'Bihar'),
    'samastipur': (25.8629, 85.7811, 'Samastipur', 'Bihar'),
    # Madhya Pradesh
    'bhopal': (23.2599, 77.4126, 'Bhopal', 'Madhya Pradesh'),
    'indore': (22.7196, 75.8577, 'Indore', 'Madhya Pradesh'),
    'jabalpur': (23.1815, 79.9864, 'Jabalpur', 'Madhya Pradesh'),
    'gwalior': (26.2183, 78.1828, 'Gwalior', 'Madhya Pradesh'),
    'ujjain': (23.1765, 75.7885, 'Ujjain', 'Madhya Pradesh'),
    'hoshangabad': (22.7519, 77.7289, 'Narmadapuram', 'Madhya Pradesh'),
    # Punjab & Haryana
    'ludhiana': (30.9010, 75.8573, 'Ludhiana', 'Punjab'),
    'amritsar': (31.6340, 74.8723, 'Amritsar', 'Punjab'),
    'jalandhar': (31.3260, 75.5762, 'Jalandhar', 'Punjab'),
    'bathinda': (30.2110, 74.9455, 'Bathinda', 'Punjab'),
    'karnal': (29.6857, 76.9905, 'Karnal', 'Haryana'),
    'hisar': (29.1492, 75.7217, 'Hisar', 'Haryana'),
    'rohtak': (28.8955, 76.6066, 'Rohtak', 'Haryana'),
    'ambala': (30.3782, 76.7767, 'Ambala', 'Haryana'),
    # Rajasthan
    'jaipur': (26.9124, 75.7873, 'Jaipur', 'Rajasthan'),
    'jodhpur': (26.2389, 73.0243, 'Jodhpur', 'Rajasthan'),
    'kota': (25.2138, 75.8648, 'Kota', 'Rajasthan'),
    'udaipur': (24.5854, 73.7125, 'Udaipur', 'Rajasthan'),
    'bikaner': (28.0229, 73.3119, 'Bikaner', 'Rajasthan'),
    'ganganagar': (29.9038, 73.8772, 'Sri Ganganagar', 'Rajasthan'),
    # Maharashtra
    'nagpur': (21.1458, 79.0882, 'Nagpur', 'Maharashtra'),
    'pune': (18.5204, 73.8567, 'Pune', 'Maharashtra'),
    'nashik': (19.9975, 73.7898, 'Nashik', 'Maharashtra'),
    'aurangabad': (19.8762, 75.3433, 'Chhatrapati Sambhaji Nagar', 'Maharashtra'),
    'solapur': (17.6599, 75.9064, 'Solapur', 'Maharashtra'),
    'amravati': (20.9374, 77.7796, 'Amravati', 'Maharashtra'),
    # Gujarat
    'ahmedabad': (23.0225, 72.5714, 'Ahmedabad', 'Gujarat'),
    'rajkot': (22.3039, 70.8022, 'Rajkot', 'Gujarat'),
    'surat': (21.1702, 72.8311, 'Surat', 'Gujarat'),
    'vadodara': (22.3072, 73.1812, 'Vadodara', 'Gujarat'),
    'anand': (22.5645, 72.9289, 'Anand', 'Gujarat'),
    # Southern & Eastern States
    'hyderabad': (17.3850, 78.4867, 'Hyderabad', 'Telangana'),
    'bengaluru': (12.9716, 77.5946, 'Bengaluru', 'Karnataka'),
    'shimoga': (13.9299, 75.5681, 'Shivamogga', 'Karnataka'),
    'coimbatore': (11.0168, 76.9558, 'Coimbatore', 'Tamil Nadu'),
    'madurai': (9.9252, 78.1198, 'Madurai', 'Tamil Nadu'),
    'vijayawada': (16.5062, 80.6480, 'Vijayawada', 'Andhra Pradesh'),
    'bhubaneswar': (20.2961, 85.8245, 'Bhubaneswar', 'Odisha'),
    'cuttack': (20.4625, 85.8828, 'Cuttack', 'Odisha'),
    'ranchi': (23.3441, 85.3096, 'Ranchi', 'Jharkhand'),
    'kolkata': (22.5726, 88.3639, 'Kolkata', 'West Bengal'),
    'bardhaman': (23.2324, 87.8615, 'Bardhaman', 'West Bengal')
}

def resolve_location(
    query_or_district: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None
) -> Tuple[float, float, str]:
    """
    Resolves district or GPS coordinates into latitude, longitude, and user-facing location label.
    Prioritizes explicit GPS coordinates (with privacy rounding to 3 decimals).
    """
    if lat is not None and lon is not None:
        safe_lat = round(float(lat), 3)
        safe_lon = round(float(lon), 3)
        return safe_lat, safe_lon, 'आपके जीपीएस स्थान (GPS Location)'

    if query_or_district:
        normalized = query_or_district.strip().lower()
        for d_key, data in DISTRICT_COORDS.items():
            if d_key in normalized or data[2].lower() in normalized:
                return data[0], data[1], f"{data[2]}, {data[3]}"

    return DEFAULT_LATITUDE, DEFAULT_LONGITUDE, f"{DEFAULT_DISTRICT}, {DEFAULT_STATE}"

def get_weather_data(
    latitude: float = DEFAULT_LATITUDE,
    longitude: float = DEFAULT_LONGITUDE,
    location_name: str = 'उत्तर प्रदेश'
) -> Dict[str, Any]:
    """Retrieves current weather and 5-day agro-meteorological forecast via provider."""
    return default_weather_provider.fetch_weather(latitude, longitude, location_name)
