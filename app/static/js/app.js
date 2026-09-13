// KrishiSaathi Frontend Application Logic
let currentSessionId = "session_" + Math.random().toString(36).substring(2, 9);
let currentFarmerId = "default_farmer";
let liveWeatherCache = null;

// Speech Recognition & Synthesis
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
  initVoice();
  loadLiveWeather();
  loadFarmerProfile();
  setupChatHandlers();
  setupDiseaseUpload();
  setupSoilAnalyzer();
  setupCropRecommender();
  setupSchemesSearch();
});

// Tab Management
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

// Weather Loading
async function loadLiveWeather(district = "Lucknow") {
  try {
    const res = await fetch(`/api/weather?district=${encodeURIComponent(district)}`);
    const data = await res.json();
    if (data.success) {
      liveWeatherCache = data;
      const curr = data.current;
      document.getElementById("header-weather").innerHTML = `📍 ${data.location} | 🌡️ ${curr.temperature}°C | 💧 ${curr.humidity}% | ${curr.condition}`;
      
      // Update Weather Tab
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
                <div style="font-size: 0.8rem; color: #0288d1;">🌧️ ${f.rain_prob}% वर्षा</div>
                <div style="font-size: 0.75rem; margin-top: 4px;">${f.condition}</div>
              </div>
            `).join("") + `</div>`;
        }

        weatherTabBox.innerHTML = `
          <div style="display: flex; justify-content: space-between; align-items: center; background: #e8f5e9; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
            <div>
              <h3 style="color: #1b5e20;">${data.location}</h3>
              <p style="color: #388e3c; font-size: 0.9rem;">स्रोत: ${data.source}</p>
            </div>
            <div style="text-align: right;">
              <span style="font-size: 2rem; font-weight: 800; color: #2e7d32;">${curr.temperature}°C</span>
              <div style="font-size: 0.85rem; color: #555;">नमी: ${curr.humidity}% | हवा: ${curr.wind_speed} km/h</div>
            </div>
          </div>
          <h4 style="margin-bottom: 10px; color: #1b5e20;">🌾 कृषि मौसम परामर्श (Agri Advisories)</h4>
          ${advisoriesHtml}
          <h4 style="margin-top: 20px; margin-bottom: 8px; color: #1b5e20;">📅 आगामी 5 दिनों का पूर्वानुमान</h4>
          ${forecastHtml}
        `;
      }
    }
  } catch (err) {
    console.error("Error loading weather:", err);
  }
}

// Voice Recognition & Text-To-Speech
function initVoice() {
  const micBtn = document.getElementById("mic-btn");
  const chatInput = document.getElementById("chat-input");
  
  if (!recognition) {
    micBtn.title = "वॉइस इनपुट इस ब्राउज़र में समर्थित नहीं है";
    micBtn.style.opacity = "0.6";
    return;
  }

  micBtn.addEventListener("click", () => {
    if (micBtn.classList.contains("recording")) {
      recognition.stop();
      micBtn.classList.remove("recording");
    } else {
      micBtn.classList.add("recording");
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
    alert("आपके ब्राउज़र में आवाज़ (TTS) समर्थित नहीं है।");
    return;
  }
  window.speechSynthesis.cancel();
  // Strip markdown markers
  const clean = text.replace(/[*#•`_]/g, "").replace(/\n+/g, " ");
  const utterance = new SpeechSynthesisUtterance(clean);
  utterance.lang = "hi-IN";
  utterance.rate = 0.95;
  
  // Choose Hindi voice if available
  const voices = window.speechSynthesis.getVoices();
  const hiVoice = voices.find(v => v.lang.includes("hi") || v.name.includes("Hindi"));
  if (hiVoice) utterance.voice = hiVoice;
  
  window.speechSynthesis.speak(utterance);
}

