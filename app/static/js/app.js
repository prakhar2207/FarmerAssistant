/**
 * KrishiSaathi — Multimodal AI Agricultural Advisory System
 * ChatGPT-Grade Clean Frontend Logic with Full Session Management,
 * Speech STT/TTS, Multimodal Leaf Vision, and Specialized Agro-Modals.
 */

// ==========================================
// Application State
// ==========================================
let currentSessionId = localStorage.getItem("ks_current_session") || ("session_" + Date.now().toString(36) + Math.random().toString(36).substring(2, 6));
let currentFarmerId = "default_farmer";
let currentLang = localStorage.getItem("ks_current_lang") || "hi";
let liveWeatherCache = null;
let attachedChatFile = null;
let currentSpeakingUtterance = null;
let activeTtsButton = null;

// ==========================================
// Starter Prompts Bilingual Catalog
// ==========================================
const STARTER_PROMPTS = {
  starter_1: {
    hi: "गेहूं में खाद की सही मात्रा और डालने का समय बताओ",
    en: "What is the recommended fertilizer schedule for wheat crop?"
  },
  starter_2: {
    hi: "पत्ते पीले पड़ रहे हैं और काले धब्बे हैं, क्या उपाय करें?",
    en: "Leaves are turning yellow with dark spots, how to treat?"
  },
  starter_3: {
    hi: "अगले 5 दिनों का मौसम और बारिश का पूर्वानुमान क्या है?",
    en: "What is the 5-day weather and rainfall forecast?"
  },
  starter_4: {
    hi: "PM-KISAN सम्मान निधि और फसल बीमा योजना (PMFBY) की जानकारी दो",
    en: "Give details about PM-KISAN and PMFBY crop insurance schemes"
  }
};

// ==========================================
// Bilingual i18n Dictionaries
// ==========================================
const I18N = {
  hi: {
    app_title: "कृषि साथी (KrishiSaathi)",
    btn_new_chat: "नया संवाद (New Chat)",
    history_title: "हालिया संवाद / Recent Chats",
    tools_title: "कृषि उपकरण / Tools",
    tool_disease: "पत्ती रोग जांच (YOLO)",
    tool_soil: "मृदा स्वास्थ्य कार्ड (Soil)",
    tool_crop: "फसल चयन AI (Crop ML)",
    tool_weather: "मौसम पूर्वानुमान (Weather)",
    tool_schemes: "सरकारी योजनाएं (Schemes)",
    hero_title: "नमस्ते किसान भाई! 🙏",
    hero_subtitle: "मैं आपका AI कृषि सारथी हूँ। अपनी फसल, खाद, कीट-रोग, मौसम या सरकारी योजनाओं के बारे में लिखकर, बोलकर या पत्ती की फोटो भेजकर पूछें।",
    starter_1_title: "गेहूं में खाद की मात्रा",
    starter_1_desc: "यूरिया, डीएपी और पोटाश का संतुलित शेड्यूल",
    starter_2_title: "फसल रोग निदान",
    starter_2_desc: "पत्ती पर धब्बे, झुलसा या रतुआ का वैज्ञानिक उपचार",
    starter_3_title: "मौसम व बारिश अलर्ट",
    starter_3_desc: "तापमान, वर्षा संभावना और स्प्रे अनुकूलता",
    starter_4_title: "सरकारी किसान योजनाएं",
    starter_4_desc: "पीएम किसान, पीएमएफबीवाई और केसीसी आवेदन",
    photo_attached: "पत्ती की फोटो संलग्न (YOLO Vision Active)",
    chat_placeholder: "यहाँ अपनी फसल या सवाल के बारे में पूछें...",
    footer_disclaimer: "🌾 कृषि साथी AI भारतीय कृषि अनुसंधान परिषद (ICAR) संस्तुतियों पर आधारित है। रासायनिक छिड़काव से पहले मौसम व सुरक्षा नियमों का पालन करें।",
    you: "आप",
    assistant: "कृषि साथी",
    loading_msg: "🌾 कृषि साथी सोच रहा है... (मौसम, YOLO विज़न व ICAR ज्ञानकोश जांच जारी)",
    listen_btn: "🔊 सुनो",
    stop_audio_btn: "⏹️ रोकें",
    copy_btn: "📋 कॉपी करें",
    confidence: "विश्वास स्कोर",
    foliar_damage: "संक्रमण",
    citations_title: "📚 प्रामाणिक कृषि संदर्भ (ICAR / KVK / CIBRC):",
    confirm_delete: "क्या आप वाकई इस चैट को हटाना चाहते हैं?",
    empty_history: "कोई पुराना संवाद नहीं मिला।",
    weather_loading: "मौसम लोड हो रहा है...",
    no_active_disease: "स्वस्थ पत्ती अथवा कोई गंभीर लक्षण नहीं पाया गया।",
    modal_disease_title: "📸 फसल रोग एवं पत्ती स्वास्थ्य जांच (AI Vision)",
    modal_disease_intro: "पौधे की पत्ती की स्पष्ट फोटो अपलोड करें। हमारा YOLO विज़न मॉडल रोग के लक्षणों को पहचान कर सुरक्षित उपचार सुझाएगा।",
    modal_disease_crop_label: "संबंधित फसल (वैकल्पिक):",
    modal_disease_autodetect: "स्वचालित पहचान (Auto Detect)",
    modal_disease_dropzone: "यहाँ पत्ते की फोटो खींचकर छोड़ें या क्लिक करके अपलोड करें",
    modal_soil_title: "🧪 मृदा स्वास्थ्य कार्ड विश्लेषण एवं KVK लैब खोजक",
    soil_ph: "पीएच मान (pH):",
    soil_oc: "जैविक कार्बन (OC %):",
    soil_n: "नाइट्रोजन (N kg/ha):",
    soil_p: "फॉस्फोरस (P kg/ha):",
    soil_k: "पोटाश (K kg/ha):",
    soil_ec: "विद्युत चालकता (EC dS/m):",
    soil_zn: "जिंक (Zn ppm):",
    soil_s: "सल्फर (S ppm):",
    soil_fe: "आयरन (Fe ppm):",
    soil_state: "राज्य (State):",
    soil_district: "जिला (District):",
    btn_soil_submit: "🧪 मृदा स्वास्थ्य रिपोर्ट तैयार करें",
    modal_crop_title: "🌱 फसल चयन सलाहकार (Crop ML Engine)",
    crop_n: "नाइट्रोजन (N):",
    crop_p: "फॉस्फोरस (P):",
    crop_k: "पोटाश (K):",
    crop_temp: "तापमान (°C):",
    crop_humidity: "हवा में नमी (%):",
    crop_ph: "पीएच मान (pH):",
    crop_rainfall: "अनुमानित वर्षा (mm):",
    crop_month: "बुवाई का माह (Month):",
    btn_crop_submit: "🌱 श्रेष्ठ फसलों की गणना करें",
    modal_weather_title: "🌦️ मौसम पूर्वानुमान एवं कृषि अलर्ट",
    modal_schemes_title: "🏛️ सरकारी किसान कल्याण योजनाएं",
    modal_profile_title: "👤 किसान प्रोफाइल प्रबंधन",
    profile_name: "किसान का नाम:",
    profile_village: "गांव / पंचायत:",
    profile_district: "जिला:",
    profile_state: "राज्य:",
    profile_acres: "खेत का आकार (एकड़):",
    profile_crop: "वर्तमान मुख्य फसल:",
    profile_soil: "मिट्टी का प्रकार:",
    profile_irrigation: "सिंचाई स्रोत:",
    btn_profile_save: "💾 प्रोफाइल सहेजें (Save Profile)",
    btn_search: "खोजें"
  },
  en: {
    app_title: "KrishiSaathi (Farmer Assistant)",
    btn_new_chat: "New Chat",
    history_title: "Recent Chats",
    tools_title: "Agricultural Tools",
    tool_disease: "Leaf Disease (YOLO)",
    tool_soil: "Soil Health Card",
    tool_crop: "Crop Selector (ML)",
    tool_weather: "Weather Forecast",
    tool_schemes: "Govt Schemes",
    hero_title: "Welcome Farmer Friend! 🙏",
    hero_subtitle: "I am your AI KrishiSaathi assistant. Ask any question about your crops, fertilizer, pests, weather or government schemes via text, voice, or leaf photos.",
    starter_1_title: "Wheat Fertilizer Schedule",
    starter_1_desc: "Balanced dosage for Urea, DAP, and Potash",
    starter_2_title: "Crop Disease Diagnosis",
    starter_2_desc: "Scientific cure for leaf spots, blights, or rusts",
    starter_3_title: "Weather & Rain Alert",
    starter_3_desc: "Temperature, rain probability, and safe spray windows",
    starter_4_title: "Government Schemes",
    starter_4_desc: "PM-KISAN, PMFBY insurance, and KCC credit cards",
    photo_attached: "Leaf Photo Attached (YOLO Vision Active)",
    chat_placeholder: "Ask anything about crops, fertilizers, or pests...",
    footer_disclaimer: "🌾 KrishiSaathi AI is grounded in ICAR & Ministry of Agriculture recommendations. Verify weather conditions before chemical sprays.",
    you: "You",
    assistant: "KrishiSaathi",
    loading_msg: "🌾 KrishiSaathi is analyzing... (Checking weather, YOLO vision & ICAR guidelines)",
    listen_btn: "🔊 Listen",
    stop_audio_btn: "⏹️ Stop",
    copy_btn: "📋 Copy",
    confidence: "Confidence",
    foliar_damage: "Foliar Damage",
    citations_title: "📚 Verified Scientific Grounding (ICAR / KVK / CIBRC):",
    confirm_delete: "Are you sure you want to delete this chat session?",
    empty_history: "No previous chats found.",
    weather_loading: "Loading weather...",
    no_active_disease: "Healthy leaf or no severe pathogen detected.",
    modal_disease_title: "📸 Leaf Disease & Foliar Health (AI Vision)",
    modal_disease_intro: "Upload a clear photo of the plant leaf. Our YOLO vision model will detect disease symptoms and suggest safe ICAR-approved remedies.",
    modal_disease_crop_label: "Associated Crop (Optional):",
    modal_disease_autodetect: "Auto Detect Crop",
    modal_disease_dropzone: "Drop leaf photo here or click to upload",
    modal_soil_title: "🧪 Soil Health Card Analysis & KVK Lab Finder",
    soil_ph: "Soil pH Value:",
    soil_oc: "Organic Carbon (OC %):",
    soil_n: "Nitrogen (N kg/ha):",
    soil_p: "Phosphorus (P kg/ha):",
    soil_k: "Potash (K kg/ha):",
    soil_ec: "Electrical Cond. (EC dS/m):",
    soil_zn: "Zinc (Zn ppm):",
    soil_s: "Sulphur (S ppm):",
    soil_fe: "Iron (Fe ppm):",
    soil_state: "State:",
    soil_district: "District:",
    btn_soil_submit: "🧪 Generate Soil Health Report",
    modal_crop_title: "🌱 Crop Selection Advisor (Crop ML Engine)",
    crop_n: "Nitrogen (N):",
    crop_p: "Phosphorus (P):",
    crop_k: "Potash (K):",
    crop_temp: "Temperature (°C):",
    crop_humidity: "Relative Humidity (%):",
    crop_ph: "Soil pH:",
    crop_rainfall: "Expected Rainfall (mm):",
    crop_month: "Sowing Month:",
    btn_crop_submit: "🌱 Calculate Optimal Crops",
    modal_weather_title: "🌦️ Weather Forecast & Agro Advisories",
    modal_schemes_title: "🏛️ Government Farmer Welfare Schemes",
    modal_profile_title: "👤 Farmer Profile Management",
    profile_name: "Farmer Name:",
    profile_village: "Village / Panchayat:",
    profile_district: "District:",
    profile_state: "State:",
    profile_acres: "Farm Size (Acres):",
    profile_crop: "Primary Current Crop:",
    profile_soil: "Soil Type:",
    profile_irrigation: "Irrigation Source:",
    btn_profile_save: "💾 Save Profile",
    btn_search: "Search"
  }
};

