// KrishiSaathi Frontend Application Logic (Bilingual: Hindi + English)
let currentSessionId = "session_" + Math.random().toString(36).substring(2, 9);
let currentFarmerId = "default_farmer";
let currentLang = "hi";
let liveWeatherCache = null;

const I18N = {
  hi: {
    app_title: "कृषि साथी (KrishiSaathi)",
    app_subtitle: "भारतीय किसानों के लिए बुद्धिमान एजेंटिक कृषि परामर्श प्रणाली",
    tab_chat: "💬 कृषि मित्र चैट",
    tab_disease: "📸 फसल रोग जांच",
    tab_soil: "🧪 मृदा स्वास्थ्य कार्ड",
    tab_crop: "🌱 फसल चयन सलाहकार",
    tab_weather: "🌦️ मौसम व कृषि अलर्ट",
    tab_schemes: "🏛️ सरकारी योजनाएं",
    tab_profile: "👤 किसान प्रोफाइल",
    welcome_title: "नमस्ते किसान भाई! 🙏",
    welcome_desc: "मैं आपका डिजिटल कृषि साथी हूँ। आप मुझसे अपनी भाषा में बोलकर या लिखकर अपनी फसल, खाद, कीट-रोग, मौसम या सरकारी योजनाओं के बारे में पूछ सकते हैं।",
    speak_btn: "🔊 बोलकर सुनाएं",
    quick_services_title: "⚡ त्वरित कृषि सेवाएं",
    quick_services_desc: "विशिष्ट उपकरणों का सीधा उपयोग करें:",
    btn_check_leaf: "📸 पत्ती की फोटो जांचें",
    btn_check_soil: "🧪 मृदा स्वास्थ्य कार्ड विश्लेषण",
    btn_calc_crop: "🌱 सर्वोत्तम फसल की गणना",
    safety_title: "🛡️ किसान सुरक्षा गारंटी",
    safety_1: "प्रतिबंधित कीटनाशकों (Endosulfan आदि) पर पूर्ण रोक।",
    safety_2: "वर्षा व आंधी में छिड़काव रोकने की सुरक्षा चेतावनी।",
    safety_3: "ICAR एवं कृषि विज्ञान केंद्र (KVK) द्वारा संस्तुत प्रमाणिक उपाय।",
    disease_title: "📸 फसल रोग एवं पत्ती स्वास्थ्य जांच (AI Vision Diagnostic)",
    disease_subtitle: "अपनी फसल के प्रभावित पत्ते की स्पष्ट फोटो अपलोड करें। हमारा कंप्यूटर विज़न मॉडल रोग की पहचान कर जैविक व रासायनिक उपचार सुझाएगा।",
    lbl_crop_hint: "संबंधित फसल (वैकल्पिक):",
    opt_auto_detect: "स्वचालित पहचान (Auto Detect)",
    dropzone_title: "यहाँ पत्ते की फोटो खींचकर छोड़ें या क्लिक करके अपलोड करें",
    dropzone_desc: "JPG, PNG या WEBP समर्थित",
    soil_title: "🧪 मृदा स्वास्थ्य कार्ड विश्लेषण एवं सरकारी लैब खोजक",
    soil_subtitle: "अपनी मिट्टी जांच रिपोर्ट (Soil Health Card) के आंकड़े दर्ज करें। प्रणाली पोषक तत्वों की कमियां पहचान कर सुधार हेतु संस्तुति और नजदीकी लैब बताएगी।",
    lbl_ph: "पीएच मान (pH):",
    lbl_oc: "जैविक कार्बन (OC %):",
    lbl_n: "उपलब्ध नाइट्रोजन (N kg/ha):",
    lbl_p: "उपलब्ध फॉस्फोरस (P kg/ha):",
    lbl_k: "उपलब्ध पोटाश (K kg/ha):",
    lbl_ec: "विद्युत चालकता (EC dS/m):",
    lbl_zn: "जिंक (Zn ppm):",
    lbl_s: "सल्फर/गंधक (S ppm):",
    lbl_state: "राज्य (State):",
    lbl_district: "जिला (District):",
    btn_analyze_soil: "🧪 मिट्टी स्वास्थ्य कार्ड की जांच करें",
    crop_rec_title: "🌱 मशीन लर्निंग आधारित फसल चयन सलाहकार (Crop Recommendation)",
    crop_rec_subtitle: "अपनी मिट्टी के पोषक तत्व और मौसम दर्ज करें। हमारा AI मॉडल (22 फसलों पर प्रशिक्षित) आपकी परिस्थितियों के अनुसार सर्वश्रेष्ठ 3 फसलों की सिफारिश करेगा।",
    btn_sync_weather: "🌦️ वर्तमान लाइव मौसम से तापमान व नमी सिंक करें",
    lbl_crop_n: "नाइट्रोजन (N स्तर):",
    lbl_crop_p: "फॉस्फोरस (P स्तर):",
    lbl_crop_k: "पोटाश (K स्तर):",
    lbl_temp: "तापमान (°C):",
    lbl_humidity: "नमी (Humidity %):",
    lbl_crop_ph: "पीएच मान (pH):",
    lbl_rainfall: "अनुमानित वर्षा (Rainfall mm):",
    btn_calc_crops: "🌱 सबसे अनुकूल फसलों की गणना करें",
    weather_title: "🌦️ मौसम पूर्वानुमान एवं कृषि मौसम अलर्ट",
    btn_view_weather: "🔍 मौसम देखें",
    schemes_title: "🏛️ भारतीय किसान कल्याणकारी सरकारी योजनाएं (Govt Schemes Portal)",
    schemes_subtitle: "केंद्र एवं राज्य सरकारों द्वारा किसानों के लिए संचालित वित्तीय, बीमा एवं सब्सिडी योजनाओं की प्रामाणिक जानकारी:",
    profile_title: "👤 किसान प्रोफाइल प्रबंधन (Personalized Farming Profile)",
    profile_subtitle: "अपनी प्रोफाइल विवरण को सुरक्षित करें ताकि कृषि साथी की प्रत्येक सलाह आपके खेत, क्षेत्र और फसल के अनुकूल हो सके।",
    lbl_name: "किसान का नाम:",
    lbl_village: "ग्राम / गांव:",
    lbl_prof_district: "जिला (District):",
    lbl_prof_state: "राज्य (State):",
    lbl_acres: "खेत का आकार (एकड़ में):",
    lbl_current_crop: "वर्तमान मुख्य फसल:",
    lbl_soil_type: "मिट्टी का प्रकार:",
    btn_save_profile: "💾 प्रोफाइल सुरक्षित करें",
    footer_text: "कृषि साथी (KrishiSaathi) — ICAR एवं भारत सरकार की कृषि संस्तुतियों पर आधारित AI निर्णय समर्थन प्रणाली",
    footer_helpline: "किसान कॉल सेंटर टोल-फ्री: 1800-180-1551 | आपातकालीन कृषि परामर्श",
    chat_placeholder: "यहाँ अपना सवाल लिखें या बोलें (उदा: गेहूं के पत्ते पीले हो रहे हैं)...",
    schemes_placeholder: "योजना खोजें (जैसे: सम्मान निधि, फसल बीमा, सोलर पंप, केसीसी)...",
    weather_placeholder: "जिला दर्ज करें (उदा: Varanasi, Karnal, Patna)...",
    default_chips: [
      "गेहूं में पहली सिंचाई और खाद का सही समय बताएं",
      "टमाटर के पत्तों पर काले-भूरे धब्बे पड़ रहे हैं, क्या करें?",
      "मेरी मिट्टी में नाइट्रोजन कम है, क्या बारिश में यूरिया डाल सकते हैं?",
      "पीएम किसान सम्मान निधि योजना की जानकारी दें"
    ]
  },
  en: {
    app_title: "KrishiSaathi (Farmer Assistant)",
    app_subtitle: "Intelligent Agentic Agricultural Advisory System for Indian Farmers",
    tab_chat: "💬 Farming Assistant Chat",
    tab_disease: "📸 Crop Disease Diagnosis",
    tab_soil: "🧪 Soil Health Card",
    tab_crop: "🌱 Crop Recommender",
    tab_weather: "🌦️ Weather & Agri-Alerts",
    tab_schemes: "🏛️ Govt Schemes",
    tab_profile: "👤 Farmer Profile",
    welcome_title: "Welcome Farmer Friend! 🙏",
    welcome_desc: "I am your digital KrishiSaathi assistant. You can ask me in English or Hindi by typing or speaking about crops, fertilizers, pest diseases, weather forecasts, or government schemes.",
    speak_btn: "🔊 Read Aloud",
    quick_services_title: "⚡ Quick Agricultural Tools",
    quick_services_desc: "Access specialized tools directly:",
    btn_check_leaf: "📸 Check Leaf Photo",
    btn_check_soil: "🧪 Analyze Soil Health Card",
    btn_calc_crop: "🌱 Recommend Best Crops",
    safety_title: "🛡️ Farmer Safety Guarantee",
    safety_1: "Strict ban on hazardous chemicals (Endosulfan, etc.).",
    safety_2: "Automatic weather alert to prevent spray before rain.",
    safety_3: "Grounded in ICAR & Krishi Vigyan Kendra (KVK) guidelines.",
    disease_title: "📸 Crop Disease & Leaf Health Diagnosis (AI Vision)",
    disease_subtitle: "Upload a clear photo of your affected crop leaf. Our computer vision model identifies the disease and provides organic and safe chemical treatments.",
    lbl_crop_hint: "Target Crop (Optional):",
    opt_auto_detect: "Auto Detect",
    dropzone_title: "Drag & drop crop leaf photo here or click to upload",
    dropzone_desc: "Supports JPG, PNG or WEBP",
    soil_title: "🧪 Soil Health Card Analytics & Govt Lab Finder",
    soil_subtitle: "Enter parameters from your laboratory Soil Health Card. The engine identifies deficiencies and recommends corrective amendments and nearby labs.",
    lbl_ph: "pH Value:",
    lbl_oc: "Organic Carbon (OC %):",
    lbl_n: "Available Nitrogen (N kg/ha):",
    lbl_p: "Available Phosphorus (P kg/ha):",
    lbl_k: "Available Potassium (K kg/ha):",
    lbl_ec: "Electrical Conductivity (EC dS/m):",
    lbl_zn: "Zinc (Zn ppm):",
    lbl_s: "Sulphur (S ppm):",
    lbl_state: "State:",
    lbl_district: "District:",
    btn_analyze_soil: "🧪 Analyze Soil Health Card",
    crop_rec_title: "🌱 Machine Learning Crop Recommendation Engine",
    crop_rec_subtitle: "Input your soil nutrients and climate parameters. Our ML model (trained on 22 crops) recommends the top 3 best-suited crops.",
    btn_sync_weather: "🌦️ Sync Live Weather Temperature & Humidity",
    lbl_crop_n: "Nitrogen (N level):",
    lbl_crop_p: "Phosphorus (P level):",
    lbl_crop_k: "Potassium (K level):",
    lbl_temp: "Temperature (°C):",
    lbl_humidity: "Humidity (%):",
    lbl_crop_ph: "Soil pH:",
    lbl_rainfall: "Rainfall (mm):",
    btn_calc_crops: "🌱 Calculate Optimal Crops",
    weather_title: "🌦️ Meteorological Forecast & Agricultural Alerts",
    btn_view_weather: "🔍 View Weather",
    schemes_title: "🏛️ Indian Agricultural Welfare Schemes Portal",
    schemes_subtitle: "Authoritative information on central and state welfare, insurance, and subsidy schemes for farmers:",
    profile_title: "👤 Farmer Profile Management",
    profile_subtitle: "Save your farm context so that every advisory is tailored to your acreage, district, and cultivated crops.",
    lbl_name: "Farmer Name:",
    lbl_village: "Village / Town:",
    lbl_prof_district: "District:",
    lbl_prof_state: "State:",
    lbl_acres: "Farm Size (Acres):",
    lbl_current_crop: "Primary Crop:",
    lbl_soil_type: "Soil Type:",
    btn_save_profile: "💾 Save Profile",
    footer_text: "KrishiSaathi — Decision-Support AI Grounded in ICAR & Ministry of Agriculture Guidelines",
    footer_helpline: "Kisan Call Centre Toll-Free: 1800-180-1551 | Agricultural Advisory",
    chat_placeholder: "Type or speak your farming query (e.g., yellow spots on wheat leaves)...",
    schemes_placeholder: "Search schemes (e.g., PM-KISAN, crop insurance, solar pump)...",
    weather_placeholder: "Enter district name (e.g., Varanasi, Karnal, Patna)...",
    default_chips: [
      "Optimal irrigation and fertilizer schedule for wheat",
      "Dark spots on tomato leaves, what should I do?",
      "Soil has low nitrogen, can I apply urea before rain?",
      "Tell me about PM-KISAN Samman Nidhi scheme"
    ]
  }
};