// Chat Handlers
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
  
  // Add User Message
  const userDiv = document.createElement("div");
  userDiv.className = "message user";
  userDiv.innerHTML = `<strong>आप:</strong> ${escapeHtml(text)}`;
  messagesArea.appendChild(userDiv);
  messagesArea.scrollTop = messagesArea.scrollHeight;

  // Loading indicator
  const loadingDiv = document.createElement("div");
  loadingDiv.className = "message agent";
  loadingDiv.id = "agent-loading";
  loadingDiv.innerHTML = `<em>कृषि साथी सोच रहा है... (मौसम व ज्ञानकोश जांच जारी)</em>`;
  messagesArea.appendChild(loadingDiv);
  messagesArea.scrollTop = messagesArea.scrollHeight;

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        session_id: currentSessionId,
        farmer_id: currentFarmerId
      })
    });
    const data = await res.json();
    loadingDiv.remove();

    // Render Agent Message
    const agentDiv = document.createElement("div");
    agentDiv.className = "message agent";

    let thoughtHtml = "";
    if (data.thought_steps && data.thought_steps.length > 0) {
      thoughtHtml = `
        <details class="thought-steps">
          <summary>🧠 एजेंट विचार प्रक्रिया (Agent Reasoning & Tools)</summary>
          <ul>${data.thought_steps.map(s => `<li>${escapeHtml(s)}</li>`).join("")}</ul>
        </details>
      `;
    }

    // Format markdown bold & line breaks
    let formattedResp = escapeHtml(data.response)
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.*?)\*/g, "<em>$1</em>")
      .replace(/\n/g, "<br>");

    agentDiv.innerHTML = `
      ${thoughtHtml}
      <div>${formattedResp}</div>
      <div class="message-actions">
        <button class="tts-btn" onclick="speakText(\`${escapeJsString(data.response)}\`)">🔊 बोलकर सुनाएं</button>
      </div>
    `;
    messagesArea.appendChild(agentDiv);

    // Update Follow-up Chips
    renderChips(data.follow_up_suggestions || []);
    messagesArea.scrollTop = messagesArea.scrollHeight;
  } catch (err) {
    loadingDiv.innerHTML = `<span style="color: red;">त्रुटि: सर्वर से संपर्क नहीं हो सका। कृपया पुनः प्रयास करें।</span>`;
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

// Disease Diagnostic Module
function setupDiseaseUpload() {
  const dropzone = document.getElementById("disease-dropzone");
  const fileInput = document.getElementById("disease-file");
  const resultArea = document.getElementById("disease-result");

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
  
  resultArea.innerHTML = `<div style="text-align: center; padding: 20px;">📸 छवि विश्लेषण जारी है... कृपया प्रतीक्षा करें।</div>`;

  const formData = new FormData();
  formData.append("file", file);
  formData.append("crop_hint", cropHint);
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
      const chem = data.chemical_solution;
      resultArea.innerHTML = `
        <div class="result-card">
          <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #c8e6c9; padding-bottom: 10px; margin-bottom: 12px;">
            <div>
              <h3 style="color: #2e7d32;">${data.disease_name_hindi}</h3>
              <div style="color: #555; font-size: 0.9rem;">फसल: <strong>${data.crop}</strong></div>
            </div>
            <div style="text-align: right;">
              <span class="badge ${data.confidence_score >= 75 ? 'badge-success' : 'badge-warning'}">विश्वास स्कोर: ${data.confidence_score}%</span>
              <div style="font-size: 0.8rem; color: #777; margin-top: 4px;">स्तर: ${data.confidence_level}</div>
            </div>
          </div>

          <p style="margin-bottom: 8px;"><strong>🔍 मुख्य लक्षण:</strong> ${data.symptoms}</p>
          <p style="margin-bottom: 8px;"><strong>🦠 कारण/पैथोजन:</strong> ${data.pathogen_cause}</p>
          <p style="margin-bottom: 8px;"><strong>⚡ तुरंत करने योग्य उपाय:</strong> ${data.immediate_cultural_action}</p>
          <p style="margin-bottom: 8px;"><strong>🌿 जैविक व देसी समाधान (IPM):</strong> ${data.organic_ipm_remedy}</p>
          
          <div style="background: #f9fbe7; border-left: 4px solid #9e9d24; padding: 10px; border-radius: 6px; margin: 12px 0;">
            <strong>🧪 संस्तुत सुरक्षित रासायनिक उपाय:</strong><br>
            • दवा: <strong>${chem.name}</strong><br>
            • मात्रा: ${chem.dose}<br>
            • सावधानी: ${chem.precaution}
          </div>

          <div style="background: #e3f2fd; padding: 8px 12px; border-radius: 6px; font-size: 0.9rem; margin-bottom: 10px;">
            ${data.weather_spray_advisory}
          </div>

          <div style="font-size: 0.82rem; color: #c62828; border-top: 1px dashed #ccc; padding-top: 8px;">
            📌 ${data.kvk_escalation_note}
          </div>
          
          <div style="margin-top: 10px; text-align: right;">
            <button class="tts-btn" onclick="speakText(\`${escapeJsString(data.disease_name_hindi + '. लक्षण: ' + data.symptoms + '. तुरंत उपाय: ' + data.immediate_cultural_action + '. दवा: ' + chem.name + ' ' + chem.dose)}\`)">🔊 निदान बोलकर सुनें</button>
          </div>
        </div>
      `;
    } else {
      resultArea.innerHTML = `<div style="color: red;">${data.error}</div>`;
    }
  } catch (err) {
    resultArea.innerHTML = `<div style="color: red;">त्रुटि: विश्लेषण असफल रहा।</div>`;
  }
}