// ==========================================
// Speech Recognition Setup (STT)
// ==========================================
let recognition = null;
if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
  const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SpeechRec();
  recognition.lang = currentLang === "hi" ? "hi-IN" : "en-IN";
  recognition.continuous = false;
  recognition.interimResults = false;
}

// ==========================================
// Initialization on DOM Ready
// ==========================================
document.addEventListener("DOMContentLoaded", () => {
  initLanguageSwitcher();
  initSidebarToggle();
  initChatInput();
  initVoice();
  initModals();
  loadLiveWeather();
  loadFarmerProfile();
  loadSessions();
  loadCurrentSessionHistory();
});

// ==========================================
// Language Switching & Localization
// ==========================================
function initLanguageSwitcher() {
  const langSelect = document.getElementById("lang-select");
  if (!langSelect) return;
  langSelect.value = currentLang;

  langSelect.addEventListener("change", (e) => {
    setLanguage(e.target.value);
  });

  applyLanguage(currentLang);
}

function setLanguage(lang) {
  currentLang = lang;
  localStorage.setItem("ks_current_lang", lang);
  document.documentElement.lang = lang;
  if (recognition) {
    recognition.lang = lang === "hi" ? "hi-IN" : "en-IN";
  }
  applyLanguage(lang);
  loadLiveWeather();
}

function applyLanguage(lang) {
  const dict = I18N[lang] || I18N.hi;

  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (dict[key]) {
      el.innerText = dict[key];
    }
  });

  const textarea = document.getElementById("chat-textarea");
  if (textarea) textarea.placeholder = dict.chat_placeholder;
}

// ==========================================
// Sidebar & Navigation Handlers
// ==========================================
function initSidebarToggle() {
  const sidebar = document.getElementById("sidebar");
  const openBtn = document.getElementById("sidebar-open-btn");
  const closeBtn = document.getElementById("sidebar-close-btn");
  const newChatBtn = document.getElementById("new-chat-btn");
  const backdrop = document.getElementById("sidebar-backdrop");

  function openSidebar() {
    if (sidebar) sidebar.classList.add("open");
    if (backdrop) backdrop.classList.add("active");
  }

  function closeSidebar() {
    if (sidebar) sidebar.classList.remove("open");
    if (backdrop) backdrop.classList.remove("active");
  }

  if (openBtn) {
    openBtn.addEventListener("click", openSidebar);
  }

  if (closeBtn) {
    closeBtn.addEventListener("click", closeSidebar);
  }

  if (backdrop) {
    backdrop.addEventListener("click", closeSidebar);
  }

  if (newChatBtn) {
    newChatBtn.addEventListener("click", () => {
      startNewChat();
      if (window.innerWidth <= 768) {
        closeSidebar();
      }
    });
  }
}

// ==========================================
// Session Management (ChatGPT Style)
// ==========================================
async function loadSessions() {
  const container = document.getElementById("session-history-list");
  if (!container) return;

  try {
    const res = await fetch("/api/chat/sessions");
    const data = await res.json();

    if (data.success && data.sessions && data.sessions.length > 0) {
      container.innerHTML = "";
      data.sessions.forEach((s) => {
        const item = document.createElement("div");
        item.className = "session-item" + (s.session_id === currentSessionId ? " active" : "");
        item.dataset.sessionId = s.session_id;

        const titleText = s.preview || s.session_id.replace("session_", "Chat ");
        
        item.innerHTML = `
          <span class="session-icon">💬</span>
          <span class="session-title" title="${escapeHtml(titleText)}">${escapeHtml(titleText)}</span>
          <button class="session-delete-btn" title="Delete chat" onclick="deleteSession('${escapeJsString(s.session_id)}', event)">✕</button>
        `;

        item.addEventListener("click", (e) => {
          if (e.target.closest(".session-delete-btn")) return;
          switchSession(s.session_id);
          const sidebar = document.getElementById("sidebar");
          const backdrop = document.getElementById("sidebar-backdrop");
          if (window.innerWidth <= 768 && sidebar) {
            sidebar.classList.remove("open");
            if (backdrop) backdrop.classList.remove("active");
          }
        });

        container.appendChild(item);
      });
    } else {
      const dict = I18N[currentLang] || I18N.hi;
      container.innerHTML = `<div style="font-size:0.8rem; color:#888; padding: 10px 12px;">${dict.empty_history}</div>`;
    }
  } catch (err) {
    console.error("Error loading chat sessions:", err);
  }
}