let recognition = null;
if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
  const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SpeechRec();
  recognition.lang = "hi-IN";
  recognition.continuous = false;
  recognition.interimResults = false;
}

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initLanguageSwitcher();
  initVoice();
  loadLiveWeather();
  loadFarmerProfile();
  setupChatHandlers();
  setupDiseaseUpload();
  setupSoilAnalyzer();
  setupCropRecommender();
  setupSchemesSearch();
});

function initLanguageSwitcher() {
  const select = document.getElementById("lang-select");
  if (!select) return;
  select.value = currentLang;
  
  select.addEventListener("change", (e) => {
    setLanguage(e.target.value);
  });
  
  applyLanguage(currentLang);
}

function setLanguage(lang) {
  currentLang = lang;
  document.documentElement.lang = lang;
  if (recognition) {
    recognition.lang = lang === "hi" ? "hi-IN" : "en-IN";
  }
  applyLanguage(lang);
  loadLiveWeather();
}

function applyLanguage(lang) {
  const dict = I18N[lang] || I18N.hi;
  
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.getAttribute("data-i18n");
    if (dict[key]) {
      el.innerText = dict[key];
    }
  });

  const chatInput = document.getElementById("chat-input");
  if (chatInput) chatInput.placeholder = dict.chat_placeholder;

  const schemesInput = document.getElementById("schemes-search");
  if (schemesInput) schemesInput.placeholder = dict.schemes_placeholder;

  const weatherInput = document.getElementById("weather-search-district");
  if (weatherInput) weatherInput.placeholder = dict.weather_placeholder;

  renderChips(dict.default_chips);
}

