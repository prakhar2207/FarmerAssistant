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
    deficiencies_en = []
    excesses = []
    excesses_en = []
    amendments = []
    health_score = 100
    
    # 1. pH evaluation
    if ph < 6.5:
        ph_status = 'अम्लीय (Acidic)'
        ph_status_en = 'Acidic'
        health_score -= 15
        deficiencies.append('मिट्टी अम्लीय है, जिससे सूक्ष्म पोषक तत्वों की उपलब्धता बाधित होती है।')
        deficiencies_en.append('Soil is acidic (pH < 6.5), which restricts micronutrient availability.')
        amendments.append({
            'action': 'चूना (Lime) उपचार',
            'action_en': 'Agricultural Lime Treatment',
            'dose': '1.5 से 2.5 क्विंटल प्रति एकड़ बुझा हुआ चूना या डोलोमाइट जुताई के समय मिलाएं।',
            'dose_en': 'Apply 1.5 - 2.5 quintals/acre of slaked lime or dolomite during land preparation.',
            'importance': 'उच्च',
            'importance_en': 'High'
        })
    elif ph > 8.2:
        ph_status = 'क्षारीय (Alkaline / Saline)'
        ph_status_en = 'Alkaline / Saline'
        health_score -= 20
        excesses.append('मिट्टी क्षारीय है, सोडियम की मात्रा अधिक हो सकती है।')
        excesses_en.append('Soil is alkaline (pH > 8.2); excess sodium may cause dispersion and poor drainage.')
        amendments.append({
            'action': 'जिप्सम (Gypsum) प्रयोग',
            'action_en': 'Gypsum Amendment',
            'dose': '2 से 4 क्विंटल प्रति एकड़ कृषि जिप्सम खेत में डालकर पलेवा करें।',
            'dose_en': 'Apply 2 - 4 quintals/acre of agricultural gypsum followed by light irrigation.',
            'importance': 'अति आवश्यक',
            'importance_en': 'Critical'
        })
    else:
        ph_status = 'सामान्य व उत्तम (Normal / Ideal)'
        ph_status_en = 'Normal / Ideal'

    # 2. Organic Carbon (OC %)
    if oc < 0.5:
        oc_status = 'निम्न (Low)'
        oc_status_en = 'Low'
        health_score -= 20
        deficiencies.append('जैविक कार्बन (OC) बहुत कम है (< 0.5%)। इससे मिट्टी की जलधारण क्षमता और सूक्ष्मजीवी सक्रियता कमजोर है।')
        deficiencies_en.append('Organic Carbon (OC) is low (< 0.5%), lowering water holding capacity and microbial biomass.')
        amendments.append({
            'action': 'जीवांश खाद एवं हरी खाद',
            'action_en': 'Organic & Green Manuring',
            'dose': 'प्रति एकड़ 4-5 ट्रॉली सड़ी गोबर खाद या 1-2 टन वर्मीकम्पोस्ट डालें। ढैंचा या सनई की हरी खाद पलटें।',
            'dose_en': 'Incorporate 4-5 trolley loads of well-rotted FYM or 1-2 tonnes vermicompost. Squeeze in Dhaincha green manure.',
            'importance': 'उच्च',
            'importance_en': 'High'
        })
    elif oc <= 0.75:
        oc_status = 'मध्यम (Medium)'
        oc_status_en = 'Medium'
    else:
        oc_status = 'उत्तम (High / Sufficient)'
        oc_status_en = 'Optimal / High'

    # 3. Nitrogen (N kg/ha)
    if n < 280:
        n_status = 'कम (Deficient)'
        n_status_en = 'Low / Deficient'
        health_score -= 15
        deficiencies.append(f'उपलब्ध नाइट्रोजन कम है ({n:.1f} kg/ha, सामान्य स्तर > 280 होना चाहिए)।')
        deficiencies_en.append(f'Available Nitrogen is deficient ({n:.1f} kg/ha; normal benchmark > 280 kg/ha).')
    elif n > 560:
        n_status = 'अधिक (Excess)'
        n_status_en = 'Excess'
        health_score -= 5
        excesses.append(f'नाइट्रोजन अत्यधिक है ({n:.1f} kg/ha)। अत्यधिक यूरिया से बचें।')
        excesses_en.append(f'Available Nitrogen is high ({n:.1f} kg/ha). Avoid excess urea to prevent lodging.')
    else:
        n_status = 'मध्यम / संतुलित (Optimal)'
        n_status_en = 'Optimal'

    # 4. Phosphorus (P kg/ha)
    if p < 10:
        p_status = 'कम (Deficient)'
        p_status_en = 'Low / Deficient'
        health_score -= 15
        deficiencies.append(f'फॉस्फोरस की कमी है ({p:.1f} kg/ha, न्यूनतम 10-25 होना चाहिए)।')
        deficiencies_en.append(f'Available Phosphorus is low ({p:.1f} kg/ha; recommended 10-25 kg/ha).')
        amendments.append({
            'action': 'फॉस्फेटिक खाद',
            'action_en': 'Phosphatic Fertilizer',
            'dose': 'बुवाई के समय DAP (40-50 किग्रा/एकड़) या SSP (100 किग्रा/एकड़) का प्रयोग करें।',
            'dose_en': 'Apply DAP (40-50 kg/acre) or Single Super Phosphate (100 kg/acre) at sowing.',
            'importance': 'मध्यम',
            'importance_en': 'Medium'
        })
    elif p > 25:
        p_status = 'पर्याप्त / अधिक (High)'
        p_status_en = 'High / Sufficient'
    else:
        p_status = 'मध्यम (Optimal)'
        p_status_en = 'Optimal'

    # 5. Potassium (K kg/ha)
    if k < 110:
        k_status = 'कम (Deficient)'
        k_status_en = 'Low / Deficient'
        health_score -= 10
        deficiencies.append(f'पोटाश की कमी है ({k:.1f} kg/ha, न्यूनतम > 110 होना चाहिए)।')
        deficiencies_en.append(f'Available Potassium is low ({k:.1f} kg/ha; recommended > 110 kg/ha).')
        amendments.append({
            'action': 'म्यूरेट ऑफ पोटाश (MOP)',
            'action_en': 'Muriate of Potash (MOP)',
            'dose': 'प्रति एकड़ 20-25 किग्रा MOP (0:0:60) का उपयोग करें।',
            'dose_en': 'Apply 20-25 kg/acre of MOP (0:0:60) basal or split dose.',
            'importance': 'मध्यम',
            'importance_en': 'Medium'
        })
    elif k > 280:
        k_status = 'पर्याप्त (High)'
        k_status_en = 'High / Sufficient'
    else:
        k_status = 'मध्यम (Optimal)'
        k_status_en = 'Optimal'

    # 6. Micronutrients (Zn, S)
    if zn < 0.6:
        deficiencies.append(f'जिंक (Zn) की कमी ({zn} ppm)।')
        deficiencies_en.append(f'Zinc deficiency ({zn} ppm; threshold 0.6 ppm).')
        amendments.append({
            'action': 'जिंक सल्फेट 21%',
            'action_en': 'Zinc Sulphate 21%',
            'dose': 'प्रति एकड़ 10 किग्रा जिंक सल्फेट बुवाई से पूर्व मिट्टी में मिलाएं।',
            'dose_en': 'Apply 10 kg/acre Zinc Sulphate to soil prior to sowing.',
            'importance': 'उच्च',
            'importance_en': 'High'
        })
    if s < 10.0:
        deficiencies.append(f'सल्फर/गंधक की कमी ({s} ppm)।')
        deficiencies_en.append(f'Sulphur deficiency ({s} ppm; threshold 10 ppm).')
        amendments.append({
            'action': 'सल्फर 90% दानेदार',
            'action_en': 'Bentonite Sulphur 90%',
            'dose': 'प्रति एकड़ 3-4 किग्रा बेंटोनाइट सल्फर का प्रयोग करें।',
            'dose_en': 'Apply 3-4 kg/acre Bentonite Sulphur granules.',
            'importance': 'मध्यम',
            'importance_en': 'Medium'
        })

    health_score = max(35, min(100, health_score))
    soil_type_info = estimate_soil_type(ph, state)

    summary_hi = f'मृदा स्वास्थ्य सूचकांक {health_score}/100 है। मिट्टी की प्रकृति {ph_status} है तथा जैविक कार्बन स्तर {oc_status} है। ' + (f'{len(deficiencies)} मुख्य कमियां पाई गईं।' if deficiencies else 'सभी प्रमुख पोषक तत्व संतुलित स्तर पर हैं।')
    summary_en = f'Soil Health Score is {health_score}/100. Soil condition is {ph_status_en} and organic carbon is {oc_status_en}. ' + (f'{len(deficiencies_en)} key nutrient deficiencies identified.' if deficiencies_en else 'All major nutrients are at optimal levels.')

    return {
        'health_score': health_score,
        'parameters': {
            'pH': {'value': ph, 'status': ph_status, 'status_en': ph_status_en, 'ideal_range': '6.5 - 7.5'},
            'EC': {'value': ec, 'status': 'सामान्य' if ec < 1.5 else 'लवणता अधिक', 'status_en': 'Normal' if ec < 1.5 else 'Saline', 'unit': 'dS/m'},
            'Organic_Carbon': {'value': oc, 'status': oc_status, 'status_en': oc_status_en, 'unit': '%', 'ideal_range': '> 0.75%'},
            'Nitrogen': {'value': n, 'status': n_status, 'status_en': n_status_en, 'unit': 'kg/ha', 'ideal_range': '280 - 560 kg/ha'},
            'Phosphorus': {'value': p, 'status': p_status, 'status_en': p_status_en, 'unit': 'kg/ha', 'ideal_range': '10 - 25 kg/ha'},
            'Potassium': {'value': k, 'status': k_status, 'status_en': k_status_en, 'unit': 'kg/ha', 'ideal_range': '110 - 280 kg/ha'},
            'Zinc': {'value': zn, 'status': 'पर्याप्त' if zn >= 0.6 else 'कमी', 'status_en': 'Adequate' if zn >= 0.6 else 'Deficient', 'unit': 'ppm'},
            'Iron': {'value': fe, 'status': 'पर्याप्त' if fe >= 4.5 else 'कमी', 'status_en': 'Adequate' if fe >= 4.5 else 'Deficient', 'unit': 'ppm'},
            'Sulphur': {'value': s, 'status': 'पर्याप्त' if s >= 10.0 else 'कमी', 'status_en': 'Adequate' if s >= 10.0 else 'Deficient', 'unit': 'ppm'}
        },
        'soil_classification': soil_type_info,
        'deficiencies': deficiencies,
        'deficiencies_en': deficiencies_en,
        'excesses': excesses,
        'excesses_en': excesses_en,
        'amendments': amendments,
        'hindi_summary': summary_hi,
        'english_summary': summary_en
    }