function startNewChat() {
  currentSessionId = "session_" + Date.now().toString(36) + Math.random().toString(36).substring(2, 6);
  localStorage.setItem("ks_current_session", currentSessionId);

  // Clear messages and show hero empty state
  const messagesStream = document.getElementById("messages-stream");
  const emptyHero = document.getElementById("empty-state-hero");

  if (messagesStream) messagesStream.innerHTML = "";
  if (emptyHero) emptyHero.style.display = "flex";

  clearAttachment();
  loadSessions();

  const textarea = document.getElementById("chat-textarea");
  if (textarea) textarea.focus();
}

async function switchSession(sessionId) {
  if (sessionId === currentSessionId) return;
  currentSessionId = sessionId;
  localStorage.setItem("ks_current_session", sessionId);

  // Highlight active session in sidebar
  document.querySelectorAll(".session-item").forEach((el) => {
    el.classList.toggle("active", el.dataset.sessionId === sessionId);
  });

  await loadCurrentSessionHistory();
}

async function deleteSession(sessionId, event) {
  if (event) event.stopPropagation();
  const dict = I18N[currentLang] || I18N.hi;
  if (!confirm(dict.confirm_delete)) return;

  try {
    const res = await fetch(`/api/chat/sessions/${encodeURIComponent(sessionId)}`, {
      method: "DELETE"
    });
    const data = await res.json();

    if (data.success) {
      if (sessionId === currentSessionId) {
        startNewChat();
      } else {
        loadSessions();
      }
    }
  } catch (err) {
    console.error("Failed to delete session:", err);
  }
}

async function loadCurrentSessionHistory() {
  const messagesStream = document.getElementById("messages-stream");
  const emptyHero = document.getElementById("empty-state-hero");
  if (!messagesStream) return;

  try {
    const res = await fetch(`/api/chat/history/${encodeURIComponent(currentSessionId)}`);
    const data = await res.json();

    if (data.success && data.history && data.history.length > 0) {
      if (emptyHero) emptyHero.style.display = "none";
      messagesStream.innerHTML = "";

      data.history.forEach((turn) => {
        // User turn
        if (turn.user_query) {
          appendUserMessage(turn.user_query, null, false);
        }
        // Assistant turn
        if (turn.bot_response) {
          appendAssistantMessage({
            response: turn.bot_response,
            status_badges: [],
            citations: turn.citations ? JSON.parse(turn.citations) : [],
            vision: turn.image_analysis ? JSON.parse(turn.image_analysis) : null
          }, false);
        }
      });
      scrollToBottom();
    } else {
      messagesStream.innerHTML = "";
      if (emptyHero) emptyHero.style.display = "flex";
    }
  } catch (err) {
    console.error("Failed to load session history:", err);
  }
}

// ==========================================
// Starter Prompt Cards Trigger
// ==========================================
window.triggerStarterPrompt = function(promptKeyOrText) {
  let promptText = promptKeyOrText;
  if (STARTER_PROMPTS[promptKeyOrText]) {
    promptText = STARTER_PROMPTS[promptKeyOrText][currentLang] || STARTER_PROMPTS[promptKeyOrText].hi;
  }

  const textarea = document.getElementById("chat-textarea");
  if (textarea) {
    textarea.value = promptText;
    adjustTextareaHeight(textarea);
    handleSendMessage();
  }
};

// ==========================================
// Chat Input, Attachment & Auto-Resize
// ==========================================
function initChatInput() {
  const textarea = document.getElementById("chat-textarea");
  const sendBtn = document.getElementById("chat-send-btn");
  const attachBtn = document.getElementById("chat-attach-btn");
  const photoInput = document.getElementById("chat-photo-input");
  const clearThumbBtn = document.getElementById("clear-thumb-btn");

  if (textarea) {
    textarea.addEventListener("input", () => adjustTextareaHeight(textarea));
    textarea.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSendMessage();
      }
    });
  }

  if (sendBtn) {
    sendBtn.addEventListener("click", () => handleSendMessage());
  }

  if (attachBtn && photoInput) {
    attachBtn.addEventListener("click", () => photoInput.click());

    photoInput.addEventListener("change", (e) => {
      if (e.target.files && e.target.files[0]) {
        attachedChatFile = e.target.files[0];
        displayAttachmentPreview(attachedChatFile);
      }
    });
  }

  if (clearThumbBtn) {
    clearThumbBtn.addEventListener("click", clearAttachment);
  }
}

function adjustTextareaHeight(el) {
  el.style.height = "auto";
  el.style.height = Math.min(el.scrollHeight, 160) + "px";
}

function displayAttachmentPreview(file) {
  const bar = document.getElementById("attachment-preview-bar");
  const thumb = document.getElementById("preview-thumb-img");
  const filename = document.getElementById("preview-filename");

  if (filename) filename.innerText = file.name;

  if (thumb) {
    const reader = new FileReader();
    reader.onload = (e) => {
      thumb.src = e.target.result;
      if (bar) bar.style.display = "flex";
    };
    reader.readAsDataURL(file);
  }
}

function clearAttachment() {
  attachedChatFile = null;
  const photoInput = document.getElementById("chat-photo-input");
  const bar = document.getElementById("attachment-preview-bar");
  const thumb = document.getElementById("preview-thumb-img");

  if (photoInput) photoInput.value = "";
  if (thumb) thumb.src = "";
  if (bar) bar.style.display = "none";
}

// ==========================================
// Voice Input (Web Speech Recognition STT)
// ==========================================
function initVoice() {
  const micBtn = document.getElementById("chat-mic-btn");
  const textarea = document.getElementById("chat-textarea");

  if (!recognition || !micBtn) {
    if (micBtn) {
      micBtn.title = "Voice recognition not supported in this browser";
      micBtn.style.opacity = "0.5";
    }
    return;
  }

  micBtn.addEventListener("click", () => {
    if (micBtn.classList.contains("recording")) {
      recognition.stop();
      micBtn.classList.remove("recording");
    } else {
      micBtn.classList.add("recording");
      recognition.lang = currentLang === "hi" ? "hi-IN" : "en-IN";
      try {
        recognition.start();
      } catch (e) {
        micBtn.classList.remove("recording");
      }
    }
  });

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    if (textarea) {
      textarea.value = transcript;
      adjustTextareaHeight(textarea);
    }
    micBtn.classList.remove("recording");
    handleSendMessage();
  };

  recognition.onerror = () => {
    micBtn.classList.remove("recording");
  };

  recognition.onend = () => {
    micBtn.classList.remove("recording");
  };
}

