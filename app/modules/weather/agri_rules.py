from typing import Dict, Any, List

def generate_agricultural_weather_advisories(weather_data: Dict[str, Any]) -> List[Dict[str, str]]:
    current = weather_data.get('current', {})
    forecast = weather_data.get('forecast', [])
    temp = current.get('temperature', 28.0)
    humidity = current.get('humidity', 60)
    wind_speed = current.get('wind_speed', 8.0)
    
    max_rain_prob = max([day.get('rain_prob', 0) for day in forecast[:3]] or [0])
    total_rain_expected = sum([day.get('rain_sum_mm', 0) for day in forecast[:3]])
    
    advisories = []
    
    # 1. Spray Advisory (कीटनाशक व पर्ण उर्वरक छिड़काव)
    if max_rain_prob >= 40 or total_rain_expected > 5.0:
        advisories.append({
            'type': 'warning',
            'title': '⚠️ कीटनाशक/उर्वरक छिड़काव स्थगित करें (Hold Spraying)',
            'advice': 'अगले 48-72 घंटों में बारिश की संभावना है। पर्ण छिड़काव करने से दवा पानी में बह जाएगी और व्यर्थ होगी।'
        })
    elif wind_speed > 15.0:
        advisories.append({
            'type': 'warning',
            'title': '⚠️ तेज हवा की चेतावनी (High Wind Alert)',
            'advice': f'हवा की गति {wind_speed} किमी/घंटा है। दवा का छिड़काव न करें क्योंकि हवा से दवा उड़ जाएगी (Drift)।'
        })
    else:
        advisories.append({
            'type': 'safe',
            'title': '✅ छिड़काव के लिए उपयुक्त समय (Safe for Spraying)',
            'advice': 'मौसम शांत और साफ है। आवश्यक कीटनाशक या यूरिया/माइक्रोन्यूट्रीएंट का छिड़काव सुबह 8 से 11 बजे या शाम 4 बजे के बाद करें।'
        })
        
    # 2. Irrigation Scheduling (सिंचाई प्रबंधन)
    if total_rain_expected > 10.0:
        advisories.append({
            'type': 'info',
            'title': '💧 सिंचाई रोकें (Postpone Irrigation)',
            'advice': f'आगामी दिनों में लगभग {total_rain_expected:.1f} मिमी बारिश का अनुमान है। खेतों में पानी भराव से बचने के लिए सिंचाई टालें।'
        })
    elif temp > 35.0:
        advisories.append({
            'type': 'alert',
            'title': '🔥 उच्च तापमान व नमी संरक्षण (Heat Alert)',
            'advice': 'तापमान अधिक होने से पौधों में वाष्पीकरण बढ़ेगा। फसल में नमी बनाए रखने हेतु शाम के समय हल्की सिंचाई करें।'
        })
    else:
        advisories.append({
            'type': 'info',
            'title': '💧 सामान्य सिंचाई आवश्यकता (Routine Irrigation)',
            'advice': 'खेत में नमी की स्थिति देखकर ही सिंचाई करें। क्रांतिक अवस्था (CRI, कल्ले फूटना या फूल आते समय) पर पानी की कमी न होने दें।'
        })
        
    # 3. Disease Risk Warning (रोग जोखिम)
    if humidity > 80 and 18 <= temp <= 30:
        advisories.append({
            'type': 'danger',
            'title': '🍄 फफूंद जनित रोगों का उच्च जोखिम (Fungal Disease Risk)',
            'advice': f'उच्च आर्द्रता ({humidity}%) एवं अनुकूल तापमान के कारण झुलसा (Blight), रतुआ (Rust) या सड़न रोग फैलने की प्रबल संभावना है। नियमित रूप से पत्तियों की जांच करें।'
        })
        
    # 4. Frost Warning (शीत लहर व पाला)
    min_temp = min([day.get('temp_min', 20) for day in forecast] or [temp])
    if min_temp <= 4.0:
        advisories.append({
            'type': 'danger',
            'title': '❄️ पाला / शीत लहर की चेतावनी (Frost Alert)',
            'advice': 'तापमान 4°C से नीचे जाने पर पाला पड़ने की संभावना है। शाम के समय खेत की मेड़ों पर धुआं करें या हल्की सिंचाई करें जिससे खेत का तापमान 1-2°C बढ़ सके।'
        })
        
    return advisories