function initTabs() {
  const tabs = document.querySelectorAll(".tab-btn");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
      
      tab.classList.add("active");
      const targetId = tab.getAttribute("data-tab");
      document.getElementById(targetId).classList.add("active");
    });
  });
}

function showTab(tabId) {
  document.querySelectorAll(".tab-btn").forEach(t => {
    t.classList.toggle("active", t.getAttribute("data-tab") === tabId);
  });
  document.querySelectorAll(".tab-content").forEach(c => {
    c.classList.toggle("active", c.id === tabId);
  });
}

async function loadLiveWeather(district = "Lucknow") {
  try {
    const res = await fetch(`/api/weather?district=${encodeURIComponent(district)}`);
    const data = await res.json();
    if (data.success) {
      liveWeatherCache = data;
      const curr = data.current;
      document.getElementById("header-weather").innerHTML = `📍 ${data.location} | 🌡️ ${curr.temperature}°C | 💧 ${curr.humidity}% | ${curr.condition}`;
      
      const weatherTabBox = document.getElementById("weather-display-box");
      if (weatherTabBox) {
        let advisoriesHtml = "";
        if (data.agricultural_advisories) {
          advisoriesHtml = data.agricultural_advisories.map(a => 
            `<div class="advisory-item ${a.type}">
              <strong>${a.title}</strong><br>${a.advice}
            </div>`
          ).join("");
        }

        let forecastHtml = "";
        if (data.forecast) {
          forecastHtml = `<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; margin-top: 15px;">` +
            data.forecast.map(f => `
              <div style="background: white; border: 1px solid #c8e6c9; padding: 10px; border-radius: 8px; text-align: center;">
                <div style="font-size: 0.8rem; color: #555;">${f.date}</div>
                <div style="font-size: 1.1rem; font-weight: 700; color: #2e7d32; margin: 4px 0;">${f.temp_max}° / ${f.temp_min}°</div>
                <div style="font-size: 0.8rem; color: #0288d1;">🌧️ ${f.rain_prob}% ${currentLang === 'hi' ? 'वर्षा' : 'Rain'}</div>
                <div style="font-size: 0.75rem; margin-top: 4px;">${f.condition}</div>
              </div>
            `).join("") + `</div>`;
        }

        const sourceLabel = currentLang === "hi" ? "स्रोत" : "Source";
        const humidityLabel = currentLang === "hi" ? "नमी" : "Humidity";
        const windLabel = currentLang === "hi" ? "हवा" : "Wind";
        const advTitle = currentLang === "hi" ? "🌾 कृषि मौसम परामर्श (Agri Advisories)" : "🌾 Agricultural Weather Advisories";
        const forecastTitle = currentLang === "hi" ? "📅 आगामी 5 दिनों का पूर्वानुमान" : "📅 5-Day Weather Forecast";

        weatherTabBox.innerHTML = `
          <div style="display: flex; justify-content: space-between; align-items: center; background: #e8f5e9; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
            <div>
              <h3 style="color: #1b5e20;">${data.location}</h3>
              <p style="color: #388e3c; font-size: 0.9rem;">${sourceLabel}: ${data.source}</p>
            </div>
            <div style="text-align: right;">
              <span style="font-size: 2rem; font-weight: 800; color: #2e7d32;">${curr.temperature}°C</span>
              <div style="font-size: 0.85rem; color: #555;">${humidityLabel}: ${curr.humidity}% | ${windLabel}: ${curr.wind_speed} km/h</div>
            </div>
          </div>
          <h4 style="margin-bottom: 10px; color: #1b5e20;">${advTitle}</h4>
          ${advisoriesHtml}
          <h4 style="margin-top: 20px; margin-bottom: 8px; color: #1b5e20;">${forecastTitle}</h4>
          ${forecastHtml}
        `;
      }
    }
  } catch (err) {
    console.error("Error loading weather:", err);
  }
}

