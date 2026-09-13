from typing import List, Dict, Any

# Indian Government Soil Testing Laboratories & KVKs Directory
GOVT_SOIL_LABS = [
    {
        "state": "Uttar Pradesh",
        "district": "Lucknow",
        "name": "केन्द्रीय उपोष्ण बागवानी संस्थान (ICAR-CISH) एवं मृदा परीक्षण प्रयोगशाला",
        "address": "रहमानखेड़ा, काकोरी, लखनऊ, उत्तर प्रदेश 226101",
        "contact": "0522-2841022 / 1800-180-1551",
        "type": "ICAR संस्थान / सरकारी प्रयोगशाला",
        "fee": "मृदा स्वास्थ्य कार्ड धारकों के लिए निःशुल्क / सामान्य नमूना ₹20"
    },
    {
        "state": "Uttar Pradesh",
        "district": "Varanasi",
        "name": "भारतीय सब्जी अनुसंधान संस्थान (ICAR-IIVR) मृदा जांच केंद्र",
        "address": "जक्खिनी, शाहंशाहपुर, वाराणसी, उत्तर प्रदेश 221305",
        "contact": "0542-2635293",
        "type": "ICAR प्रयोगशाला",
        "fee": "निःशुल्क (सरकारी योजना अंतर्गत)"
    },
    {
        "state": "Uttar Pradesh",
        "district": "Kanpur",
        "name": "चंद्रशेखर आजाद कृषि एवं प्रौद्योगिकी विश्वविद्यालय (CSAUAT) मृदा परीक्षण लैब",
        "address": "कृषि नगर, नवाबगंज, कानपुर, उत्तर प्रदेश 208002",
        "contact": "0512-2534157",
        "type": "राज्य कृषि विश्वविद्यालय (SAU)",
        "fee": "₹25 प्रति नमूना"
    },
    {
        "state": "Haryana",
        "district": "Karnal",
        "name": "केन्द्रीय मृदा लवणता अनुसंधान संस्थान (ICAR-CSSRI) मृदा परीक्षण प्रयोगशाला",
        "address": "जरीफा फार्म, कछवा रोड, करनाल, हरियाणा 132001",
        "contact": "0184-2290501",
        "type": "ICAR राष्ट्रीय संस्थान",
        "fee": "निःशुल्क (लवणता व क्षारीयता सुधार परामर्श सहित)"
    },
    {
        "state": "Punjab",
        "district": "Ludhiana",
        "name": "पंजाब कृषि विश्वविद्यालय (PAU) मृदा एवं जल परीक्षण प्रयोगशाला",
        "address": "फिरोजपुर रोड, लुधियाना, पंजाब 141004",
        "contact": "0161-2401960",
        "type": "राज्य कृषि विश्वविद्यालय",
        "fee": "₹30 प्रति नमूना"
    },
    {
        "state": "Bihar",
        "district": "Patna",
        "name": "जिला कृषि कार्यालय एवं सरकारी मृदा परीक्षण प्रयोगशाला",
        "address": "मीठापुर कृषि फार्म, पटना, बिहार 800001",
        "contact": "0612-2222384",
        "type": "जिला कृषि विभाग (बिहार सरकार)",
        "fee": "निःशुल्क"
    },
    {
        "state": "Madhya Pradesh",
        "district": "Bhopal",
        "name": "भारतीय मृदा विज्ञान संस्थान (ICAR-IISS) आदर्श मृदा परीक्षण केंद्र",
        "address": "नबीबाग, बैरसिया रोड, भोपाल, मध्य प्रदेश 462038",
        "contact": "0755-2730970",
        "type": "ICAR राष्ट्रीय मृदा संस्थान",
        "fee": "निःशुल्क"
    },
    {
        "state": "Rajasthan",
        "district": "Jaipur",
        "name": "कृषि अनुसंधान केंद्र (दुर्गापुरा) मृदा स्वास्थ्य प्रयोगशाला",
        "address": "टोंक रोड, दुर्गापुरा, जयपुर, राजस्थान 302018",
        "contact": "0141-2550229",
        "type": "राज्य कृषि विभाग",
        "fee": "₹20 प्रति नमूना"
    },
    {
        "state": "Maharashtra",
        "district": "Pune",
        "name": "कृषि विज्ञान केंद्र (KVK) बारामती / पुणे मृदा परीक्षण केंद्र",
        "address": "शारदानगर, मालेगांव रोड, बारामती, पुणे, महाराष्ट्र 413115",
        "contact": "02112-255207",
        "type": "KVK बारामती (ADT)",
        "fee": "₹50 (12 मापदंड व सूक्ष्म पोषक तत्व)"
    }
]

def find_nearby_soil_labs(state: str = "", district: str = "") -> List[Dict[str, Any]]:
    matched = []
    state_clean = state.strip().lower()
    dist_clean = district.strip().lower()
    
    for lab in GOVT_SOIL_LABS:
        l_state = lab["state"].lower()
        l_dist = lab["district"].lower()
        
        if dist_clean and dist_clean in l_dist:
            matched.append(lab)
        elif state_clean and (state_clean in l_state or l_state in state_clean):
            matched.append(lab)
            
    if not matched:
        # Return prominent national central labs as default
        return [GOVT_SOIL_LABS[0], GOVT_SOIL_LABS[6]]
    return matched[:3]
