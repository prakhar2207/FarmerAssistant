import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.config import DB_PATH

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS farmer_profiles (
        farmer_id TEXT PRIMARY KEY,
        name TEXT,
        village TEXT,
        district TEXT,
        state TEXT,
        farm_size_acres REAL,
        current_crop TEXT,
        soil_type TEXT,
        irrigation_type TEXT,
        language TEXT DEFAULT 'Hindi'
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        farmer_id TEXT,
        user_message TEXT,
        agent_response TEXT,
        intent TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS diagnostic_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farmer_id TEXT,
        crop TEXT,
        disease_detected TEXT,
        confidence REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Insert default test profile if not exists
    cursor.execute("SELECT COUNT(*) FROM farmer_profiles WHERE farmer_id = 'default_farmer'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO farmer_profiles (farmer_id, name, village, district, state, farm_size_acres, current_crop, soil_type, irrigation_type)
        VALUES ('default_farmer', 'रामसिंह वर्मा (Ram Singh)', 'बख्शी का तालाब', 'Lucknow', 'Uttar Pradesh', 3.5, 'गेहूं', 'जलोढ़ दोमट', 'नहर व ट्यूबवेल')
        """)
        
    conn.commit()
    conn.close()

def get_farmer_profile(farmer_id: str = "default_farmer") -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM farmer_profiles WHERE farmer_id = ?", (farmer_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return {
        "farmer_id": farmer_id,
        "name": "किसान मित्र",
        "village": "ग्राम पंचायत",
        "district": "Lucknow",
        "state": "Uttar Pradesh",
        "farm_size_acres": 2.5,
        "current_crop": "गेहूं",
        "soil_type": "जलोढ़",
        "irrigation_type": "ट्यूबवेल"
    }

def update_farmer_profile(profile_data: Dict[str, Any]) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO farmer_profiles (farmer_id, name, village, district, state, farm_size_acres, current_crop, soil_type, irrigation_type)
    VALUES (:farmer_id, :name, :village, :district, :state, :farm_size_acres, :current_crop, :soil_type, :irrigation_type)
    ON CONFLICT(farmer_id) DO UPDATE SET
        name = excluded.name,
        village = excluded.village,
        district = excluded.district,
        state = excluded.state,
        farm_size_acres = excluded.farm_size_acres,
        current_crop = excluded.current_crop,
        soil_type = excluded.soil_type,
        irrigation_type = excluded.irrigation_type
    """, profile_data)
    conn.commit()
    conn.close()
    return True

def save_chat_turn(session_id: str, farmer_id: str, user_msg: str, agent_resp: str, intent: str = "GENERAL"):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO chat_history (session_id, farmer_id, user_message, agent_response, intent)
    VALUES (?, ?, ?, ?, ?)
    """, (session_id, farmer_id, user_msg, agent_resp, intent))
    conn.commit()
    conn.close()

def get_recent_chat_history(session_id: str, limit: int = 5) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT user_message, agent_response, intent, timestamp 
    FROM chat_history 
    WHERE session_id = ? 
    ORDER BY id DESC LIMIT ?
    """, (session_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in reversed(rows)]

def get_chat_sessions(farmer_id: str = "default_farmer", limit: int = 20) -> List[Dict[str, Any]]:
    """Retrieves all distinct chat sessions for a farmer with title and message count."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT session_id, user_message, intent, MAX(timestamp) as last_activity, COUNT(id) as message_count
    FROM chat_history
    WHERE farmer_id = ?
    GROUP BY session_id
    ORDER BY last_activity DESC
    LIMIT ?
    """, (farmer_id, limit))
    rows = cursor.fetchall()
    conn.close()
    sessions = []
    for r in rows:
        msg = r["user_message"] or "कृषि परामर्श / Farm Chat"
        title = msg[:36] + ("..." if len(msg) > 36 else "")
        sessions.append({
            "session_id": r["session_id"],
            "title": title,
            "intent": r["intent"],
            "last_activity": r["last_activity"],
            "message_count": r["message_count"]
        })
    return sessions

def get_session_turns(session_id: str) -> List[Dict[str, Any]]:
    """Retrieves full conversation turns for a session in chronological order."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT user_message, agent_response, intent, timestamp 
    FROM chat_history 
    WHERE session_id = ? 
    ORDER BY id ASC
    """, (session_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_chat_session(session_id: str) -> bool:
    """Deletes all messages associated with a session."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()
    return True

def clear_all_chat_history(farmer_id: str = "default_farmer") -> bool:
    """Resets all chat history for a farmer."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_history WHERE farmer_id = ?", (farmer_id,))
    conn.commit()
    conn.close()
    return True

init_db()