function initVoice() {
  const micBtn = document.getElementById("mic-btn");
  const chatInput = document.getElementById("chat-input");
  
  if (!recognition) {
    micBtn.title = currentLang === "hi" ? "वॉइस इनपुट इस ब्राउज़र में समर्थित नहीं है" : "Voice input is not supported in this browser";
    micBtn.style.opacity = "0.6";
    return;
  }

  micBtn.addEventListener("click", () => {
    if (micBtn.classList.contains("recording")) {
      recognition.stop();
      micBtn.classList.remove("recording");
    } else {
      micBtn.classList.add("recording");
      recognition.lang = currentLang === "hi" ? "hi-IN" : "en-IN";
      recognition.start();
    }
  });

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    chatInput.value = transcript;
    micBtn.classList.remove("recording");
    sendMessage(transcript);
  };

  recognition.onerror = () => {
    micBtn.classList.remove("recording");
  };

  recognition.onend = () => {
    micBtn.classList.remove("recording");
  };
}

function speakText(text) {
  if (!("speechSynthesis" in window)) {
    alert(currentLang === "hi" ? "आपके ब्राउज़र में आवाज़ समर्थित नहीं है।" : "Voice playback is not supported in your browser.");
    return;
  }
  window.speechSynthesis.cancel();
  const clean = text.replace(/[*#•`_]/g, "").replace(/\n+/g, " ");
  const utterance = new SpeechSynthesisUtterance(clean);
  utterance.lang = currentLang === "hi" ? "hi-IN" : "en-IN";
  utterance.rate = 0.95;
  
  const voices = window.speechSynthesis.getVoices();
  const targetLangCode = currentLang === "hi" ? "hi" : "en";
  const matchedVoice = voices.find(v => v.lang.startsWith(targetLangCode));
  if (matchedVoice) utterance.voice = matchedVoice;
  
  window.speechSynthesis.speak(utterance);
}

function setupChatHandlers() {
  const sendBtn = document.getElementById("send-btn");
  const chatInput = document.getElementById("chat-input");

  sendBtn.addEventListener("click", () => {
    const text = chatInput.value.trim();
    if (text) {
      sendMessage(text);
      chatInput.value = "";
    }
  });

  chatInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      const text = chatInput.value.trim();
      if (text) {
        sendMessage(text);
        chatInput.value = "";
      }
    }
  });
}