// Soil Health Card Module
function setupSoilAnalyzer() {
  const form = document.getElementById("soil-form");
  const resultArea = document.getElementById("soil-result");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    resultArea.innerHTML = `<div style="text-align:center; padding: 20px;">मृदा विश्लेषण जारी है...</div>`;

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
      
      let defHtml = data.deficiencies.map(d => `<li>${d}</li>`).join("");
      let amendHtml = data.amendments.map(a => `<li><strong>${a.action}:</strong> ${a.dose} (महत्व: ${a.importance})</li>`).join("");
      let labsHtml = data.nearby_labs.map(l => `
        <div style="background: white; border: 1px solid #c8e6c9; padding: 10px; border-radius: 8px; margin-bottom: 8px;">
          <strong style="color: #2e7d32;">${l.name}</strong> (${l.type})<br>
          <span style="font-size: 0.85rem; color: #555;">📍 ${l.address} | 📞 ${l.contact} | 💰 ${l.fee}</span>
        </div>
      `).join("");

      resultArea.innerHTML = `
        <div class="result-card">
          <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #e8f5e9; padding-bottom: 8px;">
            <h3 style="color: #1b5e20;">मृदा स्वास्थ्य स्कोर: ${data.health_score}/100</h3>
            <span class="badge ${data.health_score >= 70 ? 'badge-success' : 'badge-warning'}">${data.soil_classification.name_hindi}</span>
          </div>
          <p style="margin: 10px 0; font-size: 0.95rem;">${data.hindi_summary}</p>
          
          <h4 style="color: #c62828; margin-top: 12px;">⚠️ प्रमुख पोषक तत्वों की कमियां:</h4>
          <ul>${defHtml || "<li>कोई गंभीर कमी नहीं पाई गई।</li>"}</ul>

          <h4 style="color: #2e7d32; margin-top: 12px;">🌾 सुधारात्मक कृषि सिफारिशें:</h4>
          <ul>${amendHtml || "<li>संतुलित गोबर खाद व वर्मीकम्पोस्ट का प्रयोग जारी रखें।</li>"}</ul>

          <h4 style="color: #0288d1; margin-top: 15px; margin-bottom: 8px;">🏛️ नजदीकी सरकारी मृदा परीक्षण प्रयोगशालाएं:</h4>
          ${labsHtml}
        </div>
      `;
    } catch (err) {
      resultArea.innerHTML = `<div style="color: red;">त्रुटि: विश्लेषण असफल रहा।</div>`;
    }
  });
}

