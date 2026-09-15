/**
 * Gemini KrishiSaathi — Advanced Multimodal AI Agricultural Advisory System
 * Replicates Official Google Gemini Interface (Matching User Screenshots)
 * Complete interactive features: Expandable + Menu, Model Picker (Flash/Pro),
 * Chat/Spark Mode, Search Chats, Notebooks, Categories & Agro-Modals.
 */

// ==========================================
// Application State
// ==========================================
let currentSessionId = localStorage.getItem("ks_current_session") || ("session_" + Date.now().toString(36) + Math.random().toString(36).substring(2, 6));
let currentFarmerId = "default_farmer";
let currentLang = localStorage.getItem("ks_current_lang") || "en";
const ACTIVE_MODEL = "Flash"; // Hardcoded single backend model
let liveWeatherCache = null;
let attachedChatFile = null;
let activeTtsButton = null;
let customNotebooks = JSON.parse(localStorage.getItem("ks_custom_notebooks") || "[]");

// ==========================================
// Starter Prompts Bilingual Catalog
// ==========================================
const STARTER_PROMPTS = {
  starter_1: {
    en: "What is the recommended fertilizer schedule for wheat crop?",
    hi: "गेहूं में खाद की सही मात्रा और डालने का समय बताओ"
  },
  starter_2: {
    en: "Leaves are turning yellow with dark spots, how to treat?",
    hi: "पत्ते पीले पड़ रहे हैं और काले धब्बे हैं, क्या उपाय करें?"
  },
  starter_3: {
    en: "What is the 5-day weather and rainfall forecast?",
    hi: "अगले 5 दिनों का मौसम और बारिश का पूर्वानुमान क्या है?"
  },
  starter_4: {
    en: "Give details about PM-KISAN and PMFBY crop insurance schemes",
    hi: "PM-KISAN सम्मान निधि और फसल बीमा योजना (PMFBY) की जानकारी दो"
  }
};

// ==========================================
// Bilingual i18n Dictionaries
// ==========================================
const I18N = {
  en: {
    app_title: "KrishiSaathi AI (कृषि साथी) — Agricultural Advisory",
    new_chat: "New chat",
    search_chats: "Search chats",
    students: "Students",
    images: "Images",
    videos: "Videos",
    library: "Library",
    notebooks: "Notebooks",
    new_notebook: "New notebook",
    recent: "Recent",
    hero_headline: "Welcome Farmer Friend! 🙏",
    hero_subtext: "I am your AI KrishiSaathi assistant. Ask any question about your crops, fertilizer, pests, weather or government schemes via text, voice, or leaf photos.",
    starter_1_title: "Wheat Fertilizer Schedule",
    starter_2_title: "Leaf Disease Diagnosis",
    starter_3_title: "Weather & Rain Forecast",
    starter_4_title: "PM-KISAN & PMFBY Schemes",
    chat_placeholder: "Ask KrishiSaathi...",
    footer_disclaimer: "KrishiSaathi displays ICAR scientific guidelines. Check local agro-weather before chemical application.",
    listen_btn: "🔊 Listen",
    stop_audio_btn: "⏹️ Stop",
    copy_btn: "📋 Copy",
    confidence: "Confidence",
    foliar_damage: "Foliar Damage",
    citations_title: "📚 Verified Scientific Grounding (ICAR / KVK / CIBRC):",
    confirm_delete: "Delete this chat conversation?",
    empty_history: "No previous conversations."
  },
  hi: {
    app_title: "कृषि साथी (KrishiSaathi) — बहुआयामी AI कृषि सलाहकार",
    new_chat: "नया संवाद",
    search_chats: "संवाद खोजें",
    students: "कृषि छात्र (Students)",
    images: "फोटो गैलरी",
    videos: "सलाह वीडियो",
    library: "ज्ञानकोश (Library)",
    notebooks: "नोटबुक्स",
    new_notebook: "नई नोटबुक",
    recent: "हालिया संवाद",
    hero_headline: "Welcome Farmer Friend! 🙏",
    hero_subtext: "मैं आपका AI कृषि साथी सहायक हूँ। अपनी फसल, खाद, कीट-रोग, मौसम या सरकारी योजनाओं के बारे में लिखकर, बोलकर या पत्ती की फोटो भेजकर पूछें।",
    starter_1_title: "गेहूं में खाद का शेड्यूल",
    starter_2_title: "पत्ती रोग निदान (YOLO)",
    starter_3_title: "मौसम व बारिश अलर्ट",
    starter_4_title: "पीएम किसान व फसल बीमा",
    chat_placeholder: "कृषि साथी से पूछें...",
    footer_disclaimer: "कृषि साथी भारतीय कृषि अनुसंधान परिषद (ICAR) संस्तुतियों पर आधारित है। रासायनिक छिड़काव से पूर्व मौसम अनुकूलता जांचें।",
    listen_btn: "🔊 सुनो",
    stop_audio_btn: "⏹️ रोकें",
    copy_btn: "📋 कॉपी",
    confidence: "विश्वास स्कोर",
    foliar_damage: "संक्रमण",
    citations_title: "📚 प्रामाणिक कृषि संदर्भ (ICAR / KVK / CIBRC):",
    confirm_delete: "क्या आप इस संवाद को हटाना चाहते हैं?",
    empty_history: "कोई पुराना संवाद नहीं मिला।"
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
// DOM Initialization
// ==========================================
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initLanguageSwitcher();
  initSidebar();
  initPlusMenu();
  initChatInput();
  initVoice();
  initModals();
  initGeolocationAndWeather();
  loadFarmerProfile();
  loadSessions();
  loadNotebooks();
  loadCurrentSessionHistory();
});