async function sendMessage(text) {
  const messagesArea = document.getElementById("chat-messages");
  const userLabel = currentLang === "hi" ? "आप" : "You";
  
  const userDiv = document.createElement("div");
  userDiv.className = "message user";
  userDiv.innerHTML = `<strong>${userLabel}:</strong> ${escapeHtml(text)}`;
  messagesArea.appendChild(userDiv);
  messagesArea.scrollTop = messagesArea.scrollHeight;

  const loadingDiv = document.createElement("div");
  loadingDiv.className = "message agent";
  loadingDiv.id = "agent-loading";
  const loadingText = currentLang === "hi" 
    ? "कृषि साथी सोच रहा है... (मौसम व ज्ञानकोश जांच जारी)"
    : "KrishiSaathi is analyzing... (Checking weather & knowledge base)";
  loadingDiv.innerHTML = `<em>${loadingText}</em>`;
  messagesArea.appendChild(loadingDiv);
  messagesArea.scrollTop = messagesArea.scrollHeight;

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        session_id: currentSessionId,
        farmer_id: currentFarmerId,
        lang: currentLang
      })
    });
    const data = await res.json();
    loadingDiv.remove();

    const agentDiv = document.createElement("div");
    agentDiv.className = "message agent";

    let thoughtHtml = "";
    if (data.thought_steps && data.thought_steps.length > 0) {
      const thoughtTitle = currentLang === "hi"
        ? "🧠 एजेंट विचार प्रक्रिया (Agent Reasoning & Tools)"
        : "🧠 Agent Reasoning Steps & Tool Invocations";
      thoughtHtml = `
        <details class="thought-steps">
          <summary>${thoughtTitle}</summary>
          <ul>${data.thought_steps.map(s => `<li>${escapeHtml(s)}</li>`).join("")}</ul>
        </details>
      `;
    }

    let formattedResp = escapeHtml(data.response)
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.*?)\*/g, "<em>$1</em>")
      .replace(/\n/g, "<br>");

    const speakBtnLabel = currentLang === "hi" ? "🔊 बोलकर सुनाएं" : "🔊 Read Aloud";

    agentDiv.innerHTML = `
      ${thoughtHtml}
      <div>${formattedResp}</div>
      <div class="message-actions">
        <button class="tts-btn" onclick="speakText(\`${escapeJsString(data.response)}\`)">${speakBtnLabel}</button>
      </div>
    `;
    messagesArea.appendChild(agentDiv);

    renderChips(data.follow_up_suggestions || []);
    messagesArea.scrollTop = messagesArea.scrollHeight;
  } catch (err) {
    loadingDiv.innerHTML = `<span style="color: red;">Error: Unable to connect to server. / सर्वर से संपर्क नहीं हो सका।</span>`;
  }
}

function renderChips(suggestions) {
  const container = document.getElementById("chips-container");
  container.innerHTML = "";
  suggestions.forEach(s => {
    const btn = document.createElement("button");
    btn.className = "chip";
    btn.innerText = s;
    btn.onclick = () => sendMessage(s);
    container.appendChild(btn);
  });
}

function setupDiseaseUpload() {
  const dropzone = document.getElementById("disease-dropzone");
  const fileInput = document.getElementById("disease-file");

  dropzone.addEventListener("click", () => fileInput.click());

  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.style.background = "#dcedc8";
  });
  dropzone.addEventListener("dragleave", () => {
    dropzone.style.background = "#f1f8e9";
  });
  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.style.background = "#f1f8e9";
    if (e.dataTransfer.files.length > 0) {
      processDiseaseFile(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
      processDiseaseFile(e.target.files[0]);
    }
  });
}

