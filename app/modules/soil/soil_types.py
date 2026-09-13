# Indian Soil Classification & Agronomic Properties

INDIAN_SOIL_CLASSES = {
    'alluvial': {
        'name_hindi': 'जलोढ़ मिट्टी (Alluvial Soil)',
        'regions': ['गंगा-यमुना दोआब', 'उत्तर प्रदेश', 'पंजाब', 'हरियाणा', 'बिहार', 'पश्चिम बंगाल'],
        'properties': 'बहुत उपजाऊ, पोटाश और चूने से भरपूर, लेकिन नाइट्रोजन और जैविक कार्बन की कमी।',
        'crops': ['गेहूं', 'धान', 'गन्ना', 'मक्का', 'दलहन', 'तिलहन', 'सब्जियां'],
        'management': 'हरी खाद (ढैंचा) और गोबर की सड़ी खाद का उपयोग करें। नाइट्रोजन संतुलित मात्रा में दें।'
    },
    'black': {
        'name_hindi': 'काली मिट्टी / रेगुर (Black / Regur Soil)',
        'regions': ['दक्कन का पठार', 'महाराष्ट्र', 'मध्य प्रदेश', 'गुजरात', 'आंध्र प्रदेश'],
        'properties': 'चिकनी मिट्टी, उच्च जलधारण क्षमता, नमी सूखने पर दरारें, कैल्शियम और मैग्नीशियम से भरपूर, फॉस्फोरस कम।',
        'crops': ['कपास', 'सोयाबीन', 'चना', 'ज्वार', 'गेहूं', 'अलसी'],
        'management': 'जल निकासी का उचित प्रबंध रखें। डीएपी या सिंगल सुपर फॉस्फेट (SSP) से फॉस्फोरस की पूर्ति करें।'
    },
    'red': {
        'name_hindi': 'लाल और पीली मिट्टी (Red & Yellow Soil)',
        'regions': ['तमिलनाडु', 'कर्नाटक', 'ओडिशा', 'झारखंड', 'मध्य प्रदेश का पूर्वी भाग'],
        'properties': 'लोहा प्रचुर मात्रा में (लाल रंग), नाइट्रोजन, फॉस्फोरस और ह्यूमस की कमी, हल्की और छिद्रयुक्त।',
        'crops': ['बाजरा', 'मूंगफली', 'दलहन', 'तंबाकू', 'आलू', 'रागी'],
        'management': 'पर्याप्त सिंचाई और जीवांश खाद (FYM/वर्मीकम्पोस्ट) डालें। फॉस्फोरस उर्वरक अवश्य मिलाएं।'
    },
    'laterite': {
        'name_hindi': 'लेटराइट मिट्टी (Laterite Soil)',
        'regions': ['पश्चिमी घाट', 'केरल', 'कर्नाटक', 'असम की पहाड़ियां'],
        'properties': 'अत्यधिक वर्षा से निक्षालित (leached), अम्लीय प्रकृति, नाइट्रोजन, पोटाश और चूने की अत्यधिक कमी।',
        'crops': ['काजू', 'चाय', 'कॉफी', 'रबड़', 'नारियल'],
        'management': 'चूना (Lime) डालकर अम्लीयता कम करें। पोटाश और फास्फोरस की नियमित पूर्ति करें।'
    },
    'arid': {
        'name_hindi': 'मरुस्थलीय / रेतीली मिट्टी (Arid / Desert Soil)',
        'regions': ['पश्चिमी राजस्थान', 'उत्तरी गुजरात', 'दक्षिणी हरियाणा'],
        'properties': 'रेतीली संरचना, कम जलधारण क्षमता, घुलनशील लवण अधिक, जैविक पदार्थ नगण्य।',
        'crops': ['बाजरा', 'ज्वार', 'ग्वार', 'मोठ', 'तिल', 'अनार'],
        'management': 'ड्रिप सिंचाई (टपक सिंचाई) अपनाएं। जैविक मल्चिंग करें ताकि नमी उड़ने से बचे।'
    }
}

def estimate_soil_type(ph: float, state: str = '', texture: str = '') -> dict:
    state_lower = state.lower()
    if 'maharashtra' in state_lower or 'madhya' in state_lower or 'gujarat' in state_lower:
        return INDIAN_SOIL_CLASSES['black']
    elif 'punjab' in state_lower or 'haryana' in state_lower or 'uttar' in state_lower or 'bihar' in state_lower or 'bengal' in state_lower:
        return INDIAN_SOIL_CLASSES['alluvial']
    elif 'rajasthan' in state_lower:
        return INDIAN_SOIL_CLASSES['arid']
    elif 'kerala' in state_lower or 'karnataka' in state_lower:
        return INDIAN_SOIL_CLASSES['red'] if ph >= 6.0 else INDIAN_SOIL_CLASSES['laterite']
    return INDIAN_SOIL_CLASSES['alluvial']