// Crop Recommender Module
function setupCropRecommender() {
  const form = document.getElementById("crop-rec-form");
  const resultArea = document.getElementById("crop-rec-result");
  const syncBtn = document.getElementById("sync-weather-crop-btn");

  syncBtn.addEventListener("click", () => {
    if (liveWeatherCache && liveWeatherCache.current) {
      document.getElementById("crop-temp").value = liveWeatherCache.current.temperature;
      document.getElementById("crop-humidity").value = liveWeatherCache.current.humidity;
      alert(`मौसम आंकड़े सिंक हुए: तापमान ${liveWeatherCache.current.temperature}°C, नमी ${liveWeatherCache.current.humidity}%`);
    } else {
      alert("मौसम डेटा लोड हो रहा है, कृपया 1 सेकंड बाद दबाएं।");
    }
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    resultArea.innerHTML = `<div style="text-align: center; padding: 20px;">सर्वोत्तम फसलों की गणना हो रही है...</div>`;

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
      
      const cardsHtml = data.top_recommendations.map((c, i) => `
        <div style="background: white; border: 1px solid #c8e6c9; border-radius: 10px; padding: 15px; margin-bottom: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.04);">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <h3 style="color: #2e7d32;">#${i+1} ${c.hindi_name}</h3>
            <span class="badge badge-success">अनुकूलता: ${c.suitability_score}%</span>
          </div>
          <p style="font-size: 0.9rem; color: #444; margin: 8px 0;">${c.description}</p>
          <div style="font-size: 0.85rem; color: #555; display: flex; gap: 15px; flex-wrap: wrap;">
            <span>📅 बुवाई समय: <strong>${c.sowing_months}</strong></span>
            <span>💧 पानी: <strong>${c.water_need}</strong></span>
            <span>🍂 फसल चक्र: <strong>${c.season}</strong></span>
          </div>
        </div>
      `).join("");

      resultArea.innerHTML = `
        <div class="result-card">
          <h4 style="color: #1b5e20; margin-bottom: 10px;">🌟 शीर्ष अनुशंसित फसलें (${data.current_season}):</h4>
          ${cardsHtml}
          <div style="background: #f1f8e9; padding: 10px; border-radius: 8px; font-size: 0.9rem; color: #33691e; margin-top: 10px;">
            💡 ${data.summary_hindi}
          </div>
        </div>
      `;
    } catch (err) {
      resultArea.innerHTML = `<div style="color: red;">त्रुटि: फसल अनुशंसा असफल रही।</div>`;
    }
  });
}

// Schemes Search Module
function setupSchemesSearch() {
  const searchInput = document.getElementById("schemes-search");
  const container = document.getElementById("schemes-display-box");

  async function fetchSchemes(q = "") {
    try {
      const res = await fetch(`/api/schemes?q=${encodeURIComponent(q)}`);
      const data = await res.json();
      if (data.schemes) {
        container.innerHTML = data.schemes.map(s => `
          <div style="background: white; border: 1px solid #c8e6c9; border-radius: 10px; padding: 15px; margin-bottom: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; padding-bottom: 8px;">
              <h3 style="color: #1b5e20; font-size: 1.15rem;">🏛️ ${s.name}</h3>
              <span style="font-size: 0.8rem; background: #e0f2f1; color: #00796b; padding: 3px 8px; border-radius: 10px;">${s.ministry}</span>
            </div>
            <p style="margin: 10px 0; font-size: 0.92rem; line-height: 1.4;">${s.objective}</p>
            <div style="font-size: 0.88rem; line-height: 1.5; background: #fafafa; padding: 10px; border-radius: 6px;">
              <strong>🎯 पात्रता:</strong> ${s.eligibility}<br>
              <strong>💰 मुख्य लाभ:</strong> ${s.benefits}<br>
              <strong>📝 आवेदन कैसे करें:</strong> ${s.how_to_apply}<br>
              <strong>📞 हेल्पलाइन:</strong> <span style="color: #d32f2f; font-weight: 700;">${s.helpline}</span>
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

// Farmer Profile Loading & Updating
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
      irrigation_type: "ट्यूबवेल"
    };

    try {
      const res = await fetch("/api/profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      alert("✅ प्रोफाइल सफलतापूर्वक सुरक्षित हुई!");
      loadLiveWeather(payload.district);
    } catch (err) {
      alert("त्रुटि: प्रोफाइल सुरक्षित नहीं हो सकी।");
    }
  });
}

// Helpers
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