async function processDiseaseFile(file) {
  const resultArea = document.getElementById("disease-result");
  const cropHint = document.getElementById("disease-crop-hint").value;
  
  resultArea.innerHTML = `<div style="text-align: center; padding: 20px;">${currentLang === 'hi' ? '📸 छवि विश्लेषण जारी है... कृपया प्रतीक्षा करें।' : '📸 Analyzing image... please wait.'}</div>`;

  const formData = new FormData();
  formData.append("file", file);
  formData.append("crop_hint", cropHint);
  formData.append("lang", currentLang);
  if (liveWeatherCache) {
    const isRain = liveWeatherCache.forecast && liveWeatherCache.forecast[0].rain_prob >= 30;
    formData.append("rain_forecast", isRain);
  }

  try {
    const res = await fetch("/api/disease/detect", {
      method: "POST",
      body: formData
    });
    const data = await res.json();
    if (data.success) {
      const isEn = currentLang === "en";
      const diseaseName = isEn ? data.disease_name_en : data.disease_name_hindi;
      const cropName = isEn ? data.crop_en : data.crop;
      const symptoms = isEn ? data.symptoms_en : data.symptoms;
      const causes = isEn ? data.pathogen_cause_en : data.pathogen_cause;
      const action = isEn ? data.immediate_cultural_action_en : data.immediate_cultural_action;
      const organic = isEn ? data.organic_ipm_remedy_en : data.organic_ipm_remedy;
      const chem = isEn ? data.chemical_solution_en : data.chemical_solution;
      const sprayAdv = isEn ? data.weather_spray_advisory_en : data.weather_spray_advisory;
      const kvkNote = isEn ? data.kvk_escalation_note_en : data.kvk_escalation_note;

      const confLabel = isEn ? "Confidence" : "विश्वास स्कोर";
      const cropLabel = isEn ? "Crop" : "फसल";
      const sympLabel = isEn ? "🔍 Visible Symptoms" : "🔍 मुख्य लक्षण";
      const causeLabel = isEn ? "🦠 Pathogen / Cause" : "🦠 कारण/पैथोजन";
      const actionLabel = isEn ? "⚡ Immediate Action" : "⚡ तुरंत करने योग्य उपाय";
      const organicLabel = isEn ? "🌿 Organic & IPM Remedies" : "🌿 जैविक व देसी समाधान (IPM)";
      const chemTitle = isEn ? "🧪 Recommended Safe Chemical Treatment" : "🧪 संस्तुत सुरक्षित रासायनिक उपाय";
      const speakBtnLabel = isEn ? "🔊 Read Diagnosis" : "🔊 निदान बोलकर सुनें";

      resultArea.innerHTML = `
        <div class="result-card">
          <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #c8e6c9; padding-bottom: 10px; margin-bottom: 12px;">
            <div>
              <h3 style="color: #2e7d32;">${diseaseName}</h3>
              <div style="color: #555; font-size: 0.9rem;">${cropLabel}: <strong>${cropName}</strong></div>
            </div>
            <div style="text-align: right;">
              <span class="badge ${data.confidence_score >= 75 ? 'badge-success' : 'badge-warning'}">${confLabel}: ${data.confidence_score}%</span>
            </div>
          </div>

          <p style="margin-bottom: 8px;"><strong>${sympLabel}:</strong> ${symptoms}</p>
          <p style="margin-bottom: 8px;"><strong>${causeLabel}:</strong> ${causes}</p>
          <p style="margin-bottom: 8px;"><strong>${actionLabel}:</strong> ${action}</p>
          <p style="margin-bottom: 8px;"><strong>${organicLabel}:</strong> ${organic}</p>
          
          <div style="background: #f9fbe7; border-left: 4px solid #9e9d24; padding: 10px; border-radius: 6px; margin: 12px 0;">
            <strong>${chemTitle}:</strong><br>
            • ${isEn ? 'Chemical' : 'दवा'}: <strong>${chem.name}</strong><br>
            • ${isEn ? 'Dose' : 'मात्रा'}: ${chem.dose}<br>
            • ${isEn ? 'Precaution' : 'सावधानी'}: ${chem.precaution}
          </div>

          <div style="background: #e3f2fd; padding: 8px 12px; border-radius: 6px; font-size: 0.9rem; margin-bottom: 10px;">
            ${sprayAdv}
          </div>

          <div style="font-size: 0.82rem; color: #c62828; border-top: 1px dashed #ccc; padding-top: 8px;">
            📌 ${kvkNote}
          </div>
          
          <div style="margin-top: 10px; text-align: right;">
            <button class="tts-btn" onclick="speakText(\`${escapeJsString(diseaseName + '. ' + symptoms + '. ' + action + '. ' + chem.name + ' ' + chem.dose)}\`)">${speakBtnLabel}</button>
          </div>
        </div>
      `;
    } else {
      resultArea.innerHTML = `<div style="color: red;">${data.error}</div>`;
    }
  } catch (err) {
    resultArea.innerHTML = `<div style="color: red;">Error processing diagnosis. / विश्लेषण असफल रहा।</div>`;
  }
}