// ==========================================
// Dynamic Theme Provider (OS Preference + Manual Override)
// ==========================================
function initTheme() {
  const toggleBtn = document.getElementById("theme-toggle-btn");
  const icon = document.getElementById("theme-toggle-icon");
  const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");

  function applyTheme(themeName) {
    document.body.classList.remove("light-theme", "dark-theme");
    document.body.classList.add(`${themeName}-theme`);
    if (icon) {
      icon.innerText = themeName === "dark" ? "🌙" : "☀️";
    }
  }

  const savedTheme = localStorage.getItem("ks_theme");
  if (savedTheme === "light" || savedTheme === "dark") {
    applyTheme(savedTheme);
  } else {
    // Automatically respect system / OS preference
    applyTheme(mediaQuery.matches ? "dark" : "light");
  }

  // Listen for live device / OS preference changes
  mediaQuery.addEventListener("change", (e) => {
    if (!localStorage.getItem("ks_theme")) {
      applyTheme(e.matches ? "dark" : "light");
    }
  });

  if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
      const isCurrentlyDark = document.body.classList.contains("dark-theme") ||
        (!document.body.classList.contains("light-theme") && mediaQuery.matches);
      const newTheme = isCurrentlyDark ? "light" : "dark";
      localStorage.setItem("ks_theme", newTheme);
      applyTheme(newTheme);
    });
  }
}

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
}

function applyLanguage(lang) {
  const dict = I18N[lang] || I18N.en;

  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (dict[key]) {
      el.innerText = dict[key];
    }
  });

  const textarea = document.getElementById("chat-textarea");
  if (textarea) textarea.placeholder = dict.chat_placeholder;

  const headline = document.getElementById("hero-headline");
  if (headline) headline.innerText = dict.hero_headline;

  const subtext = document.getElementById("hero-subtext");
  if (subtext) subtext.innerText = dict.hero_subtext;
}

// ==========================================
// Sidebar & Mode Pill Controls
// ==========================================
function initSidebar() {
  const sidebar = document.getElementById("sidebar");
  const toggleBtn = document.getElementById("sidebar-toggle-btn");
  const mobileMenuBtn = document.getElementById("mobile-menu-btn");
  const backdrop = document.getElementById("gemini-backdrop");
  const newChatBtn = document.getElementById("new-chat-btn");

  function toggleSidebar() {
    if (window.innerWidth <= 768) {
      const isOpen = sidebar.classList.contains("open");
      sidebar.classList.toggle("open", !isOpen);
      if (backdrop) backdrop.classList.toggle("active", !isOpen);
    } else {
      sidebar.classList.toggle("collapsed");
    }
  }

  function closeSidebar() {
    sidebar.classList.remove("open");
    if (backdrop) backdrop.classList.remove("active");
  }

  if (toggleBtn) toggleBtn.addEventListener("click", toggleSidebar);
  if (mobileMenuBtn) mobileMenuBtn.addEventListener("click", toggleSidebar);
  if (backdrop) backdrop.addEventListener("click", closeSidebar);

  if (newChatBtn) {
    newChatBtn.addEventListener("click", () => {
      startNewChat();
      if (window.innerWidth <= 768) closeSidebar();
    });
  }
}

// ==========================================
// Expandable Plus Menu (Matching Screenshot 2)
// ==========================================
function initPlusMenu() {
  const plusBtn = document.getElementById("plus-toggle-btn");
  const plusMenu = document.getElementById("gemini-plus-menu");
  const plusSymbol = document.getElementById("plus-icon-symbol");

  if (!plusBtn || !plusMenu) return;

  plusBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    const isActive = plusMenu.classList.contains("active");
    if (isActive) {
      closePlusMenu();
    } else {
      plusMenu.classList.add("active");
      plusBtn.classList.add("active");
      if (plusSymbol) plusSymbol.innerText = "✕";
    }
  });

  // Close popup menu when clicking outside
  document.addEventListener("click", (e) => {
    if (plusMenu.classList.contains("active")) {
      if (!plusMenu.contains(e.target) && !plusBtn.contains(e.target)) {
        closePlusMenu();
      }
    }
  });
}

function closePlusMenu() {
  const plusBtn = document.getElementById("plus-toggle-btn");
  const plusMenu = document.getElementById("gemini-plus-menu");
  const plusSymbol = document.getElementById("plus-icon-symbol");

  if (plusMenu) plusMenu.classList.remove("active");
  if (plusBtn) plusBtn.classList.remove("active");
  if (plusSymbol) plusSymbol.innerText = "＋";

  const sub = document.getElementById("more-tools-submenu");
  if (sub) sub.style.display = "none";
}

window.closePlusMenu = closePlusMenu;

window.triggerFileUpload = function() {
  closePlusMenu();
  const fileInput = document.getElementById("chat-photo-input");
  if (fileInput) fileInput.click();
};

window.openDrivePicker = function() {
  closePlusMenu();
  const promptVal = prompt(
    currentLang === "hi" 
      ? "Google Drive से मृदा रिपोर्ट या फसल दस्तावेज़ लिंक दर्ज करें:" 
      : "Enter Google Drive URL or document link for soil/crop report:"
  );
  if (promptVal) {
    const textarea = document.getElementById("chat-textarea");
    if (textarea) {
      textarea.value = (textarea.value ? textarea.value + " " : "") + "[Drive File: " + promptVal.trim() + "]";
      adjustTextareaHeight(textarea);
    }
  }
};

window.openMoreUploads = function() {
  closePlusMenu();
  triggerFileUpload();
};

window.triggerCreateImage = function() {
  closePlusMenu();
  const textarea = document.getElementById("chat-textarea");
  if (textarea) {
    textarea.value = currentLang === "hi" 
      ? "स्वस्थ व रोग-मुक्त गेहूं की बाली का विस्तृत वैज्ञानिक दृश्य तैयार करें।" 
      : "Create an illustrative scientific diagram of healthy wheat grain head and root system.";
    adjustTextareaHeight(textarea);
    handleSendMessage();
  }
};

window.triggerCreateVideo = function() {
  closePlusMenu();
  openCategoryView("videos");
};

window.triggerCreateMusic = function() {
  closePlusMenu();
  const textarea = document.getElementById("chat-textarea");
  if (textarea) {
    textarea.value = currentLang === "hi" 
      ? "मौसम और मानसूनी कृषि पर एक पारंपरिक किसान गीत और परामर्श सुनाएं।" 
      : "Generate a traditional agrarian folk rhyme and seasonal weather forecast advisory.";
    adjustTextareaHeight(textarea);
    handleSendMessage();
  }
};