// ==========================================
// Text to Speech (TTS) & Copy
// ==========================================
window.speakText = function(text, btnElement) {
  if (!("speechSynthesis" in window)) {
    alert(currentLang === "hi" ? "ब्राउज़र में आवाज़ समर्थित नहीं है।" : "Speech playback is not supported in this browser.");
    return;
  }

  // If already speaking the same message, toggle to pause/stop
  if (window.speechSynthesis.speaking && activeTtsButton === btnElement) {
    window.speechSynthesis.cancel();
    if (activeTtsButton) {
      activeTtsButton.classList.remove("active-playing");
      activeTtsButton.innerText = I18N[currentLang].listen_btn;
      activeTtsButton = null;
    }
    return;
  }

  window.speechSynthesis.cancel();
  if (activeTtsButton) {
    activeTtsButton.classList.remove("active-playing");
    activeTtsButton.innerText = I18N[currentLang].listen_btn;
  }

  const cleanText = text.replace(/[*#•`_]/g, "").replace(/\n+/g, " ");
  const utterance = new SpeechSynthesisUtterance(cleanText);
  utterance.lang = currentLang === "hi" ? "hi-IN" : "en-IN";
  utterance.rate = 0.95;

  const voices = window.speechSynthesis.getVoices();
  const targetCode = currentLang === "hi" ? "hi" : "en";
  const matchedVoice = voices.find((v) => v.lang.startsWith(targetCode));
  if (matchedVoice) utterance.voice = matchedVoice;

  if (btnElement) {
    activeTtsButton = btnElement;
    btnElement.classList.add("active-playing");
    btnElement.innerText = I18N[currentLang].stop_audio_btn;
  }

  utterance.onend = () => {
    if (activeTtsButton) {
      activeTtsButton.classList.remove("active-playing");
      activeTtsButton.innerText = I18N[currentLang].listen_btn;
      activeTtsButton = null;
    }
  };

  utterance.onerror = () => {
    if (activeTtsButton) {
      activeTtsButton.classList.remove("active-playing");
      activeTtsButton.innerText = I18N[currentLang].listen_btn;
      activeTtsButton = null;
    }
  };

  window.speechSynthesis.speak(utterance);
};

window.copyMessageText = async function(text, btnElement) {
  try {
    await navigator.clipboard.writeText(text);
    if (btnElement) {
      const originalText = btnElement.innerText;
      const feedback = currentLang === "hi" ? "✓ कॉपीड!" : "✓ Copied!";
      btnElement.innerText = feedback;
      btnElement.style.color = "#059669";
      setTimeout(() => {
        btnElement.innerText = originalText;
        btnElement.style.color = "";
      }, 2000);
    }
  } catch (err) {
    console.error("Failed to copy text:", err);
  }
};

// ==========================================
// Send Message & Multimodal Submission
// ==========================================
async function handleSendMessage() {
  const textarea = document.getElementById("chat-textarea");
  const text = (textarea ? textarea.value : "").trim();
  const sendingFile = attachedChatFile;

  if (!text && !sendingFile) return;

  const userQuery = text || (currentLang === "hi" ? "कृपया इस पौधे की पत्ती की जांच करें।" : "Please analyze this plant leaf photo.");

  // Hide starter hero
  const emptyHero = document.getElementById("empty-state-hero");
  if (emptyHero) emptyHero.style.display = "none";

  // Create preview URL for user bubble if photo attached
  let previewUrl = null;
  if (sendingFile) {
    previewUrl = URL.createObjectURL(sendingFile);
  }

  // Append user bubble
  appendUserMessage(userQuery, previewUrl, true);

  // Clear inputs immediately
  if (textarea) {
    textarea.value = "";
    adjustTextareaHeight(textarea);
  }
  clearAttachment();

  // Append Loading indicator
  const loadingId = "loading-" + Date.now();
  appendLoadingBubble(loadingId);
  scrollToBottom();

  try {
    let res;
    if (sendingFile) {
      const formData = new FormData();
      formData.append("message", userQuery);
      formData.append("file", sendingFile);
      formData.append("session_id", currentSessionId);
      formData.append("farmer_id", currentFarmerId);
      formData.append("lang", currentLang);

      res = await fetch("/api/chat/multimodal", {
        method: "POST",
        body: formData
      });
    } else {
      res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userQuery,
          session_id: currentSessionId,
          farmer_id: currentFarmerId,
          lang: currentLang
        })
      });
    }

    const data = await res.json();
    removeLoadingBubble(loadingId);

    if (data.success !== false) {
      appendAssistantMessage(data, true);
      loadSessions(); // refresh session list with latest turn
      rewardTaskCompletion(currentLang === "hi" ? "AI कृषि सलाह तैयार!" : "AI Advice Generated!", 3000);
    } else {
      appendAssistantMessage({
        response: data.error || (currentLang === "hi" ? "सर्वर से उत्तर प्राप्त करने में त्रुटि।" : "Error receiving server response.")
      }, true);
    }
  } catch (err) {
    removeLoadingBubble(loadingId);
    console.error("Chat error:", err);
    appendAssistantMessage({
      response: currentLang === "hi" ? "⚠️ सर्वर से संपर्क नहीं हो सका। कृपया पुनः प्रयास करें।" : "⚠️ Connection error. Please try again."
    }, true);
  }

  scrollToBottom();
}

// ==========================================
// DOM Message Rendering
// ==========================================
function appendUserMessage(text, photoUrl, scroll = true) {
  const stream = document.getElementById("messages-stream");
  if (!stream) return;

  const msgDiv = document.createElement("div");
  msgDiv.className = "message-row user-row";

  let imgTag = "";
  if (photoUrl) {
    imgTag = `<div class="user-attached-thumb"><img src="${photoUrl}" alt="Attached photo"></div>`;
  }

  msgDiv.innerHTML = `
    <div class="user-bubble">
      ${imgTag}
      <div class="user-text">${escapeHtml(text)}</div>
    </div>
  `;

  stream.appendChild(msgDiv);
  if (scroll) scrollToBottom();
}

function appendLoadingBubble(id) {
  const stream = document.getElementById("messages-stream");
  if (!stream) return;

  const dict = I18N[currentLang] || I18N.hi;
  const loadDiv = document.createElement("div");
  loadDiv.className = "message-row assistant-row";
  loadDiv.id = id;

  loadDiv.innerHTML = `
    <div class="assistant-avatar">🌱</div>
    <div class="assistant-card">
      <div class="loading-state">
        <span class="loading-dots">● ● ●</span>
        <span>${escapeHtml(dict.loading_msg)}</span>
      </div>
    </div>
  `;

  stream.appendChild(loadDiv);
}