function setupSoilAnalyzer() {
  const form = document.getElementById("soil-form");
  const resultArea = document.getElementById("soil-result");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    resultArea.innerHTML = `<div style="text-align:center; padding: 20px;">${currentLang === 'hi' ? 'मृदा विश्लेषण जारी है...' : 'Analyzing Soil Health Report...'}</div>`;

    const payload = {
      ph: parseFloat(document.getElementById("soil-ph").value),
      oc: parseFloat(document.getElementById("soil-oc").value),
      n: parseFloat(document.getElementById("soil-n").value),
      p: parseFloat(document.getElementById("soil-p").value),
      k: parseFloat(document.getElementById("soil-k").value),
      ec: parseFloat(document.getElementById("soil-ec").value),
      zn: parseFloat(document.getElementById("soil-zn").value),
      s: parseFloat(document.getElementById("soil-s").value),
      fe: 5.0,
      state: document.getElementById("soil-state").value,
      district: document.getElementById("soil-district").value
    };

    try {
      const res = await fetch("/api/soil/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      const isEn = currentLang === "en";

      const defs = isEn ? data.deficiencies_en : data.deficiencies;
      const defHtml = defs.map(d => `<li>${d}</li>`).join("");

      const amendHtml = data.amendments.map(a => {
        const act = isEn ? a.action_en : a.action;
        const dose = isEn ? a.dose_en : a.dose;
        const imp = isEn ? a.importance_en : a.importance;
        return `<li><strong>${act}:</strong> ${dose} (${isEn ? 'Priority' : 'महत्व'}: ${imp})</li>`;
      }).join("");

      const labsHtml = data.nearby_labs.map(l => `
        <div style="background: white; border: 1px solid #c8e6c9; padding: 10px; border-radius: 8px; margin-bottom: 8px;">
          <strong style="color: #2e7d32;">${l.name}</strong> (${l.type})<br>
          <span style="font-size: 0.85rem; color: #555;">📍 ${l.address} | 📞 ${l.contact} | 💰 ${l.fee}</span>
        </div>
      `).join("");

      const summary = isEn ? data.english_summary : data.hindi_summary;
      const scoreTitle = isEn ? `Soil Health Score: ${data.health_score}/100` : `मृदा स्वास्थ्य स्कोर: ${data.health_score}/100`;
      const defTitle = isEn ? "⚠️ Detected Nutrient Deficiencies:" : "⚠️ प्रमुख पोषक तत्वों की कमियां:";
      const amendTitle = isEn ? "🌾 Corrective Soil Amendments:" : "🌾 सुधारात्मक कृषि सिफारिशें:";
      const labTitle = isEn ? "🏛️ Nearby Govt Soil Testing Labs & KVKs:" : "🏛️ नजदीकी सरकारी मृदा परीक्षण प्रयोगशालाएं:";

      resultArea.innerHTML = `
        <div class="result-card">
          <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #e8f5e9; padding-bottom: 8px;">
            <h3 style="color: #1b5e20;">${scoreTitle}</h3>
            <span class="badge ${data.health_score >= 70 ? 'badge-success' : 'badge-warning'}">${data.soil_classification.name_hindi}</span>
          </div>
          <p style="margin: 10px 0; font-size: 0.95rem;">${summary}</p>
          
          <h4 style="color: #c62828; margin-top: 12px;">${defTitle}</h4>
          <ul>${defHtml || (isEn ? "<li>No critical deficiencies detected.</li>" : "<li>कोई गंभीर कमी नहीं पाई गई।</li>")}</ul>

          <h4 style="color: #2e7d32; margin-top: 12px;">${amendTitle}</h4>
          <ul>${amendHtml || (isEn ? "<li>Maintain balanced organic manuring.</li>" : "<li>संतुलित गोबर खाद व वर्मीकम्पोस्ट का प्रयोग जारी रखें।</li>")}</ul>

          <h4 style="color: #0288d1; margin-top: 15px; margin-bottom: 8px;">${labTitle}</h4>
          ${labsHtml}
        </div>
      `;
    } catch (err) {
      resultArea.innerHTML = `<div style="color: red;">Error during soil analysis. / विश्लेषण असफल रहा।</div>`;
    }
  });
}