window.toggleMoreToolsSubmenu = function() {
  const sub = document.getElementById("more-tools-submenu");
  if (sub) {
    sub.style.display = sub.style.display === "none" ? "flex" : "none";
  }
};

// ==========================================
// Search Chats Modal
// ==========================================
window.openSearchModal = function() {
  openModal("modal-search");
  const input = document.getElementById("search-chats-input");
  if (input) {
    input.value = "";
    input.focus();
    filterSessionsList("");
  }
};

window.filterSessionsList = async function(query) {
  const container = document.getElementById("search-results-list");
  if (!container) return;

  try {
    const res = await fetch("/api/chat/sessions");
    const data = await res.json();

    if (data.success && data.sessions) {
      const filtered = data.sessions.filter((s) => {
        const text = (s.preview || s.session_id).toLowerCase();
        return text.includes(query.toLowerCase());
      });

      if (filtered.length === 0) {
        container.innerHTML = `<div style="color:#8e918f; font-size:0.88rem; padding:12px 0;">No matching conversations found.</div>`;
        return;
      }

      container.innerHTML = filtered.map((s) => `
        <div class="session-item" style="padding:10px 12px; margin-bottom:4px; border-radius:8px; background:#191a1b;" onclick="switchSession('${escapeJsString(s.session_id)}'); closeModal('modal-search');">
          <span>💬 ${escapeHtml(s.preview || s.session_id)}</span>
        </div>
      `).join("");
    }
  } catch (err) {
    container.innerHTML = `<div style="color:red;">Error loading sessions.</div>`;
  }
};

// ==========================================
// Notebooks Feature (Screenshot 1)
// ==========================================
function loadNotebooks() {
  const container = document.getElementById("notebooks-list");
  if (!container) return;

  if (customNotebooks.length === 0) {
    customNotebooks = [
      { id: "nb_wheat_2026", title: "Rabi 2026 Wheat Plan" },
      { id: "nb_soil_kh", title: "Bakshi Ka Talab Soil Log" }
    ];
    localStorage.setItem("ks_custom_notebooks", JSON.stringify(customNotebooks));
  }

  container.innerHTML = customNotebooks.map((nb) => `
    <div class="notebook-item" onclick="triggerStarterPrompt('Summarize crop notes for ${escapeJsString(nb.title)}')">
      <span class="session-title">📓 ${escapeHtml(nb.title)}</span>
    </div>
  `).join("");
}

window.openNewNotebookModal = function() {
  openModal("modal-notebook");
  const input = document.getElementById("notebook-name-input");
  if (input) {
    input.value = "";
    input.focus();
  }
};

window.createNewNotebook = function() {
  const input = document.getElementById("notebook-name-input");
  const title = (input ? input.value : "").trim();
  if (!title) return;

  const newNb = {
    id: "nb_" + Date.now(),
    title: title
  };

  customNotebooks.push(newNb);
  localStorage.setItem("ks_custom_notebooks", JSON.stringify(customNotebooks));
  loadNotebooks();
  closeModal("modal-notebook");
};

// ==========================================
// Categories Modal (Students / Images / Videos / Library)
// ==========================================
window.openCategoryView = function(categoryKey) {
  const modal = document.getElementById("modal-category");
  const title = document.getElementById("category-modal-title");
  const content = document.getElementById("category-modal-content");
  if (!modal || !title || !content) return;

  if (categoryKey === "students") {
    title.innerText = "🎓 Agronomy Student Learning Modules";
    content.innerHTML = `
      <div style="display:flex; flex-direction:column; gap:10px;">
        <div style="background:#282a2c; padding:12px; border-radius:8px;">
          <strong style="color:#4285f4;">Module 1: Soil Nitrogen Dynamics &amp; Urea Efficiency</strong>
          <p style="color:#c4c7c5; font-size:0.86rem; margin-top:4px;">Mechanisms of ammonification, nitrification inhibitors, and neem-coated urea applications.</p>
        </div>
        <div style="background:#282a2c; padding:12px; border-radius:8px;">
          <strong style="color:#4285f4;">Module 2: Foliar Phytopathology &amp; Fungal Diagnostic Keys</strong>
          <p style="color:#c4c7c5; font-size:0.86rem; margin-top:4px;">Differentiating Yellow Rust (Puccinia striiformis) from Leaf Blight (Bipolaris sorokiniana).</p>
        </div>
        <div style="background:#282a2c; padding:12px; border-radius:8px;">
          <strong style="color:#4285f4;">Module 3: ICAR Agro-Climatic Zoning of India</strong>
          <p style="color:#c4c7c5; font-size:0.86rem; margin-top:4px;">15 major agro-climatic zones and corresponding cropping patterns.</p>
        </div>
      </div>
    `;
  } else if (categoryKey === "images") {
    title.innerText = "🖼️ Plant Disease Visual Gallery (YOLO)";
    content.innerHTML = `
      <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(130px, 1fr)); gap:10px;">
        <div style="background:#282a2c; padding:8px; border-radius:8px; text-align:center;">
          <div style="font-size:2.5rem;">🍃</div>
          <strong style="font-size:0.84rem; color:#fff;">Tomato Early Blight</strong>
        </div>
        <div style="background:#282a2c; padding:8px; border-radius:8px; text-align:center;">
          <div style="font-size:2.5rem;">🌾</div>
          <strong style="font-size:0.84rem; color:#fff;">Wheat Stripe Rust</strong>
        </div>
        <div style="background:#282a2c; padding:8px; border-radius:8px; text-align:center;">
          <div style="font-size:2.5rem;">🥔</div>
          <strong style="font-size:0.84rem; color:#fff;">Potato Late Blight</strong>
        </div>
        <div style="background:#282a2c; padding:8px; border-radius:8px; text-align:center;">
          <div style="font-size:2.5rem;">🌱</div>
          <strong style="font-size:0.84rem; color:#fff;">Rice Blast</strong>
        </div>
      </div>
    `;
  } else if (categoryKey === "videos") {
    title.innerText = "🎬 Agricultural Video Tutorials (ICAR / KVK)";
    content.innerHTML = `
      <div style="display:flex; flex-direction:column; gap:10px;">
        <div style="background:#282a2c; padding:12px; border-radius:8px;">
          <strong style="color:#fbbc05;">▶ Scientific Wheat Sowing &amp; Seed Treatment Guide</strong>
          <p style="color:#8e918f; font-size:0.82rem; margin-top:2px;">KVK Lucknow • 12 mins • Hindi</p>
        </div>
        <div style="background:#282a2c; padding:12px; border-radius:8px;">
          <strong style="color:#fbbc05;">▶ Safe Spray Windows: Calibrating Knapsack Sprayers</strong>
          <p style="color:#8e918f; font-size:0.82rem; margin-top:2px;">ICAR-CIBRC Extension • 8 mins • Hindi &amp; English</p>
        </div>
      </div>
    `;
  } else {
    title.innerText = "📚 Agricultural Knowledge Library";
    content.innerHTML = `
      <div style="display:flex; flex-direction:column; gap:8px;">
        <div style="background:#282a2c; padding:10px; border-radius:8px;">📖 ICAR Crop Production Manual (Rabi Season)</div>
        <div style="background:#282a2c; padding:10px; border-radius:8px;">📖 CIBRC Registered Agro-Chemical Formulations Directory</div>
        <div style="background:#282a2c; padding:10px; border-radius:8px;">📖 Soil Health Card Assessment Guidelines (Govt of India)</div>
      </div>
    `;
  }

  openModal("modal-category");
};

