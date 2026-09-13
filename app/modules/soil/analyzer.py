from typing import Dict, Any, List, Optional
from app.modules.soil.soil_types import estimate_soil_type

def analyze_soil_metrics(
    ph: Optional[float] = 7.2,
    ec: Optional[float] = 0.4,
    oc: Optional[float] = 0.55,
    n: Optional[float] = 240.0,
    p: Optional[float] = 14.0,
    k: Optional[float] = 160.0,
    zn: Optional[float] = 0.8,
    fe: Optional[float] = 5.2,
    s: Optional[float] = 12.0,
    b: Optional[float] = None,
    state: str = 'Uttar Pradesh',
    crop_context: Optional[str] = None,
    crop_key: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    effective_crop = crop_context or crop_key

    # Sanitize None values to standard agronomic reference values
    ph = float(ph) if ph is not None else 7.2
    ec = float(ec) if ec is not None else 0.4
    oc = float(oc) if oc is not None else 0.55
    n = float(n) if n is not None else 240.0
    p = float(p) if p is not None else 14.0
    k = float(k) if k is not None else 160.0
    zn = float(zn) if zn is not None else 0.8
    fe = float(fe) if fe is not None else 5.2
    s = float(s) if s is not None else 12.0


    """
    Transparent Soil Health Scoring & Amendment Recommendation
    Grounded in ICAR & National Soil Health Card Benchmarks.
    """
    deficiencies = []
    deficiencies_en = []
    excesses = []
    excesses_en = []
    amendments = []
    
    # Transparent Component Scores (Total 100)
    score_ph = 25.0
    score_oc = 25.0
    score_npk = 30.0
    score_micro = 20.0

    # 1. Soil Reaction (pH) Evaluation (25 pts)
    if ph < 6.0:
        ph_status = 'अत्यधिक अम्लीय (Strongly Acidic)'
        ph_status_en = 'Strongly Acidic'
        score_ph = 10.0
        deficiencies.append('मिट्टी अत्यधिक अम्लीय (pH < 6.0) है। फास्फोरस एवं सूक्ष्म पोषक तत्वों का अवशोषण रुक जाता है।')
        deficiencies_en.append('Soil is strongly acidic (pH < 6.0); phosphorus fixation and aluminum toxicity occur.')
        amendments.append({
            'action': 'कृषि चूना या डोलोमाइट उपचार',
            'action_en': 'Agricultural Lime / Dolomite Treatment',
            'dose': '2 से 3 क्विंटल प्रति एकड़ बुझा हुआ चूना जुताई के समय खेत में समान रूप से मिलाएं।',
            'dose_en': 'Apply 2 - 3 quintals/acre of agricultural lime or dolomite during summer land preparation.',
            'importance': 'उच्च (High)',
            'importance_en': 'High'
        })
    elif ph < 6.5:
        ph_status = 'हल्की अम्लीय (Slightly Acidic)'
        ph_status_en = 'Slightly Acidic'
        score_ph = 18.0
        deficiencies.append('मिट्टी हल्की अम्लीय है। दलहनी फसलों में राइजोबियम सक्रियता धीमी हो सकती है।')
        deficiencies_en.append('Soil is moderately acidic. Microbial nitrogen fixation may be sluggish.')
    elif ph >= 8.5:
        ph_status = 'अत्यधिक क्षारीय (Strongly Alkaline / Sodic)'
        ph_status_en = 'Strongly Alkaline / Sodic'
        score_ph = 8.0
        excesses.append('मिट्टी अत्यधिक क्षारीय (pH >= 8.5) है। सोडियम की अधिकता से जल निकास बाधित होता है।')
        excesses_en.append('Soil is strongly alkaline/sodic (pH >= 8.5); sodium excess destroys soil aggregation.')
        amendments.append({
            'action': 'कृषि जिप्सम (Gypsum) प्रयोग',
            'action_en': 'Agricultural Gypsum Application',
            'dose': '3 से 5 क्विंटल प्रति एकड़ कृषि जिप्सम बिखेरकर गहरी जुताई करें और पलेवा करें।',
            'dose_en': 'Apply 3 - 5 quintals/acre agricultural gypsum, followed by deep plowing and ponding irrigation.',
            'importance': 'अति आवश्यक (Critical)',
            'importance_en': 'Critical'
        })
    elif ph >= 7.8:
        ph_status = 'क्षारीय (Alkaline)'
        ph_status_en = 'Alkaline'
        score_ph = 16.0
        excesses.append('मिट्टी क्षारीय (pH >= 7.8) है। जिंक व लोहे की उपलब्धता कम हो सकती है।')
        excesses_en.append('Soil is alkaline (pH >= 7.8); zinc and iron availability becomes limited.')
        amendments.append({
            'action': 'जिप्सम व जैविक खाद',
            'action_en': 'Gypsum & Organic FYM',
            'dose': '1.5 से 2 क्विंटल जिप्सम और 4-5 ट्रॉली सड़ी गोबर खाद डालें।',
            'dose_en': 'Apply 1.5 - 2 quintals gypsum combined with 4-5 trolley loads of well-rotted compost.',
            'importance': 'मध्यम (Medium)',
            'importance_en': 'Medium'
        })
    else:
        ph_status = 'आदर्श व संतुलित (Ideal Neutral)'
        ph_status_en = 'Ideal Neutral'
        score_ph = 25.0

    # 2. Organic Carbon (OC %) Evaluation (25 pts)
    if oc < 0.50:
        oc_status = 'अत्यधिक कम (Very Low)'
        oc_status_en = 'Deficient'
        score_oc = 8.0
        deficiencies.append('जैविक कार्बन (OC) गंभीर रूप से कम (< 0.5%) है। मिट्टी की जलधारण क्षमता और जीवाणु संख्या कमजोर है।')
        deficiencies_en.append('Organic Carbon is severely deficient (< 0.5%), lowering water retention and microbial activity.')
        amendments.append({
            'action': 'हरी खाद एवं वर्मीकम्पोस्ट संवर्धन',
            'action_en': 'Green Manuring & Vermicompost',
            'dose': 'प्रति एकड़ 4-5 ट्रॉली सड़ी गोबर खाद या 1.5 टन केंचुआ खाद (Vermicompost) डालें। ढैंचा की हरी खाद पलटें।',
            'dose_en': 'Apply 4-5 trolley loads well-rotted FYM or 1.5 tonnes vermicompost/acre. Incorporate green manure (Dhaincha).',
            'importance': 'अति आवश्यक (Critical)',
            'importance_en': 'Critical'
        })
    elif oc <= 0.75:
        oc_status = 'मध्यम (Medium)'
        oc_status_en = 'Medium'
        score_oc = 18.0
    else:
        oc_status = 'उत्तम (High / Optimal)'
        oc_status_en = 'High / Optimal'
        score_oc = 25.0

    # 3. Primary Macronutrients N, P, K (30 pts, 10 each)
    score_n = 10.0
    if n < 280.0:
        score_n = 4.0
        deficiencies.append(f'उपलब्ध नाइट्रोजन कम है ({n:.1f} kg/ha, मानक > 280 kg/ha)। पौधों में पीलापन व धीमा विकास संभव है।')
        deficiencies_en.append(f'Available Nitrogen is low ({n:.1f} kg/ha; benchmark > 280 kg/ha). Risk of chlorosis.')
    elif n > 560.0:
        score_n = 7.0
        excesses.append(f'नाइट्रोजन अत्यधिक है ({n:.1f} kg/ha)। अतिरिक्त यूरिया से तने कमजोर होकर फसल गिर सकती है।')
        excesses_en.append(f'Available Nitrogen is excessive ({n:.1f} kg/ha). Risk of vegetative lodging.')

    score_p = 10.0
    if p < 11.0:
        score_p = 4.0
        deficiencies.append(f'उपलब्ध फॉस्फोरस कम है ({p:.1f} kg/ha, मानक > 11 kg/ha)। जड़ विकास व कल्ले फूटना बाधित होगा।')
        deficiencies_en.append(f'Available Phosphorus is low ({p:.1f} kg/ha; benchmark > 11 kg/ha). Affects root proliferation.')
        amendments.append({
            'action': 'डीएपी या सिंगल सुपर फॉस्फेट (SSP)',
            'action_en': 'Single Super Phosphate (SSP) Application',
            'dose': 'बुवाई के समय 1 बैग डीएपी या 3 बैग एसएसपी प्रति एकड़ आधार खाद (Basal dose) के रूप में दें।',
            'dose_en': 'Apply 1 bag DAP or 3 bags SSP per acre as basal fertilizer during sowing.',
            'importance': 'उच्च (High)',
            'importance_en': 'High'
        })
    elif p > 25.0:
        score_p = 8.0

    score_k = 10.0
    if k < 120.0:
        score_k = 4.0
        deficiencies.append(f'उपलब्ध पोटाश कम है ({k:.1f} kg/ha, मानक > 120 kg/ha)। दाना भराव एवं सूखा/रोग प्रतिरोधक क्षमता कमजोर होगी।')
        deficiencies_en.append(f'Available Potassium is deficient ({k:.1f} kg/ha; benchmark > 120 kg/ha). Affects grain plumpness.')
        amendments.append({
            'action': 'म्यूरेट ऑफ पोटाश (MOP) प्रयोग',
            'action_en': 'Muriate of Potash (MOP)',
            'dose': 'प्रति एकड़ 20-25 किग्रा पोटाश (MOP) बुवाई के समय खेत में मिलाएं।',
            'dose_en': 'Incorporate 20-25 kg MOP per acre into soil prior to final harrowing.',
            'importance': 'मध्यम (Medium)',
            'importance_en': 'Medium'
        })
    elif k > 280.0:
        score_k = 8.0

    score_npk = score_n + score_p + score_k

    # 4. Secondary & Micronutrients (20 pts)
    # Zinc (Zn ppm, benchmark > 0.6)
    if zn is not None:
        if zn < 0.6:
            score_micro -= 8.0
            deficiencies.append(f'जिंक (Zn) की कमी है ({zn:.2f} ppm, मानक > 0.6 ppm)। खैरा रोग या पत्तियों में झुलसा लक्षण दिख सकते हैं।')
            deficiencies_en.append(f'Zinc deficiency ({zn:.2f} ppm; benchmark > 0.6 ppm). Risk of Khaira disease.')
            amendments.append({
                'action': 'जिंक सल्फेट (Zinc Sulphate 21%)',
                'action_en': 'Zinc Sulphate (21%) Application',
                'dose': 'प्रति एकड़ 10 किग्रा जिंक सल्फेट बुवाई से पूर्व मिट्टी में मिलाएं या 5 ग्राम/लीटर का पर्णीय छिड़काव करें।',
                'dose_en': 'Apply 10 kg zinc sulphate per acre to soil before sowing or 5g/L foliar spray.',
                'importance': 'उच्च (High)',
                'importance_en': 'High'
            })
    
    # Sulphur (S ppm, benchmark > 10.0)
    if s is not None:
        if s < 10.0:
            score_micro -= 6.0
            deficiencies.append(f'सल्फर (गंधक) कम है ({s:.1f} ppm, मानक > 10.0 ppm)। तिलहन व दलहन में तेल व प्रोटीन घटेगा।')
            deficiencies_en.append(f'Sulphur deficiency ({s:.1f} ppm; benchmark > 10 ppm). Reduces oil content in oilseeds.')
            amendments.append({
                'action': 'कृषि सल्फर / बेंटोनाइट सल्फर',
                'action_en': 'Agricultural Sulphur 90%',
                'dose': 'प्रति एकड़ 8-10 किग्रा बेंटोनाइट सल्फर का प्रयोग करें।',
                'dose_en': 'Apply 8-10 kg agricultural bentonite sulphur per acre.',
                'importance': 'मध्यम (Medium)',
                'importance_en': 'Medium'
            })

    # Total Score Calculation (0-100)
    final_health_score = max(10, min(100, round(score_ph + score_oc + score_npk + max(0, score_micro))))

    # Soil Classification based on physical and chemical status
    soil_class = estimate_soil_type(ph, state)

    hindi_summary = (
        f"मृदा स्वास्थ्य स्कोर: {final_health_score}/100। "
        f"मिट्टी का प्रकार: {soil_class['name_hindi']} (pH: {ph_status})। "
        f"जैविक कार्बन स्तर: {oc_status} ({oc}%)। "
        f"{'कुल ' + str(len(deficiencies)) + ' पोषक तत्वों में कमी पाई गई है।' if deficiencies else 'सभी प्रमुख पोषक तत्व संतुलित अवस्था में हैं।'}"
    )

    english_summary = (
        f"Soil Health Index: {final_health_score}/100. "
        f"Classification: {soil_class['name_english']} (pH: {ph_status_en}). "
        f"Organic Carbon: {oc_status_en} ({oc}%). "
        f"{str(len(deficiencies)) + ' nutrient deficiencies detected.' if deficiencies else 'Major nutrients are within optimal benchmarks.'}"
    )

    return {
        "success": True,
        "health_score": final_health_score,
        "score_breakdown": {
            "ph_score": score_ph,
            "organic_carbon_score": score_oc,
            "npk_score": score_npk,
            "micronutrient_score": max(0, score_micro)
        },
        "soil_classification": soil_class,
        "parameters": {
            "pH": {"value": ph, "status": ph_status, "status_en": ph_status_en},
            "OC": {"value": oc, "status": oc_status, "status_en": oc_status_en},
            "N": {"value": n},
            "P": {"value": p},
            "K": {"value": k},
        },
        "ph_status": ph_status,
        "ph_status_en": ph_status_en,
        "oc_status": oc_status,
        "oc_status_en": oc_status_en,
        "deficiencies": deficiencies,
        "deficiencies_en": deficiencies_en,
        "excesses": excesses,
        "excesses_en": excesses_en,
        "amendments": amendments,
        "hindi_summary": hindi_summary,
        "english_summary": english_summary
    }