function setupCropRecommender() {
  const form = document.getElementById("crop-rec-form");
  const resultArea = document.getElementById("crop-rec-result");
  const syncBtn = document.getElementById("sync-weather-crop-btn");

  syncBtn.addEventListener("click", () => {
    if (liveWeatherCache && liveWeatherCache.current) {
      document.getElementById("crop-temp").value = liveWeatherCache.current.temperature;
      document.getElementById("crop-humidity").value = liveWeatherCache.current.humidity;
      const msg = currentLang === "hi"
        ? `मौसम आंकड़े सिंक हुए: तापमान ${liveWeatherCache.current.temperature}°C, नमी ${liveWeatherCache.current.humidity}%`
        : `Weather synchronized: Temperature ${liveWeatherCache.current.temperature}°C, Humidity ${liveWeatherCache.current.humidity}%`;
      alert(msg);
    } else {
      alert(currentLang === "hi" ? "मौसम डेटा लोड हो रहा है, कृपया 1 सेकंड बाद दबाएं।" : "Weather data loading, please retry in 1 second.");
    }
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    resultArea.innerHTML = `<div style="text-align: center; padding: 20px;">${currentLang === 'hi' ? 'सर्वोत्तम फसलों की गणना हो रही है...' : 'Calculating optimal crops...'}</div>`;

    const payload = {
      n: parseFloat(document.getElementById("crop-n").value),
      p: parseFloat(document.getElementById("crop-p").value),
      k: parseFloat(document.getElementById("crop-k").value),
      temperature: parseFloat(document.getElementById("crop-temp").value),
      humidity: parseFloat(document.getElementById("crop-humidity").value),
      ph: parseFloat(document.getElementById("crop-ph").value),
      rainfall: parseFloat(document.getElementById("crop-rainfall").value),
      month: new Date().getMonth() + 1
    };

    try {
      const res = await fetch("/api/crop/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      const isEn = currentLang === "en";
      
      const cardsHtml = data.top_recommendations.map((c, i) => {
        const cropTitle = isEn ? `${c.crop_key.toUpperCase()} (${c.hindi_name})` : c.hindi_name;
        const matchLabel = isEn ? "Suitability" : "अनुकूलता";
        const sowLabel = isEn ? "Sowing" : "बुवाई समय";
        const waterLabel = isEn ? "Water" : "पानी";
        const seasonLabel = isEn ? "Season" : "फसल चक्र";

        return `
          <div style="background: white; border: 1px solid #c8e6c9; border-radius: 10px; padding: 15px; margin-bottom: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.04);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <h3 style="color: #2e7d32;">#${i+1} ${cropTitle}</h3>
              <span class="badge badge-success">${matchLabel}: ${c.suitability_score}%</span>
            </div>
            <p style="font-size: 0.9rem; color: #444; margin: 8px 0;">${c.description}</p>
            <div style="font-size: 0.85rem; color: #555; display: flex; gap: 15px; flex-wrap: wrap;">
              <span>📅 ${sowLabel}: <strong>${c.sowing_months}</strong></span>
              <span>💧 ${waterLabel}: <strong>${c.water_need}</strong></span>
              <span>🍂 ${seasonLabel}: <strong>${c.season}</strong></span>
            </div>
          </div>
        `;
      }).join("");

      const title = isEn ? `🌟 Top Recommended Crops (${data.current_season}):` : `🌟 शीर्ष अनुशंसित फसलें (${data.current_season}):`;

      resultArea.innerHTML = `
        <div class="result-card">
          <h4 style="color: #1b5e20; margin-bottom: 10px;">${title}</h4>
          ${cardsHtml}
          <div style="background: #f1f8e9; padding: 10px; border-radius: 8px; font-size: 0.9rem; color: #33691e; margin-top: 10px;">
            💡 ${data.summary_hindi}
          </div>
        </div>
      `;
    } catch (err) {
      resultArea.innerHTML = `<div style="color: red;">Error during crop recommendation. / फसल अनुशंसा असफल रही।</div>`;
    }
  });
}

function setupSchemesSearch() {
  const searchInput = document.getElementById("schemes-search");
  const container = document.getElementById("schemes-display-box");

  async function fetchSchemes(q = "") {
    try {
      const res = await fetch(`/api/schemes?q=${encodeURIComponent(q)}`);
      const data = await res.json();
      if (data.schemes) {
        const isEn = currentLang === "en";
        const eligLabel = isEn ? "Eligibility" : "पात्रता";
        const benLabel = isEn ? "Key Benefits" : "मुख्य लाभ";
        const applyLabel = isEn ? "How to Apply" : "आवेदन कैसे करें";
        const helpLabel = isEn ? "Helpline" : "हेल्पलाइन";

        container.innerHTML = data.schemes.map(s => `
          <div style="background: white; border: 1px solid #c8e6c9; border-radius: 10px; padding: 15px; margin-bottom: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; padding-bottom: 8px;">
              <h3 style="color: #1b5e20; font-size: 1.15rem;">🏛️ ${s.name}</h3>
              <span style="font-size: 0.8rem; background: #e0f2f1; color: #00796b; padding: 3px 8px; border-radius: 10px;">${s.ministry}</span>
            </div>
            <p style="margin: 10px 0; font-size: 0.92rem; line-height: 1.4;">${s.objective}</p>
            <div style="font-size: 0.88rem; line-height: 1.5; background: #fafafa; padding: 10px; border-radius: 6px;">
              <strong>🎯 ${eligLabel}:</strong> ${s.eligibility}<br>
              <strong>💰 ${benLabel}:</strong> ${s.benefits}<br>
              <strong>📝 ${applyLabel}:</strong> ${s.how_to_apply}<br>
              <strong>📞 ${helpLabel}:</strong> <span style="color: #d32f2f; font-weight: 700;">${s.helpline}</span>
            </div>
          </div>
        `).join("");
      }
    } catch (err) {
      console.error(err);
    }
  }

  searchInput.addEventListener("input", (e) => {
    fetchSchemes(e.target.value);
  });

  fetchSchemes("");
}

async function loadFarmerProfile() {
  try {
    const res = await fetch(`/api/profile?farmer_id=${currentFarmerId}`);
    const data = await res.json();
    if (data) {
      document.getElementById("prof-name").value = data.name || "";
      document.getElementById("prof-village").value = data.village || "";
      document.getElementById("prof-district").value = data.district || "Lucknow";
      document.getElementById("prof-state").value = data.state || "Uttar Pradesh";
      document.getElementById("prof-acres").value = data.farm_size_acres || 2.5;
      document.getElementById("prof-crop").value = data.current_crop || "गेहूं";
      document.getElementById("prof-soil").value = data.soil_type || "जलोढ़ दोमट";
      
      document.getElementById("soil-district").value = data.district || "Lucknow";
      document.getElementById("soil-state").value = data.state || "Uttar Pradesh";
    }
  } catch (err) {
    console.error(err);
  }

  document.getElementById("profile-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
      farmer_id: currentFarmerId,
      name: document.getElementById("prof-name").value,
      village: document.getElementById("prof-village").value,
      district: document.getElementById("prof-district").value,
      state: document.getElementById("prof-state").value,
      farm_size_acres: parseFloat(document.getElementById("prof-acres").value),
      current_crop: document.getElementById("prof-crop").value,
      soil_type: document.getElementById("prof-soil").value,
      irrigation_type: "ट्यूबवेल",
      language: currentLang === "hi" ? "Hindi" : "English"
    };

    try {
      const res = await fetch("/api/profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      alert(currentLang === "hi" ? "✅ प्रोफाइल सफलतापूर्वक सुरक्षित हुई!" : "✅ Profile saved successfully!");
      loadLiveWeather(payload.district);
    } catch (err) {
      alert("Error saving profile. / प्रोफाइल सुरक्षित नहीं हो सकी।");
    }
  });
}

function escapeHtml(text) {
  if (!text) return "";
  const div = document.createElement("div");
  div.innerText = text;
  return div.innerHTML;
}

function escapeJsString(str) {
  if (!str) return "";
  return str.replace(/\\/g, "\\\\").replace(/`/g, "\\`").replace(/\$/g, "\\$").replace(/"/g, '\\"');
}
