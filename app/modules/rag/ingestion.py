import json
from pathlib import Path
from typing import List, Dict, Any

KNOWLEDGE_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "icar_knowledge.json"

EXTENDED_ICAR_DOCS = [
    {
        "id": "icar-wheat-fert-01",
        "crop": "गेहूं (Wheat)",
        "crop_key": "wheat",
        "category": "Nutrient Management",
        "authority": "ICAR",
        "title": "गेहूं में संतुलित उर्वरक प्रबंधन एवं नत्रजन विभाजन (ICAR-IIWBR Guidelines)",
        "source": "भारतीय कृषि अनुसंधान परिषद - गेहूं एवं जौ अनुसंधान संस्थान (ICAR-IIWBR, Karnal 2023)",
        "content": "गेहूं की सिंचित समय पर बुवाई में 120-150 किग्रा नत्रजन, 60 किग्रा फास्फोरस (DAP) तथा 40 किग्रा पोटाश प्रति हेक्टेयर दें। फास्फोरस व पोटाश की पूरी मात्रा तथा नत्रजन की एक तिहाई मात्रा बुवाई के समय कूंड़ों में दें। शेष नत्रजन को दो बराबर भागों में पहली सिंचाई (सीआरआई 21 दिन) और दूसरी सिंचाई (कल्ले निकलते समय 40-45 दिन) पर टॉप ड्रेसिंग करें। बारिश की संभावना होने पर यूरिया का छिड़काव रोक दें।",
        "tags": ["wheat", "गेहूं", "fertilizer", "urea", "dap", "potash", "irrigation", "cri"]
    },
    {
        "id": "icar-tomato-blight-02",
        "crop": "टमाटर (Tomato)",
        "crop_key": "tomato",
        "category": "Plant Pathology",
        "authority": "ICAR",
        "title": "टमाटर में अगेती एवं पछेती झुलसा का एकीकृत वैज्ञानिक नियंत्रण (ICAR-IIVR)",
        "source": "भारतीय सब्जी अनुसंधान संस्थान (ICAR-IIVR, Varanasi 2023)",
        "content": "टमाटर में अगेती झुलसा (अल्टरनेरिया) में संकेंद्री छल्लेदार धब्बे बनते हैं जबकि पछेती झुलसा (फाइटोफ्थोरा) में पत्तियों पर जलसिक्त काले धब्बे और निचली सतह पर सफेद फफूंद दिखती है। रोकथाम: लक्षण दिखते ही मैंकोजेब 75% डब्ल्यूपी @ 2.5 ग्राम/लीटर या साइमोक्सानिल + मैंकोजेब (Curzate M8) @ 2 ग्राम/लीटर का छिड़काव करें। बारिश से पहले कभी स्प्रे न करें। जैविक नियंत्रण हेतु ट्राइकोडर्मा विरिडी 5 ग्राम/लीटर प्रयोग करें।",
        "tags": ["tomato", "टमाटर", "early blight", "late blight", "mancozeb", "curzate", "fungicide"]
    },
    {
        "id": "cibrc-banned-alternatives-01",
        "crop": "सभी फसलें (All Crops)",
        "crop_key": "general",
        "category": "Chemical Safety",
        "authority": "CIBRC",
        "title": "प्रतिबंधित कीटनाशक एवं सुरक्षित अनुशंसित विकल्प (CIBRC Safety Advisory)",
        "source": "केंद्रीय कीटनाशक बोर्ड एवं पंजीकरण समिति (CIBRC, Govt of India 2024)",
        "content": "मोनोक्रोटोफॉस (Monocrotophos), एंडोसल्फान (Endosulfan), फोरेट (Phorate) और पैराक्वॉट (Paraquat Dichloride) भारत सरकार द्वारा अत्यंत विषैले होने के कारण सब्जियों/खाद्य फसलों में पूर्णतया प्रतिबंधित हैं। रस चूसक कीटों (माहू, थ्रिप्स, सफेद मक्खी) हेतु सुरक्षित विकल्प: इमिडाक्लोप्रिड 17.8% एसएल (0.5 मिली/लीटर) या जैविक नीम तेल 1500 पीपीएम (3-4 मिली/लीटर)। इल्ली व सुंडी हेतु कोराजन (क्लोरेंट्रानिलिप्रोल 18.5% एससी) 0.4 मिली/लीटर प्रयोग करें।",
        "tags": ["cibrc", "safety", "banned", "monocrotophos", "endosulfan", "imidacloprid", "neem"]
    },
    {
        "id": "kvk-natural-jeevamrut-01",
        "crop": "प्राकृतिक खेती (Natural Farming)",
        "crop_key": "organic",
        "category": "Organic Inputs",
        "authority": "KVK",
        "title": "प्राकृतिक खेती: जीवामृत एवं नीमास्त्र निर्माण विधि (KVK Advisory)",
        "source": "कृषि विज्ञान केंद्र (KVK Lucknow / ICAR-ATARI)",
        "content": "जीवामृत तैयार करने की विधि: 200 लीटर पानी में 10 किग्रा देसी गाय का गोबर, 10 लीटर गोमूत्र, 2 किग्रा गुड़, 2 किग्रा बेसन और 1 मुट्ठी खेत की मेड़ की सजीव मिट्टी मिलाएं। 48-72 घंटे छाया में किण्वन होने दें। दिन में दो बार लकड़ी के डंडे से घड़ी की दिशा में हिलाएं। यह 1 एकड़ खेत में सिंचाई के पानी के साथ या 10% छानकर पर्ण स्प्रे के रूप में मृदा सूक्ष्मजीव बढ़ाने के लिए सर्वोत्तम है।",
        "tags": ["jeevamrut", "organic", "kvk", "natural farming", "cow dung", "biofertilizer"]
    },
    {
        "id": "icar-potato-late-blight-01",
        "crop": "आलू (Potato)",
        "crop_key": "potato",
        "category": "Plant Pathology",
        "authority": "ICAR",
        "title": "आलू का पछेती झुलसा: पूर्वानुमान एवं त्वरित रोकथाम (ICAR-CPRI)",
        "source": "केंद्रीय आलू अनुसंधान संस्थान (ICAR-CPRI, Shimla)",
        "content": "बादल छाए रहने, लगातार नमी (>85%) और 10-20°C तापमान पर आलू में पछेती झुलसा का प्रकोप तेजी से होता है। रोग आने से पूर्व सुरक्षात्मक रूप से मैंकोजेब (2.5 ग्राम/ली) का स्प्रे करें। रोग के धब्बे दिखने पर तुरंत सिस्टेमिक फफूंदनाशी मेटालैक्सिल 8% + मैंकोजेब 64% (रिडोमिल गोल्ड) 2.5 ग्राम प्रति लीटर की दर से छिड़कें। यदि 24 घंटे में बारिश का अंदेशा हो तो स्प्रे स्थगित करें।",
        "tags": ["potato", "आलू", "late blight", "ridomil", "mancozeb", "cpri"]
    }
]

def get_ingested_knowledge() -> List[Dict[str, Any]]:
    """Loads base ICAR knowledge and merges with extended scientific guidelines."""
    chunks = []
    if KNOWLEDGE_FILE.exists():
        try:
            with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
                base_docs = json.load(f)
                for doc in base_docs:
                    doc_copy = dict(doc)
                    if "authority" not in doc_copy:
                        doc_copy["authority"] = "ICAR"
                    if "crop_key" not in doc_copy:
                        c = doc_copy.get("crop", "").lower()
                        if "wheat" in c or "गेहूं" in c:
                            doc_copy["crop_key"] = "wheat"
                        elif "rice" in c or "धान" in c:
                            doc_copy["crop_key"] = "rice"
                        elif "tomato" in c or "टमाटर" in c:
                            doc_copy["crop_key"] = "tomato"
                        else:
                            doc_copy["crop_key"] = "general"
                    chunks.append(doc_copy)
        except Exception:
            pass

    # Merge extended docs (avoiding duplicate IDs)
    existing_ids = {c.get("id") for c in chunks}
    for ext_doc in EXTENDED_ICAR_DOCS:
        if ext_doc["id"] not in existing_ids:
            chunks.append(ext_doc)

    return chunks