function removeLoadingBubble(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function appendAssistantMessage(data, scroll = true) {
  const stream = document.getElementById("messages-stream");
  if (!stream) return;

  const dict = I18N[currentLang] || I18N.hi;
  const msgDiv = document.createElement("div");
  msgDiv.className = "message-row assistant-row";

  // Reassuring status pills
  let statusHtml = "";
  if (data.status_badges && data.status_badges.length > 0) {
    statusHtml = `
      <div class="status-badges-strip">
        ${data.status_badges.map((b) => `<span class="badge-pill">${escapeHtml(currentLang === "hi" ? b.label_hi : b.label_en)}</span>`).join("")}
      </div>
    `;
  }

  // YOLO Vision Diagnostic Badge
  let visionHtml = "";
  if (data.vision && data.vision.success) {
    const v = data.vision;
    const diseaseName = currentLang === "hi" ? v.disease_name_hindi : v.disease_name_en;
    const cropName = currentLang === "hi" ? v.crop : v.crop_en;
    visionHtml = `
      <div class="vision-diagnostic-card">
        <div class="vision-header">
          <span class="vision-icon">🍃</span>
          <span class="vision-disease">${escapeHtml(diseaseName)}</span>
          <span class="vision-crop">(${escapeHtml(cropName)})</span>
        </div>
        <div class="vision-meta">
          <span>${dict.confidence}: <strong>${v.confidence_score}%</strong></span>
          ${v.severity_percentage ? `<span>• ${dict.foliar_damage}: <strong>${v.severity_percentage}%</strong></span>` : ""}
        </div>
      </div>
    `;
  }

  // Formatted response markdown
  const formattedContent = renderMarkdown(data.response || "");

  // Grounded Citations Chips
  let citationsHtml = "";
  if (data.citations && data.citations.length > 0) {
    citationsHtml = `
      <div class="grounded-citations-box">
        <div class="citations-header">${dict.citations_title}</div>
        <div class="citations-chips-wrap">
          ${data.citations.map((c) => `<span class="citation-chip">${escapeHtml(c.citation_badge || c.source)}</span>`).join("")}
        </div>
      </div>
    `;
  }

  // Message Action Buttons (Copy & Listen)
  const escapedResp = escapeJsString(data.response || '');
  const actionsHtml = `
    <div class="card-footer-actions">
      <button class="action-btn copy-btn" onclick="copyMessageText(\`${escapedResp}\`, this)" title="कॉपी करें / Copy advisory">
        ${dict.copy_btn}
      </button>
      <button class="action-btn tts-btn" onclick="speakText(\`${escapedResp}\`, this)" title="बोलकर सुनें / Listen">
        ${dict.listen_btn}
      </button>
    </div>
  `;

  msgDiv.innerHTML = `
    <div class="assistant-avatar">🌱</div>
    <div class="assistant-card floatable" data-anti-gravity>
      ${statusHtml}
      ${visionHtml}
      <div class="response-content">${formattedContent}</div>
      ${citationsHtml}
      ${actionsHtml}
    </div>
  `;

  stream.appendChild(msgDiv);
  if (scroll) scrollToBottom();
}

function scrollToBottom() {
  const viewport = document.getElementById("chat-viewport");
  if (viewport) {
    viewport.scrollTop = viewport.scrollHeight;
  }
}

/**
 * Robust, clean Markdown parser supporting headers, bold/italic, lists (ul/ol), blockquotes and inline code.
 */
function renderMarkdown(text) {
  if (!text) return "";

  const lines = text.split("\n");
  const result = [];
  let inUl = false;
  let inOl = false;

  function closeLists() {
    if (inUl) {
      result.push("</ul>");
      inUl = false;
    }
    if (inOl) {
      result.push("</ol>");
      inOl = false;
    }
  }

  for (let i = 0; i < lines.length; i++) {
    const rawLine = lines[i];
    const trimmed = rawLine.trim();

    if (!trimmed) {
      closeLists();
      continue;
    }

    // Unordered List item: starts with * or - or •
    const ulMatch = trimmed.match(/^[\*\-\•]\s+(.*)$/);
    if (ulMatch) {
      if (inOl) {
        result.push("</ol>");
        inOl = false;
      }
      if (!inUl) {
        result.push("<ul>");
        inUl = true;
      }
      result.push(`<li>${formatInline(ulMatch[1])}</li>`);
      continue;
    }

    // Ordered List item: starts with 1. 2. etc.
    const olMatch = trimmed.match(/^\d+\.\s+(.*)$/);
    if (olMatch) {
      if (inUl) {
        result.push("</ul>");
        inUl = false;
      }
      if (!inOl) {
        result.push("<ol>");
        inOl = true;
      }
      result.push(`<li>${formatInline(olMatch[1])}</li>`);
      continue;
    }

    // Not a list line, close any open list
    closeLists();

    // Headers
    if (trimmed.startsWith("### ")) {
      result.push(`<h4>${formatInline(trimmed.substring(4))}</h4>`);
    } else if (trimmed.startsWith("## ")) {
      result.push(`<h3>${formatInline(trimmed.substring(3))}</h3>`);
    } else if (trimmed.startsWith("# ")) {
      result.push(`<h2>${formatInline(trimmed.substring(2))}</h2>`);
    } else if (trimmed.startsWith("> ")) {
      result.push(`<blockquote>${formatInline(trimmed.substring(2))}</blockquote>`);
    } else {
      result.push(`<p>${formatInline(trimmed)}</p>`);
    }
  }

  closeLists();
  return result.join("");
}

function formatInline(str) {
  if (!str) return "";
  let s = escapeHtml(str);
  // Bold **text**
  s = s.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  // Italic *text* or _text_
  s = s.replace(/\*([^\*\s][^\*]*?)\*/g, "<em>$1</em>");
  s = s.replace(/_([^_\s][^_]*?)_/g, "<em>$1</em>");
  // Inline code `code`
  s = s.replace(/`([^`]+)`/g, "<code>$1</code>");
  return s;
}

// ==========================================
// Modal System (Overlay Sheets)
// ==========================================
window.openModal = function(modalId) {
  const modal = document.getElementById(modalId);
  if (!modal) return;
  modal.classList.add("active");
  document.body.classList.add("modal-open");

  // Specific on-open triggers
  if (modalId === "modal-weather") {
    searchWeatherModal();
  } else if (modalId === "modal-schemes") {
    searchSchemesModal();
  }
};

window.closeModal = function(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.remove("active");
  document.body.classList.remove("modal-open");
};

function initModals() {
  // Close modals on clicking overlay background
  document.querySelectorAll(".modal-overlay").forEach((overlay) => {
    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) {
        overlay.classList.remove("active");
        document.body.classList.remove("modal-open");
      }
    });
  });

  // Close modals on Escape key
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      document.querySelectorAll(".modal-overlay.active").forEach((m) => {
        m.classList.remove("active");
      });
      document.body.classList.remove("modal-open");
    }
  });

  // Setup specialized tool handlers
  setupDiseaseModal();
  setupSoilModal();
  setupCropModal();
  setupProfileModal();
}

// ==========================================
// Live Weather & Top Nav Widget
// ==========================================
async function loadLiveWeather(district = "Lucknow") {
  const topText = document.getElementById("top-weather-text");
  try {
    const res = await fetch(`/api/weather?district=${encodeURIComponent(district)}`);
    const data = await res.json();
    if (data.success && data.current) {
      liveWeatherCache = data;
      if (topText) {
        topText.innerHTML = `<strong>${data.location}</strong>: ${data.current.temperature}°C • ${data.current.condition}`;
      }
    }
  } catch (err) {
    if (topText) topText.innerText = "Lucknow: 28°C ☀️";
  }
}

window.searchWeatherModal = async function() {
  const input = document.getElementById("modal-weather-district");
  const content = document.getElementById("modal-weather-content");
  const district = (input && input.value.trim()) || "Lucknow";

  if (!content) return;
  content.innerHTML = `<div style="text-align:center; padding: 24px; color: #059669;">🌦️ ${currentLang === 'hi' ? 'मौसम आंकड़े प्राप्त किए जा रहे हैं...' : 'Fetching meteorological forecast...'}</div>`;

  try {
    const res = await fetch(`/api/weather?district=${encodeURIComponent(district)}`);
    const data = await res.json();

    if (data.success) {
      liveWeatherCache = data;
      rewardTaskCompletion(currentLang === "hi" ? "मौसम आंकड़े प्राप्त हुए!" : "Weather Forecast Loaded!", 2800);
      const curr = data.current;
      const isEn = currentLang === "en";

      let advisoriesHtml = "";
      if (data.agricultural_advisories && data.agricultural_advisories.length > 0) {
        advisoriesHtml = data.agricultural_advisories.map((a) => `
          <div style="background:#f0fdf4; border-left:4px solid #059669; padding:12px; border-radius:8px; margin-bottom:10px;">
            <strong style="color:#064e3b; font-size:0.95rem;">${a.title}</strong><br>
            <span style="font-size:0.9rem; color:#1e293b; line-height:1.5;">${a.advice}</span>
          </div>
        `).join("");
      }

      let forecastHtml = "";
      if (data.forecast) {
        forecastHtml = `
          <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(110px, 1fr)); gap:10px; margin-top:10px;">
            ${data.forecast.map((f) => `
              <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:10px 8px; text-align:center;">
                <div style="font-size:0.8rem; color:#64748b; font-weight:500;">${f.date}</div>
                <div style="font-weight:700; color:#059669; font-size:1.1rem; margin:4px 0;">${f.temp_max}° / ${f.temp_min}°</div>
                <div style="font-size:0.78rem; color:#0284c7; font-weight:600;">🌧️ ${f.rain_prob}% ${isEn ? 'Rain' : 'बारिश'}</div>
                <div style="font-size:0.75rem; color:#475569; margin-top:2px;">${f.condition}</div>
              </div>
            `).join("")}
          </div>
        `;
      }

      content.innerHTML = `
        <div style="background:linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%); border-radius:12px; padding:18px; display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; border:1px solid rgba(16,185,129,0.2);">
          <div>
            <h3 style="color:#064e3b; margin-bottom:4px; font-size:1.25rem;">${data.location}</h3>
            <span style="font-size:0.85rem; color:#047857;">${isEn ? 'Source' : 'स्रोत'}: ${data.source}</span>
          </div>
          <div style="text-align:right;">
            <div style="font-size:2rem; font-weight:800; color:#059669;">${curr.temperature}°C</div>
            <div style="font-size:0.84rem; color:#475569;">${isEn ? 'Humidity' : 'नमी'}: ${curr.humidity}% | ${isEn ? 'Wind' : 'हवा'}: ${curr.wind_speed} km/h</div>
          </div>
        </div>
        <h4 style="color:#064e3b; margin-bottom:10px;">${isEn ? '🌾 Agricultural Weather Advisories' : '🌾 कृषि मौसम परामर्श'}</h4>
        ${advisoriesHtml}
        <h4 style="color:#064e3b; margin-top:16px; margin-bottom:10px;">${isEn ? '📅 5-Day Forecast' : '📅 आगामी 5 दिनों का पूर्वानुमान'}</h4>
        ${forecastHtml}
      `;
    } else {
      content.innerHTML = `<div style="color:#ef4444; padding:12px; background:#fef2f2; border-radius:8px;">${data.error || "Unable to load weather."}</div>`;
    }
  } catch (err) {
    content.innerHTML = `<div style="color:#ef4444; padding:12px;">Error fetching weather data.</div>`;
  }
};

// ==========================================
// Foliar Disease Modal (AI Vision)
// ==========================================
function setupDiseaseModal() {
  const dropzone = document.getElementById("modal-disease-dropzone");
  const fileInput = document.getElementById("modal-disease-file");

  if (!dropzone || !fileInput) return;

  dropzone.addEventListener("click", () => fileInput.click());

  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.style.borderColor = "#059669";
    dropzone.style.background = "#ecfdf5";
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.style.borderColor = "#86efac";
    dropzone.style.background = "#f8fbf9";
  });

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.style.borderColor = "#86efac";
    dropzone.style.background = "#f8fbf9";
    if (e.dataTransfer.files.length > 0) {
      runDiseaseDetection(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
      runDiseaseDetection(e.target.files[0]);
    }
  });
}

async function runDiseaseDetection(file) {
  const resultArea = document.getElementById("modal-disease-result");
  const cropSelect = document.getElementById("modal-disease-crop");
  const cropHint = cropSelect ? cropSelect.value : "";

  if (!resultArea) return;
  resultArea.innerHTML = `<div style="text-align:center; padding:20px; color:#059669;">📸 ${currentLang === 'hi' ? 'YOLO विज़न मॉडल पत्ती का विश्लेषण कर रहा है...' : 'YOLO Vision model is analyzing leaf symptoms...'}</div>`;

  const formData = new FormData();
  formData.append("file", file);
  formData.append("crop_hint", cropHint);
  formData.append("lang", currentLang);

  if (liveWeatherCache && liveWeatherCache.forecast && liveWeatherCache.forecast[0]) {
    formData.append("rain_forecast", liveWeatherCache.forecast[0].rain_prob >= 30);
  }

  try {
    const res = await fetch("/api/disease/detect", {
      method: "POST",
      body: formData
    });
    const data = await res.json();
    const isEn = currentLang === "en";

    if (data.success) {
      rewardTaskCompletion(currentLang === "hi" ? "फसल रोग निदान पूर्ण!" : "Leaf Disease Diagnosed!", 3200);
      const dName = isEn ? data.disease_name_en : data.disease_name_hindi;
      const cName = isEn ? data.crop_en : data.crop;
      const symptoms = isEn ? data.symptoms_en : data.symptoms;
      const action = isEn ? data.immediate_cultural_action_en : data.immediate_cultural_action;
      const organic = isEn ? data.organic_ipm_remedy_en : data.organic_ipm_remedy;
      const chem = isEn ? data.chemical_solution_en : data.chemical_solution;
      const sprayAdv = isEn ? data.weather_spray_advisory_en : data.weather_spray_advisory;
      const kvkNote = isEn ? data.kvk_escalation_note_en : data.kvk_escalation_note;

      resultArea.innerHTML = `
        <div style="background:#ffffff; border:1px solid #86efac; border-radius:12px; padding:18px; box-shadow:0 4px 16px rgba(0,0,0,0.05);">
          <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #f1f5f9; padding-bottom:10px; margin-bottom:12px;">
            <div>
              <h3 style="color:#064e3b; margin-bottom:2px; font-size:1.15rem;">${escapeHtml(dName)}</h3>
              <span style="font-size:0.86rem; color:#64748b;">${isEn ? 'Crop' : 'फसल'}: <strong style="color:#059669;">${escapeHtml(cName)}</strong></span>
            </div>
            <span class="badge-pill" style="font-weight:700;">
              ${data.confidence_score}% ${isEn ? 'Confidence' : 'विश्वसनीयता'}
            </span>
          </div>

          <p style="margin-bottom:8px; font-size:0.92rem;"><strong>🔍 ${isEn ? 'Symptoms' : 'लक्षण'}:</strong> ${escapeHtml(symptoms)}</p>
          <p style="margin-bottom:8px; font-size:0.92rem;"><strong>⚡ ${isEn ? 'Immediate Action' : 'तत्काल उपाय'}:</strong> ${escapeHtml(action)}</p>
          <p style="margin-bottom:10px; font-size:0.92rem;"><strong>🌿 ${isEn ? 'Organic & IPM' : 'जैविक समाधान'}:</strong> ${escapeHtml(organic)}</p>

          <div style="background:#fefce8; border-left:4px solid #eab308; padding:10px 14px; border-radius:8px; margin:12px 0; font-size:0.9rem;">
            <strong style="color:#854d0e;">🧪 ${isEn ? 'Safe Chemical Spray' : 'संस्तुत रासायनिक उपचार'}:</strong><br>
            • ${chem.name} | ${isEn ? 'Dose' : 'मात्रा'}: ${chem.dose}<br>
            • ${isEn ? 'Precaution' : 'सावधानी'}: ${chem.precaution}
          </div>

          <div style="background:#f0f9ff; border:1px solid #bae6fd; padding:10px 14px; border-radius:8px; font-size:0.86rem; color:#0369a1; margin-bottom:10px;">
            🌦️ ${sprayAdv}
          </div>

          <div style="font-size:0.82rem; color:#b91c1c; border-top:1px dashed #e2e8f0; padding-top:8px;">
            📞 ${kvkNote}
          </div>

          <div style="margin-top:16px; display:flex; justify-content:flex-end; gap:10px;">
            <button class="action-btn tts-btn" onclick="speakText(\`${escapeJsString(dName + '. ' + symptoms + '. ' + action)}\`, this)">
              ${isEn ? '🔊 Listen' : '🔊 सुनो'}
            </button>
            <button class="btn-primary" style="padding:7px 14px; font-size:0.86rem;" onclick="closeModal('modal-disease'); triggerStarterPrompt('${escapeJsString((isEn ? 'Tell me more about treating ' : 'विस्तार से बताएं कि ') + dName + (isEn ? ' in ' : ' का ') + cName + (isEn ? '' : ' में उपचार कैसे करें'))}')">
              💬 ${isEn ? 'Chat about this' : 'सहायक से पूछें'}
            </button>
          </div>
        </div>
      `;
    } else {
      resultArea.innerHTML = `<div style="background:#fef2f2; color:#b91c1c; padding:12px; border-radius:8px; border:1px solid #fecaca;">${data.rejection_reason || data.error || "Analysis failed."}</div>`;
    }
  } catch (err) {
    resultArea.innerHTML = `<div style="color:#b91c1c; padding:12px;">Error during disease analysis.</div>`;
  }
}

// ==========================================
// Soil Health Card Modal
// ==========================================
function setupSoilModal() {
  const form = document.getElementById("modal-soil-form");
  const resultArea = document.getElementById("modal-soil-result");

  if (!form || !resultArea) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const isEn = currentLang === "en";
    resultArea.innerHTML = `<div style="text-align:center; padding:18px; color:#059669;">🧪 ${isEn ? 'Analyzing Soil Parameters...' : 'मृदा स्वास्थ्य कार्ड का विश्लेषण जारी है...'}</div>`;

    const feInput = document.getElementById("modal-soil-fe");
    const payload = {
      ph: parseFloat(document.getElementById("modal-soil-ph").value),
      oc: parseFloat(document.getElementById("modal-soil-oc").value),
      n: parseFloat(document.getElementById("modal-soil-n").value),
      p: parseFloat(document.getElementById("modal-soil-p").value),
      k: parseFloat(document.getElementById("modal-soil-k").value),
      ec: parseFloat(document.getElementById("modal-soil-ec").value),
      zn: parseFloat(document.getElementById("modal-soil-zn").value),
      s: parseFloat(document.getElementById("modal-soil-s").value),
      fe: feInput ? parseFloat(feInput.value || 5.0) : 5.0,
      state: document.getElementById("modal-soil-state").value,
      district: document.getElementById("modal-soil-district").value
    };

    try {
      const res = await fetch("/api/soil/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();

      if (data.health_score !== undefined) {
        rewardTaskCompletion(currentLang === "hi" ? "मृदा स्वास्थ्य विश्लेषित!" : "Soil Analysis Complete!", 3000);
        const defs = isEn ? data.deficiencies_en : data.deficiencies;
        const summary = isEn ? data.english_summary : data.hindi_summary;

        const defHtml = (defs && defs.length > 0)
          ? defs.map((d) => `<li>${escapeHtml(d)}</li>`).join("")
          : `<li>${isEn ? 'No critical deficiencies detected.' : 'कोई गंभीर पोषक कमी नहीं पाई गई।'}</li>`;

        const amendHtml = (data.amendments && data.amendments.length > 0)
          ? data.amendments.map((a) => `
              <li><strong>${escapeHtml(isEn ? a.action_en : a.action)}:</strong> ${escapeHtml(isEn ? a.dose_en : a.dose)} (${isEn ? 'Priority' : 'महत्व'}: ${escapeHtml(isEn ? a.importance_en : a.importance)})</li>
            `).join("")
          : `<li>${isEn ? 'Maintain regular organic compost.' : 'नियमित जैविक खाद व वर्मीकम्पोस्ट जारी रखें।'}</li>`;

        const labsHtml = (data.nearby_labs && data.nearby_labs.length > 0)
          ? data.nearby_labs.map((l) => `
              <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:10px; margin-bottom:8px; font-size:0.86rem;">
                <strong style="color:#059669;">${l.name}</strong> (${l.type})<br>
                <span>📍 ${l.address} | 📞 ${l.contact} | 💰 ${l.fee}</span>
              </div>
            `).join("")
          : "";

        resultArea.innerHTML = `
          <div style="background:#ffffff; border:1px solid #86efac; border-radius:12px; padding:18px; box-shadow:0 2px 10px rgba(0,0,0,0.04);">
            <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #f1f5f9; padding-bottom:10px; margin-bottom:12px;">
              <h3 style="color:#064e3b; font-size:1.15rem;">${isEn ? 'Soil Health Score' : 'मृदा स्वास्थ्य स्कोर'}: ${data.health_score}/100</h3>
              <span class="badge-pill">${data.soil_classification.name_hindi}</span>
            </div>
            <p style="margin-bottom:12px; font-size:0.94rem; line-height:1.55;">${escapeHtml(summary)}</p>
            
            <h4 style="color:#b91c1c; margin:12px 0 6px 0;">${isEn ? '⚠️ Detected Nutrient Deficiencies:' : '⚠️ पोषक तत्वों की कमियां:'}</h4>
            <ul style="padding-left:22px; font-size:0.9rem; margin-bottom:12px; line-height:1.5;">${defHtml}</ul>

            <h4 style="color:#059669; margin:12px 0 6px 0;">${isEn ? '🌾 Corrective Soil Amendments:' : '🌾 सुधारात्मक कृषि सिफारिशें:'}</h4>
            <ul style="padding-left:22px; font-size:0.9rem; margin-bottom:12px; line-height:1.5;">${amendHtml}</ul>

            <h4 style="color:#0284c7; margin:14px 0 8px 0;">${isEn ? '🏛️ Nearby Govt Labs & KVKs:' : '🏛️ नजदीकी सरकारी मृदा प्रयोगशालाएं:'}</h4>
            ${labsHtml}
          </div>
        `;
      }
    } catch (err) {
      resultArea.innerHTML = `<div style="color:#b91c1c; padding:12px;">Error analyzing soil parameters.</div>`;
    }
  });
}

// ==========================================
// Crop ML Recommender Modal
// ==========================================
function setupCropModal() {
  const form = document.getElementById("modal-crop-form");
  const resultArea = document.getElementById("modal-crop-result");

  if (!form || !resultArea) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const isEn = currentLang === "en";
    resultArea.innerHTML = `<div style="text-align:center; padding:18px; color:#059669;">🌱 ${isEn ? 'Calculating optimal crops with ML...' : 'मशीन लर्निंग मॉडल द्वारा श्रेष्ठ फसलों की गणना जारी है...'}</div>`;

    const payload = {
      n: parseFloat(document.getElementById("modal-crop-n").value),
      p: parseFloat(document.getElementById("modal-crop-p").value),
      k: parseFloat(document.getElementById("modal-crop-k").value),
      temperature: parseFloat(document.getElementById("modal-crop-temp").value),
      humidity: parseFloat(document.getElementById("modal-crop-humidity").value),
      ph: parseFloat(document.getElementById("modal-crop-ph").value),
      rainfall: parseFloat(document.getElementById("modal-crop-rainfall").value),
      month: parseInt(document.getElementById("modal-crop-month").value, 10)
    };

    try {
      const res = await fetch("/api/crop/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();

      if (data.top_recommendations && data.top_recommendations.length > 0) {
        rewardTaskCompletion(currentLang === "hi" ? "फसल चयन AI पूर्ण!" : "Crop Recommendations Ready!", 3000);
        const cardsHtml = data.top_recommendations.map((c, idx) => {
          const cropTitle = isEn ? `${c.crop_key.toUpperCase()} (${c.hindi_name})` : c.hindi_name;
          return `
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:14px; margin-bottom:10px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <strong style="color:#059669; font-size:1.05rem;">#${idx+1} ${cropTitle}</strong>
                <span class="badge-pill">${c.suitability_score}% ${isEn ? 'Suitability' : 'अनुकूलता'}</span>
              </div>
              <p style="font-size:0.88rem; color:#334155; margin:8px 0; line-height:1.45;">${escapeHtml(c.description)}</p>
              <div style="font-size:0.82rem; color:#64748b; display:flex; gap:14px; flex-wrap:wrap;">
                <span>📅 ${isEn ? 'Sowing' : 'बुवाई'}: <strong>${c.sowing_months}</strong></span>
                <span>💧 ${isEn ? 'Water' : 'पानी'}: <strong>${c.water_need}</strong></span>
                <span>🍂 ${isEn ? 'Season' : 'मौसम'}: <strong>${c.season}</strong></span>
              </div>
            </div>
          `;
        }).join("");

        resultArea.innerHTML = `
          <div style="background:#ffffff; border:1px solid #86efac; border-radius:12px; padding:18px;">
            <h4 style="color:#064e3b; margin-bottom:12px;">🌟 ${isEn ? 'Top Recommended Crops' : 'शीर्ष अनुशंसित फसलें'} (${data.current_season}):</h4>
            ${cardsHtml}
            <div style="background:#f0fdf4; border:1px solid #bbf7d0; padding:10px 14px; border-radius:8px; font-size:0.88rem; color:#166534; margin-top:10px;">
              💡 ${escapeHtml(data.summary_hindi)}
            </div>
          </div>
        `;
      }
    } catch (err) {
      resultArea.innerHTML = `<div style="color:#b91c1c; padding:12px;">Error calculating crop recommendations.</div>`;
    }
  });
}

// ==========================================
// Government Schemes Modal
// ==========================================
window.searchSchemesModal = async function() {
  const input = document.getElementById("modal-schemes-search");
  const content = document.getElementById("modal-schemes-content");
  const q = (input && input.value.trim()) || "";

  if (!content) return;
  content.innerHTML = `<div style="text-align:center; padding:18px; color:#059669;">🏛️ ${currentLang === 'hi' ? 'योजनाएं खोजी जा रही हैं...' : 'Searching agricultural schemes...'}</div>`;

  try {
    const res = await fetch(`/api/schemes?q=${encodeURIComponent(q)}`);
    const data = await res.json();
    const isEn = currentLang === "en";

    if (data.schemes && data.schemes.length > 0) {
      rewardTaskCompletion(currentLang === "hi" ? "योजनाएं खोजी गईं!" : "Schemes Discovered!", 2500);
      content.innerHTML = data.schemes.map((s) => `
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:16px; margin-bottom:12px; box-shadow:0 2px 6px rgba(0,0,0,0.03);">
          <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #f1f5f9; padding-bottom:8px; margin-bottom:10px;">
            <h3 style="color:#064e3b; font-size:1.05rem;">🏛️ ${escapeHtml(s.name)}</h3>
            <span style="font-size:0.75rem; background:#ecfdf5; color:#065f46; padding:3px 10px; border-radius:12px; border:1px solid #a7f3d0;">${escapeHtml(s.ministry)}</span>
          </div>
          <p style="font-size:0.9rem; color:#334155; margin-bottom:10px; line-height:1.45;">${escapeHtml(s.objective)}</p>
          <div style="background:#f8fafc; padding:10px 12px; border-radius:8px; font-size:0.84rem; line-height:1.6; border:1px solid #f1f5f9;">
            <strong>🎯 ${isEn ? 'Eligibility' : 'पात्रता'}:</strong> ${escapeHtml(s.eligibility)}<br>
            <strong>💰 ${isEn ? 'Benefits' : 'लाभ'}:</strong> ${escapeHtml(s.benefits)}<br>
            <strong>📝 ${isEn ? 'How to Apply' : 'आवेदन'}:</strong> ${escapeHtml(s.how_to_apply)}<br>
            <strong>📞 ${isEn ? 'Helpline' : 'हेल्पलाइन'}:</strong> <span style="color:#dc2626; font-weight:700;">${escapeHtml(s.helpline)}</span>
          </div>
        </div>
      `).join("");
    } else {
      content.innerHTML = `<div style="text-align:center; color:#64748b; padding:18px;">${isEn ? 'No schemes found matching query.' : 'कोई योजना नहीं मिली।'}</div>`;
    }
  } catch (err) {
    content.innerHTML = `<div style="color:#b91c1c; padding:12px;">Error searching schemes.</div>`;
  }
};

// ==========================================
// Farmer Profile Modal
// ==========================================
async function loadFarmerProfile() {
  try {
    const res = await fetch(`/api/profile?farmer_id=${encodeURIComponent(currentFarmerId)}`);
    const data = await res.json();
    if (data && data.name) {
      document.getElementById("profile-name").value = data.name || "रामसिंह वर्मा";
      document.getElementById("profile-village").value = data.village || "बख्शी का तालाब";
      document.getElementById("profile-district").value = data.district || "Lucknow";
      document.getElementById("profile-state").value = data.state || "Uttar Pradesh";
      document.getElementById("profile-acres").value = data.farm_size_acres || 3.5;
      document.getElementById("profile-crop").value = data.current_crop || "गेहूं";
      document.getElementById("profile-soil").value = data.soil_type || "जलोढ़ दोमट";
      const irrEl = document.getElementById("profile-irrigation");
      if (irrEl) irrEl.value = data.irrigation_type || "ट्यूबवेल";

      // Update sidebar footer
      const nameEl = document.getElementById("sidebar-farmer-name");
      const metaEl = document.getElementById("sidebar-farmer-meta");
      if (nameEl) nameEl.innerText = data.name;
      if (metaEl) metaEl.innerText = `${data.district}, ${data.state} • ${data.current_crop}`;
    }
  } catch (err) {
    console.error("Failed to load profile:", err);
  }
}

function setupProfileModal() {
  const form = document.getElementById("modal-profile-form");
  const status = document.getElementById("modal-profile-status");

  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const isEn = currentLang === "en";

    const payload = {
      farmer_id: currentFarmerId,
      name: document.getElementById("profile-name").value,
      village: document.getElementById("profile-village").value,
      district: document.getElementById("profile-district").value,
      state: document.getElementById("profile-state").value,
      farm_size_acres: parseFloat(document.getElementById("profile-acres").value),
      current_crop: document.getElementById("profile-crop").value,
      soil_type: document.getElementById("profile-soil").value,
      irrigation_type: document.getElementById("profile-irrigation").value,
      language: currentLang === "hi" ? "Hindi" : "English"
    };

    try {
      const res = await fetch("/api/profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();

      if (status) {
        status.innerHTML = `<div style="color:#059669; font-weight:600; padding:8px 12px; background:#ecfdf5; border-radius:6px;">${isEn ? '✅ Profile updated successfully!' : '✅ प्रोफाइल सफलतापूर्वक सुरक्षित हुई!'}</div>`;
        rewardTaskCompletion(currentLang === "hi" ? "प्रोफाइल सुरक्षित!" : "Profile Saved!", 2500);
        setTimeout(() => { status.innerHTML = ""; }, 3000);
      }

      // Update sidebar display
      const nameEl = document.getElementById("sidebar-farmer-name");
      const metaEl = document.getElementById("sidebar-farmer-meta");
      if (nameEl) nameEl.innerText = payload.name;
      if (metaEl) metaEl.innerText = `${payload.district}, ${payload.state} • ${payload.current_crop}`;

      loadLiveWeather(payload.district);
    } catch (err) {
      if (status) status.innerHTML = `<div style="color:#b91c1c;">Failed to save profile.</div>`;
    }
  });
}

// ==========================================
// Utilities
// ==========================================
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

// ==========================================
// Interactive Zero-Gravity Physics Setup & Reward Loop
// ==========================================
let antigravity = null;

function rewardTaskCompletion(reason, durationMs = 3000) {
  if (window.antigravity && typeof window.antigravity.triggerBurst === "function") {
    window.antigravity.triggerBurst({ reason, durationMs });
  } else if (typeof window.triggerAntiGravityBurst === "function") {
    window.triggerAntiGravityBurst({ reason, durationMs });
  } else {
    window.dispatchEvent(new CustomEvent("antigravity:burst", { detail: { reason, durationMs } }));
  }
}
window.rewardTaskCompletion = rewardTaskCompletion;

document.addEventListener("DOMContentLoaded", () => {
  if (typeof AntiGravityEngine !== "undefined") {
    // Note: Exclude modal dialogs and sidebar menu items so modals remain completely stable!
    antigravity = new AntiGravityEngine({
      selector: '.floatable, [data-anti-gravity], .starter-card, .weather-pill, .model-badge, .hero-icon, .assistant-card',
      gravity: -0.08,
      damping: 0.988,
      elasticity: 0.8,
      repulsionRadius: 190,
      repulsionStrength: 500,
      enableDrag: true,
      burstDurationMs: 3000,
      onToggle: (active) => {
        const toggleBtn = document.getElementById("zero-g-toggle-btn");
        const statusBanner = document.getElementById("zero-g-status-banner");
        const btnText = document.getElementById("zero-g-btn-text");

        if (toggleBtn) {
          toggleBtn.classList.toggle("active", active);
        }
        if (statusBanner && !active) {
          statusBanner.classList.remove("visible", "ag-reward-burst");
        } else if (statusBanner && active && !statusBanner.classList.contains("ag-reward-burst")) {
          statusBanner.classList.add("visible");
        }
        if (btnText) {
          btnText.innerText = active ? "Landing Mode" : "Zero-G Mode";
        }
      }
    });

    window.antigravity = antigravity;

    // Attach click handler to navbar toggle button
    const toggleBtn = document.getElementById("zero-g-toggle-btn");
    if (toggleBtn) {
      toggleBtn.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        antigravity.toggle();
      });
    }

    // Keyboard shortcut trigger (Shift + G)
    window.addEventListener("keydown", (e) => {
      if (e.shiftKey && e.key.toLowerCase() === "g") {
        const activeTag = document.activeElement ? document.activeElement.tagName.toLowerCase() : "";
        if (activeTag !== "input" && activeTag !== "textarea") {
          e.preventDefault();
          antigravity.toggle();
        }
      }
    });
  }
});
