from typing import Dict, Any, List
from app.modules.soil.soil_types import estimate_soil_type

def analyze_soil_metrics(
    ph: float = 7.2,
    ec: float = 0.4,
    oc: float = 0.55,
    n: float = 240.0,
    p: float = 14.0,
    k: float = 160.0,
    zn: float = 0.8,
    fe: float = 5.2,
    s: float = 12.0,
    state: str = 'Uttar Pradesh'
) -> Dict[str, Any]:
    
    status_summary = []
    deficiencies = []
    excesses = []
    amendments = []
    health_score = 100
    
    # 1. pH evaluation
    if ph < 6.5:
        ph_status = 'अम्लीय (Acidic)'
        health_score -= 15
        deficiencies.append('मिट्टी अम्लीय है, जिससे सूक्ष्म पोषक तत्वों की उपलब्धता बाधित होती है।')
        amendments.append({
            'action': 'चूना (Lime) उपचार',
            'dose': '1.5 से 2.5 क्विंटल प्रति एकड़ बुझा हुआ चूना या डोलोमाइट जुताई के समय मिलाएं।',
            'importance': 'उच्च'
        })
    elif ph > 8.2:
        ph_status = 'क्षारीय (Alkaline / Saline)'
        health_score -= 20
        excesses.append('मिट्टी क्षारीय है, सोडियम की मात्रा अधिक हो सकती है।')
        amendments.append({
            'action': 'जिप्सम (Gypsum) प्रयोग',
            'dose': '2 से 4 क्विंटल प्रति एकड़ कृषि जिप्सम खेत में डालकर पलेवा करें।',
            'importance': 'अति आवश्यक'
        })
    else:
        ph_status = 'सामान्य व उत्तम (Normal / Ideal)'

    # 2. Organic Carbon (OC %)
    if oc < 0.5:
        oc_status = 'निम्न (Low)'
        health_score -= 20
        deficiencies.append('जैविक कार्बन (OC) बहुत कम है (< 0.5%)। इससे मिट्टी की जलधारण क्षमता और सूक्ष्मजीवी सक्रियता कमजोर है।')
        amendments.append({
            'action': 'जीवांश खाद एवं हरी खाद',
            'dose': 'प्रति एकड़ 4-5 ट्रॉली सड़ी गोबर खाद या 1-2 टन वर्मीकम्पोस्ट डालें। खरीफ से पहले ढैंचा या सनई की हरी खाद पलटें।',
            'importance': 'उच्च'
        })
    elif oc <= 0.75:
        oc_status = 'मध्यम (Medium)'
    else:
        oc_status = 'उत्तम (High / Sufficient)'

    # 3. Nitrogen (N kg/ha)
    if n < 280:
        n_status = 'कम (Deficient)'
        health_score -= 15
        deficiencies.append(f'उपलब्ध नाइट्रोजन कम है ({n:.1f} kg/ha, सामान्य स्तर > 280 होना चाहिए)। फसल के कल्ले व पत्तियां पीली पड़ सकती हैं।')
    elif n > 560:
        n_status = 'अधिक (Excess)'
        health_score -= 5
        excesses.append(f'नाइट्रोजन अत्यधिक है ({n:.1f} kg/ha)। अत्यधिक यूरिया से बचें ताकि फसल गिरे नहीं और कीट न लगें।')
    else:
        n_status = 'मध्यम / संतुलित (Optimal)'

    # 4. Phosphorus (P kg/ha)
    if p < 10:
        p_status = 'कम (Deficient)'
        health_score -= 15
        deficiencies.append(f'फॉस्फोरस की कमी है ({p:.1f} kg/ha, न्यूनतम 10-25 होना चाहिए)। जड़ों का विकास धीमा रहेगा।')
        amendments.append({
            'action': 'फॉस्फेटिक खाद',
            'dose': 'बुवाई के समय DAP (40-50 किग्रा/एकड़) या सिंगल सुपर फॉस्फेट (SSP 100 किग्रा/एकड़) का प्रयोग करें।',
            'importance': 'मध्यम'
        })
    elif p > 25:
        p_status = 'पर्याप्त / अधिक (High)'
    else:
        p_status = 'मध्यम (Optimal)'

    # 5. Potassium (K kg/ha)
    if k < 110:
        k_status = 'कम (Deficient)'
        health_score -= 10
        deficiencies.append(f'पोटाश की कमी है ({k:.1f} kg/ha)। दानों की चमक और रोग प्रतिरोधक क्षमता प्रभावित हो सकती है।')
        amendments.append({
            'action': 'म्यूरेट ऑफ पोटाश (MOP)',
            'dose': 'प्रति एकड़ 20-25 किग्रा MOP (0:0:60) का उपयोग करें।',
            'importance': 'मध्यम'
        })
    elif k > 280:
        k_status = 'पर्याप्त (High)'
    else:
        k_status = 'मध्यम (Optimal)'

    # 6. Micronutrients (Zn, Fe, S)
    if zn < 0.6:
        deficiencies.append(f'जिंक (Zn) की कमी ({zn} ppm)। धान में खैरा रोग तथा मक्का में सफेद कलिका रोग का खतरा।')
        amendments.append({
            'action': 'जिंक सल्फेट 21%',
            'dose': 'प्रति एकड़ 10 किग्रा जिंक सल्फेट बुवाई से पूर्व मिट्टी में मिलाएं।',
            'importance': 'उच्च'
        })
    if s < 10.0:
        deficiencies.append(f'सल्फर/गंधक की कमी ({s} ppm)। तिलहन व दलहन फसलों में तेल की मात्रा घटेगी।')
        amendments.append({
            'action': 'सल्फर 90% दानेदार',
            'dose': 'प्रति एकड़ 3-4 किग्रा बेंटोनाइट सल्फर का प्रयोग करें।',
            'importance': 'मध्यम'
        })

    health_score = max(35, min(100, health_score))
    soil_type_info = estimate_soil_type(ph, state)

    return {
        'health_score': health_score,
        'parameters': {
            'pH': {'value': ph, 'status': ph_status, 'ideal_range': '6.5 - 7.5'},
            'EC': {'value': ec, 'status': 'सामान्य' if ec < 1.5 else 'लवणता अधिक', 'unit': 'dS/m'},
            'Organic_Carbon': {'value': oc, 'status': oc_status, 'unit': '%', 'ideal_range': '> 0.75%'},
            'Nitrogen': {'value': n, 'status': n_status, 'unit': 'kg/ha', 'ideal_range': '280 - 560 kg/ha'},
            'Phosphorus': {'value': p, 'status': p_status, 'unit': 'kg/ha', 'ideal_range': '10 - 25 kg/ha'},
            'Potassium': {'value': k, 'status': k_status, 'unit': 'kg/ha', 'ideal_range': '110 - 280 kg/ha'},
            'Zinc': {'value': zn, 'status': 'पर्याप्त' if zn >= 0.6 else 'कमी', 'unit': 'ppm'},
            'Iron': {'value': fe, 'status': 'पर्याप्त' if fe >= 4.5 else 'कमी', 'unit': 'ppm'},
            'Sulphur': {'value': s, 'status': 'पर्याप्त' if s >= 10.0 else 'कमी', 'unit': 'ppm'}
        },
        'soil_classification': soil_type_info,
        'deficiencies': deficiencies,
        'excesses': excesses,
        'amendments': amendments,
        'hindi_summary': f'मृदा स्वास्थ्य सूचकांक {health_score}/100 है। मिट्टी की प्रकृति {ph_status} है तथा जैविक कार्बन स्तर {oc_status} है। ' + (f'{len(deficiencies)} मुख्य कमियां पाई गईं।' if deficiencies else 'सभी प्रमुख पोषक तत्व संतुलित स्तर पर हैं।')
    }