// ==========================================
// Session Management
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
          <span class="session-title" title="${escapeHtml(titleText)}">💬 ${escapeHtml(titleText)}</span>
          <button class="session-delete-btn" title="Delete conversation" onclick="deleteSession('${escapeJsString(s.session_id)}', event)">✕</button>
        `;

        item.addEventListener("click", (e) => {
          if (e.target.closest(".session-delete-btn")) return;
          switchSession(s.session_id);
          const sidebar = document.getElementById("sidebar");
          const backdrop = document.getElementById("gemini-backdrop");
          if (window.innerWidth <= 768 && sidebar) {
            sidebar.classList.remove("open");
            if (backdrop) backdrop.classList.remove("active");
          }
        });

        container.appendChild(item);
      });
    } else {
      const dict = I18N[currentLang] || I18N.en;
      container.innerHTML = `<div style="font-size:0.8rem; color:#8e918f; padding: 10px 12px;">${dict.empty_history}</div>`;
    }
  } catch (err) {
    console.error("Error loading chat sessions:", err);
  }
}

function startNewChat() {
  currentSessionId = "session_" + Date.now().toString(36) + Math.random().toString(36).substring(2, 6);
  localStorage.setItem("ks_current_session", currentSessionId);

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

  document.querySelectorAll(".session-item").forEach((el) => {
    el.classList.toggle("active", el.dataset.sessionId === sessionId);
  });

  await loadCurrentSessionHistory();
}

async function deleteSession(sessionId, event) {
  if (event) event.stopPropagation();
  const dict = I18N[currentLang] || I18N.en;
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
        if (turn.user_query) {
          appendUserMessage(turn.user_query, null, false);
        }
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
// Starter Prompts Trigger
// ==========================================
window.triggerStarterPrompt = function(promptKeyOrText) {
  let promptText = promptKeyOrText;
  if (STARTER_PROMPTS[promptKeyOrText]) {
    promptText = STARTER_PROMPTS[promptKeyOrText][currentLang] || STARTER_PROMPTS[promptKeyOrText].en;
  }

  const textarea = document.getElementById("chat-textarea");
  if (textarea) {
    textarea.value = promptText;
    adjustTextareaHeight(textarea);
    handleSendMessage();
  }
};

// ==========================================
// Chat Input, Attachments & Voice
// ==========================================
function initChatInput() {
  const textarea = document.getElementById("chat-textarea");
  const sendBtn = document.getElementById("chat-send-btn");
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

  if (photoInput) {
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
  el.style.height = Math.min(el.scrollHeight, 140) + "px";
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

function initVoice() {
  const micBtn = document.getElementById("chat-mic-btn");
  const textarea = document.getElementById("chat-textarea");

  if (!recognition || !micBtn) {
    if (micBtn) {
      micBtn.title = "Voice recognition not supported";
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

  recognition.onerror = () => { micBtn.classList.remove("recording"); };
  recognition.onend = () => { micBtn.classList.remove("recording"); };
}

// ==========================================
// Text to Speech (TTS) & Copy
// ==========================================
window.speakText = function(text, btnElement) {
  if (!("speechSynthesis" in window)) {
    alert(currentLang === "hi" ? "ब्राउज़र में आवाज़ समर्थित नहीं है।" : "Speech playback not supported.");
    return;
  }

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
      btnElement.innerText = currentLang === "hi" ? "✓ कॉपीड!" : "✓ Copied!";
      btnElement.style.color = "#4285f4";
      setTimeout(() => {
        btnElement.innerText = originalText;
        btnElement.style.color = "";
      }, 2000);
    }
  } catch (err) {
    console.error("Failed to copy:", err);
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

  const userQuery = text || (currentLang === "hi" ? "कृपया इस पौधे की पत्ती की जांच करें।" : "Please analyze this crop leaf photo.");

  // Hide hero greeting
  const emptyHero = document.getElementById("empty-state-hero");
  if (emptyHero) emptyHero.style.display = "none";

  let previewUrl = null;
  if (sendingFile) {
    previewUrl = URL.createObjectURL(sendingFile);
  }

  // Append user bubble
  appendUserMessage(userQuery, previewUrl, true);

  // Clear inputs
  if (textarea) {
    textarea.value = "";
    adjustTextareaHeight(textarea);
  }
  clearAttachment();

  // Loading indicator
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
      loadSessions();
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
    imgTag = `<div style="margin-bottom:8px;"><img src="${photoUrl}" alt="Attachment" style="max-width:200px; max-height:140px; border-radius:10px; border:1px solid #4285f4;"></div>`;
  }

  msgDiv.innerHTML = `
    <div class="user-bubble">
      ${imgTag}
      <div>${escapeHtml(text)}</div>
    </div>
  `;

  stream.appendChild(msgDiv);
  if (scroll) scrollToBottom();
}

function appendLoadingBubble(id) {
  const stream = document.getElementById("messages-stream");
  if (!stream) return;

  const loadDiv = document.createElement("div");
  loadDiv.className = "message-row assistant-row";
  loadDiv.id = id;

  loadDiv.innerHTML = `
    <div class="assistant-avatar-emblem">
      <svg viewBox="0 0 32 32" width="24" height="24">
        <circle cx="16" cy="16" r="15" fill="#e8f9f0" stroke="#86efac" stroke-width="1.2" />
        <path d="M12 23 C12 17 10 13 8 11" stroke="#10b981" stroke-width="2" stroke-linecap="round" fill="none" />
        <path d="M15 24 V9" stroke="#059669" stroke-width="2.2" stroke-linecap="round" />
        <path d="M18 24 C18 18 20 14 23 12" stroke="#047857" stroke-width="2" stroke-linecap="round" fill="none" />
        <path d="M15 10 H8 M15 14 H9 M15 18 H9" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" />
        <path d="M15 8 H21 M15 12 H22 M15 16 H21" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" />
      </svg>
    </div>
    <div class="assistant-card">
      <div style="color:#8e918f; font-style:italic;">
        <span style="color:#10b981;">● ● ●</span> KrishiSaathi is analyzing agricultural guidelines...
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

  const dict = I18N[currentLang] || I18N.en;
  const msgDiv = document.createElement("div");
  msgDiv.className = "message-row assistant-row";

  // YOLO Vision Diagnostic Badge
  let visionHtml = "";
  if (data.vision && data.vision.success) {
    const v = data.vision;
    const diseaseName = currentLang === "hi" ? v.disease_name_hindi : v.disease_name_en;
    const cropName = currentLang === "hi" ? v.crop : v.crop_en;
    visionHtml = `
      <div class="vision-diagnostic-card">
        <div class="vision-header">
          <span style="font-size:1.2rem;">🍃</span>
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

  // Action Buttons
  const escapedResp = escapeJsString(data.response || '');
  const actionsHtml = `
    <div class="card-footer-actions">
      <button class="action-btn" onclick="copyMessageText(\`${escapedResp}\`, this)">
        ${dict.copy_btn}
      </button>
      <button class="action-btn" onclick="speakText(\`${escapedResp}\`, this)">
        ${dict.listen_btn}
      </button>
    </div>
  `;

  msgDiv.innerHTML = `
    <div class="assistant-avatar-emblem">
      <svg viewBox="0 0 32 32" width="24" height="24">
        <circle cx="16" cy="16" r="15" fill="#e8f9f0" stroke="#86efac" stroke-width="1.2" />
        <path d="M12 23 C12 17 10 13 8 11" stroke="#10b981" stroke-width="2" stroke-linecap="round" fill="none" />
        <path d="M15 24 V9" stroke="#059669" stroke-width="2.2" stroke-linecap="round" />
        <path d="M18 24 C18 18 20 14 23 12" stroke="#047857" stroke-width="2" stroke-linecap="round" fill="none" />
        <path d="M15 10 H8 M15 14 H9 M15 18 H9" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" />
        <path d="M15 8 H21 M15 12 H22 M15 16 H21" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" />
      </svg>
    </div>
    <div class="assistant-card">
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
 * Structured Markdown Parser
 */
function renderMarkdown(text) {
  if (!text) return "";

  const lines = text.split("\n");
  const result = [];
  let inUl = false;
  let inOl = false;

  function closeLists() {
    if (inUl) { result.push("</ul>"); inUl = false; }
    if (inOl) { result.push("</ol>"); inOl = false; }
  }

  for (let i = 0; i < lines.length; i++) {
    const rawLine = lines[i];
    const trimmed = rawLine.trim();

    if (!trimmed) {
      closeLists();
      continue;
    }

    const ulMatch = trimmed.match(/^[\*\-\•]\s+(.*)$/);
    if (ulMatch) {
      if (inOl) { result.push("</ol>"); inOl = false; }
      if (!inUl) { result.push("<ul>"); inUl = true; }
      result.push(`<li>${formatInline(ulMatch[1])}</li>`);
      continue;
    }

    const olMatch = trimmed.match(/^\d+\.\s+(.*)$/);
    if (olMatch) {
      if (inUl) { result.push("</ul>"); inUl = false; }
      if (!inOl) { result.push("<ol>"); inOl = true; }
      result.push(`<li>${formatInline(olMatch[1])}</li>`);
      continue;
    }

    closeLists();

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
  s = s.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  s = s.replace(/\*([^\*\s][^\*]*?)\*/g, "<em>$1</em>");
  s = s.replace(/_([^_\s][^_]*?)_/g, "<em>$1</em>");
  s = s.replace(/`([^`]+)`/g, "<code>$1</code>");
  return s;
}

// ==========================================
// Modal System
// ==========================================
window.openModal = function(modalId) {
  const modal = document.getElementById(modalId);
  if (!modal) return;
  modal.classList.add("active");

  if (modalId === "modal-weather") {
    searchWeatherModal();
  } else if (modalId === "modal-schemes") {
    searchSchemesModal();
  }
};

window.closeModal = function(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.remove("active");
};

function initModals() {
  document.querySelectorAll(".modal-overlay").forEach((overlay) => {
    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) {
        overlay.classList.remove("active");
      }
    });
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      document.querySelectorAll(".modal-overlay.active").forEach((m) => {
        m.classList.remove("active");
      });
      closePlusMenu();
    }
  });

  setupDiseaseModal();
  setupSoilModal();
  setupCropModal();
  setupProfileModal();
}

// ==========================================
// Geolocation & Live Weather Display
// ==========================================
function getWeatherEmoji(cond) {
  const c = (cond || "").toLowerCase();
  if (c.includes("rain") || c.includes("shower") || c.includes("drizzle")) return "🌧️";
  if (c.includes("cloud") || c.includes("overcast")) return "⛅";
  if (c.includes("thunder") || c.includes("storm")) return "⛈️";
  if (c.includes("snow")) return "❄️";
  if (c.includes("fog") || c.includes("mist") || c.includes("haze")) return "🌫️";
  return "☀️";
}

function updateWeatherBadge(cityOrDist, stateCode, temp, cond) {
  const topText = document.getElementById("top-weather-text");
  if (!topText) return;
  const loc = stateCode ? `${cityOrDist}, ${stateCode}` : cityOrDist;
  const tempStr = temp !== undefined && temp !== null ? `${Math.round(temp)}°C` : "28°C";
  const condEmoji = cond ? getWeatherEmoji(cond) : "☀️";
  topText.innerHTML = `${loc} • ${tempStr} ${condEmoji}`;
}

async function initGeolocationAndWeather() {
  async function loadFallback() {
    try {
      const res = await fetch("/api/weather?district=Kanpur");
      const data = await res.json();
      if (data && data.success && data.current) {
        liveWeatherCache = data;
        updateWeatherBadge("Kanpur", "UP", data.current.temperature, data.current.condition);
      } else {
        updateWeatherBadge("Kanpur", "UP", 28, "Clear");
      }
    } catch {
      updateWeatherBadge("Kanpur", "UP", 28, "Clear");
    }
  }

  if (!("geolocation" in navigator)) {
    loadFallback();
    return;
  }

  navigator.geolocation.getCurrentPosition(
    async (pos) => {
      try {
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;
        let city = "Kanpur";
        let stateCode = "UP";

        try {
          const geoRes = await fetch(`https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${lat}&longitude=${lon}&localityLanguage=en`);
          if (geoRes.ok) {
            const geoData = await geoRes.json();
            city = geoData.city || geoData.locality || geoData.principalSubdivision || "Kanpur";
            const rawState = geoData.principalSubdivisionCode || geoData.principalSubdivision || "";
            stateCode = rawState.replace(/^IN-/, "").substring(0, 4).toUpperCase() || "UP";
          }
        } catch (geoErr) {
          console.warn("Reverse geocode fallback to backend coords:", geoErr);
        }

        const res = await fetch(`/api/weather?district=${encodeURIComponent(city)}&lat=${lat}&lon=${lon}`);
        const data = await res.json();
        if (data && data.success && data.current) {
          liveWeatherCache = data;
          updateWeatherBadge(city, stateCode, data.current.temperature, data.current.condition);
        } else {
          updateWeatherBadge(city, stateCode, 28, "Clear");
        }
      } catch (err) {
        console.warn("Geolocation weather error:", err);
        loadFallback();
      }
    },
    (err) => {
      console.log("Geolocation permission not granted / fallback used:", err.message);
      loadFallback();
    },
    { timeout: 8000, enableHighAccuracy: false, maximumAge: 300000 }
  );
}

window.searchWeatherModal = async function() {
  const input = document.getElementById("modal-weather-district");
  const content = document.getElementById("modal-weather-content");
  const district = (input && input.value.trim()) || "Lucknow";

  if (!content) return;
  content.innerHTML = `<div style="text-align:center; padding: 24px; color: #4285f4;">🌦️ Fetching meteorological forecast...</div>`;

  try {
    const res = await fetch(`/api/weather?district=${encodeURIComponent(district)}`);
    const data = await res.json();

    if (data.success) {
      liveWeatherCache = data;
      const curr = data.current;
      updateWeatherBadge(data.location, "", curr.temperature, curr.condition);

      let advisoriesHtml = "";
      if (data.agricultural_advisories && data.agricultural_advisories.length > 0) {
        advisoriesHtml = data.agricultural_advisories.map((a) => `
          <div style="background:#282a2c; border-left:4px solid #4285f4; padding:12px; border-radius:8px; margin-bottom:10px;">
            <strong style="color:#93c5fd; font-size:0.95rem;">${a.title}</strong><br>
            <span style="font-size:0.88rem; color:#e3e3e3; line-height:1.5;">${a.advice}</span>
          </div>
        `).join("");
      }

      let forecastHtml = "";
      if (data.forecast) {
        forecastHtml = `
          <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(110px, 1fr)); gap:10px; margin-top:10px;">
            ${data.forecast.map((f) => `
              <div style="background:#282a2c; border:1px solid #3c4043; border-radius:10px; padding:10px 8px; text-align:center;">
                <div style="font-size:0.78rem; color:#8e918f;">${f.date}</div>
                <div style="font-weight:700; color:#4285f4; font-size:1.1rem; margin:4px 0;">${f.temp_max}° / ${f.temp_min}°</div>
                <div style="font-size:0.75rem; color:#38bdf8;">🌧️ ${f.rain_prob}%</div>
                <div style="font-size:0.74rem; color:#c4c7c5; margin-top:2px;">${f.condition}</div>
              </div>
            `).join("")}
          </div>
        `;
      }

      content.innerHTML = `
        <div style="background:#282a2c; border-radius:12px; padding:16px; display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; border:1px solid #3c4043;">
          <div>
            <h3 style="color:#ffffff; margin-bottom:4px; font-size:1.25rem;">${data.location}</h3>
            <span style="font-size:0.82rem; color:#8e918f;">Source: ${data.source}</span>
          </div>
          <div style="text-align:right;">
            <div style="font-size:2rem; font-weight:700; color:#4285f4;">${curr.temperature}°C</div>
            <div style="font-size:0.82rem; color:#c4c7c5;">Humidity: ${curr.humidity}% | Wind: ${curr.wind_speed} km/h</div>
          </div>
        </div>
        <h4 style="color:#ffffff; margin-bottom:10px;">🌾 Agricultural Weather Advisories</h4>
        ${advisoriesHtml}
        <h4 style="color:#ffffff; margin-top:16px; margin-bottom:10px;">📅 5-Day Forecast</h4>
        ${forecastHtml}
      `;
    } else {
      content.innerHTML = `<div style="color:#f87171; padding:12px;">${data.error || "Unable to load weather."}</div>`;
    }
  } catch (err) {
    content.innerHTML = `<div style="color:#f87171; padding:12px;">Error fetching weather data.</div>`;
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
    dropzone.style.borderColor = "#4285f4";
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.style.borderColor = "#3c4043";
  });

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.style.borderColor = "#3c4043";
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
  resultArea.innerHTML = `<div style="text-align:center; padding:20px; color:#4285f4;">📸 YOLO Vision model is analyzing leaf symptoms...</div>`;

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
      const dName = isEn ? data.disease_name_en : data.disease_name_hindi;
      const cName = isEn ? data.crop_en : data.crop;
      const symptoms = isEn ? data.symptoms_en : data.symptoms;
      const action = isEn ? data.immediate_cultural_action_en : data.immediate_cultural_action;
      const organic = isEn ? data.organic_ipm_remedy_en : data.organic_ipm_remedy;
      const chem = isEn ? data.chemical_solution_en : data.chemical_solution;
      const sprayAdv = isEn ? data.weather_spray_advisory_en : data.weather_spray_advisory;
      const kvkNote = isEn ? data.kvk_escalation_note_en : data.kvk_escalation_note;

      resultArea.innerHTML = `
        <div style="background:#282a2c; border:1px solid #3c4043; border-radius:12px; padding:16px;">
          <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #3c4043; padding-bottom:8px; margin-bottom:12px;">
            <div>
              <h3 style="color:#ffffff; margin-bottom:2px; font-size:1.1rem;">${escapeHtml(dName)}</h3>
              <span style="font-size:0.84rem; color:#8e918f;">Crop: <strong style="color:#4285f4;">${escapeHtml(cName)}</strong></span>
            </div>
            <span style="background:#1e3a8a; color:#93c5fd; padding:3px 8px; border-radius:12px; font-size:0.78rem; font-weight:600;">
              ${data.confidence_score}% Confidence
            </span>
          </div>

          <p style="margin-bottom:8px; font-size:0.9rem;"><strong>🔍 Symptoms:</strong> ${escapeHtml(symptoms)}</p>
          <p style="margin-bottom:8px; font-size:0.9rem;"><strong>⚡ Immediate Action:</strong> ${escapeHtml(action)}</p>
          <p style="margin-bottom:10px; font-size:0.9rem;"><strong>🌿 Organic &amp; IPM:</strong> ${escapeHtml(organic)}</p>

          <div style="background:#332a00; border-left:4px solid #fbbc05; padding:10px 12px; border-radius:6px; margin:10px 0; font-size:0.88rem; color:#fef08a;">
            <strong>🧪 Safe Chemical Spray:</strong><br>
            • ${chem.name} | Dose: ${chem.dose}<br>
            • Precaution: ${chem.precaution}
          </div>

          <div style="background:#082f49; padding:8px 12px; border-radius:6px; font-size:0.84rem; color:#7dd3fc; margin-bottom:10px;">
            🌦️ ${sprayAdv}
          </div>

          <div style="font-size:0.82rem; color:#f87171; border-top:1px dashed #3c4043; padding-top:8px;">
            📞 ${kvkNote}
          </div>

          <div style="margin-top:14px; display:flex; justify-content:flex-end; gap:8px;">
            <button class="gemini-btn-primary" style="padding:6px 14px; font-size:0.84rem;" onclick="closeModal('modal-disease'); triggerStarterPrompt('${escapeJsString('Tell me more about treating ' + dName + ' in ' + cName)}')">
              💬 Ask KrishiSaathi About This
            </button>
          </div>
        </div>
      `;
    } else {
      resultArea.innerHTML = `<div style="background:#450a0a; color:#fca5a5; padding:12px; border-radius:8px;">${data.rejection_reason || data.error || "Analysis failed."}</div>`;
    }
  } catch (err) {
    resultArea.innerHTML = `<div style="color:#f87171; padding:12px;">Error during disease analysis.</div>`;
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
    resultArea.innerHTML = `<div style="text-align:center; padding:18px; color:#4285f4;">🧪 Analyzing Soil Parameters...</div>`;

    const payload = {
      ph: parseFloat(document.getElementById("modal-soil-ph").value),
      oc: parseFloat(document.getElementById("modal-soil-oc").value),
      n: parseFloat(document.getElementById("modal-soil-n").value),
      p: parseFloat(document.getElementById("modal-soil-p").value),
      k: parseFloat(document.getElementById("modal-soil-k").value),
      ec: parseFloat(document.getElementById("modal-soil-ec").value),
      zn: parseFloat(document.getElementById("modal-soil-zn").value),
      s: parseFloat(document.getElementById("modal-soil-s").value),
      fe: parseFloat(document.getElementById("modal-soil-fe").value || 5.0),
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
        const defs = data.deficiencies_en || data.deficiencies;
        const summary = data.english_summary || data.hindi_summary;

        const defHtml = (defs && defs.length > 0)
          ? defs.map((d) => `<li>${escapeHtml(d)}</li>`).join("")
          : `<li>No critical deficiencies detected.</li>`;

        const amendHtml = (data.amendments && data.amendments.length > 0)
          ? data.amendments.map((a) => `
              <li><strong>${escapeHtml(a.action_en || a.action)}:</strong> ${escapeHtml(a.dose_en || a.dose)}</li>
            `).join("")
          : `<li>Maintain regular organic compost.</li>`;

        resultArea.innerHTML = `
          <div style="background:#282a2c; border:1px solid #3c4043; border-radius:12px; padding:16px;">
            <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #3c4043; padding-bottom:8px; margin-bottom:10px;">
              <h3 style="color:#ffffff;">Soil Health Score: ${data.health_score}/100</h3>
              <span style="background:#064e3b; color:#a7f3d0; padding:3px 8px; border-radius:12px; font-size:0.8rem;">${data.soil_classification.name_hindi}</span>
            </div>
            <p style="margin-bottom:10px; font-size:0.92rem;">${escapeHtml(summary)}</p>
            
            <h4 style="color:#f87171; margin:10px 0 4px 0;">⚠️ Nutrient Deficiencies:</h4>
            <ul style="padding-left:20px; font-size:0.88rem; margin-bottom:10px;">${defHtml}</ul>

            <h4 style="color:#4285f4; margin:10px 0 4px 0;">🌾 Recommended Amendments:</h4>
            <ul style="padding-left:20px; font-size:0.88rem; margin-bottom:10px;">${amendHtml}</ul>
          </div>
        `;
      }
    } catch (err) {
      resultArea.innerHTML = `<div style="color:#f87171; padding:12px;">Error analyzing soil parameters.</div>`;
    }
  });
}

// ==========================================
// Crop ML Modal
// ==========================================
function setupCropModal() {
  const form = document.getElementById("modal-crop-form");
  const resultArea = document.getElementById("modal-crop-result");

  if (!form || !resultArea) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    resultArea.innerHTML = `<div style="text-align:center; padding:18px; color:#4285f4;">🌱 Calculating optimal crops with ML Engine...</div>`;

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
        const cardsHtml = data.top_recommendations.map((c, idx) => `
          <div style="background:#1e1f20; border:1px solid #3c4043; border-radius:10px; padding:12px; margin-bottom:10px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <strong style="color:#4285f4; font-size:1.05rem;">#${idx+1} ${c.crop_key.toUpperCase()} (${c.hindi_name})</strong>
              <span style="background:#1e3a8a; color:#93c5fd; padding:2px 8px; border-radius:10px; font-size:0.75rem;">${c.suitability_score}% Suitability</span>
            </div>
            <p style="font-size:0.86rem; color:#c4c7c5; margin:6px 0;">${escapeHtml(c.description)}</p>
            <div style="font-size:0.8rem; color:#8e918f; display:flex; gap:12px; flex-wrap:wrap;">
              <span>📅 Sowing: <strong>${c.sowing_months}</strong></span>
              <span>💧 Water: <strong>${c.water_need}</strong></span>
              <span>🍂 Season: <strong>${c.season}</strong></span>
            </div>
          </div>
        `).join("");

        resultArea.innerHTML = `
          <div style="background:#282a2c; border:1px solid #3c4043; border-radius:12px; padding:16px;">
            <h4 style="color:#ffffff; margin-bottom:10px;">🌟 Top Recommended Crops (${data.current_season}):</h4>
            ${cardsHtml}
          </div>
        `;
      }
    } catch (err) {
      resultArea.innerHTML = `<div style="color:#f87171; padding:12px;">Error calculating crop recommendations.</div>`;
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
  content.innerHTML = `<div style="text-align:center; padding:18px; color:#4285f4;">🏛️ Searching agricultural schemes...</div>`;

  try {
    const res = await fetch(`/api/schemes?q=${encodeURIComponent(q)}`);
    const data = await res.json();

    if (data.schemes && data.schemes.length > 0) {
      content.innerHTML = data.schemes.map((s) => `
        <div style="background:#282a2c; border:1px solid #3c4043; border-radius:12px; padding:14px; margin-bottom:12px;">
          <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #3c4043; padding-bottom:6px; margin-bottom:8px;">
            <h3 style="color:#ffffff; font-size:1.05rem;">🏛️ ${escapeHtml(s.name)}</h3>
            <span style="font-size:0.75rem; background:#064e3b; color:#a7f3d0; padding:2px 8px; border-radius:10px;">${escapeHtml(s.ministry)}</span>
          </div>
          <p style="font-size:0.88rem; color:#c4c7c5; margin-bottom:8px;">${escapeHtml(s.objective)}</p>
          <div style="background:#1e1f20; padding:8px 10px; border-radius:6px; font-size:0.82rem; line-height:1.5;">
            <strong>🎯 Eligibility:</strong> ${escapeHtml(s.eligibility)}<br>
            <strong>💰 Benefits:</strong> ${escapeHtml(s.benefits)}<br>
            <strong>📝 How to Apply:</strong> ${escapeHtml(s.how_to_apply)}<br>
            <strong>📞 Helpline:</strong> <span style="color:#f87171; font-weight:700;">${escapeHtml(s.helpline)}</span>
          </div>
        </div>
      `).join("");
    } else {
      content.innerHTML = `<div style="text-align:center; color:#8e918f; padding:18px;">No schemes found matching query.</div>`;
    }
  } catch (err) {
    content.innerHTML = `<div style="color:#f87171; padding:12px;">Error searching schemes.</div>`;
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
      document.getElementById("profile-name").value = data.name || "Prakhyat";
      document.getElementById("profile-village").value = data.village || "Bakshi Ka Talab";
      document.getElementById("profile-district").value = data.district || "Lucknow";
      document.getElementById("profile-state").value = data.state || "Uttar Pradesh";
      document.getElementById("profile-acres").value = data.farm_size_acres || 3.5;
      document.getElementById("profile-crop").value = data.current_crop || "Wheat (गेहूं)";
      document.getElementById("profile-soil").value = data.soil_type || "Alluvial Loam";
      const irrEl = document.getElementById("profile-irrigation");
      if (irrEl) irrEl.value = data.irrigation_type || "Tubewell";

      const nameEl = document.getElementById("sidebar-farmer-name");
      const metaEl = document.getElementById("sidebar-farmer-meta");
      if (nameEl) nameEl.innerText = data.name;
      if (metaEl) metaEl.innerText = `${data.district} • ${data.current_crop}`;
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
        status.innerHTML = `<div style="color:#4285f4; font-weight:600;">✓ Profile saved successfully!</div>`;
        setTimeout(() => { status.innerHTML = ""; }, 2500);
      }

      const nameEl = document.getElementById("sidebar-farmer-name");
      const metaEl = document.getElementById("sidebar-farmer-meta");
      if (nameEl) nameEl.innerText = payload.name;
      if (metaEl) metaEl.innerText = `${payload.district} • ${payload.current_crop}`;

      loadLiveWeather(payload.district);
    } catch (err) {
      if (status) status.innerHTML = `<div style="color:#f87171;">Failed to save profile.</div>`;
    }
  });
}

// ==========================================
// Utility Functions
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
