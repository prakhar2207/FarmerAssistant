import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import desc, func
from app.db.session import SessionLocal, init_db
from app.db.models import FarmerProfile, Conversation, Message, DiseasePrediction

def utc_now_naive():
    return datetime.now(timezone.utc).replace(tzinfo=None)

def get_farmer_profile(farmer_id: str = "default_farmer") -> Dict[str, Any]:
    """Retrieves farmer profile via SQLAlchemy ORM."""
    db = SessionLocal()
    try:
        profile = db.query(FarmerProfile).filter_by(farmer_id=farmer_id).first()
        if profile:
            return {
                "farmer_id": profile.farmer_id,
                "name": profile.name,
                "village": profile.village or "",
                "district": profile.district,
                "state": profile.state,
                "farm_size_acres": profile.farm_size_acres,
                "current_crop": profile.current_crop,
                "soil_type": profile.soil_type,
                "irrigation_type": profile.irrigation_type,
                "language": profile.language
            }
        return {
            "farmer_id": farmer_id,
            "name": "किसान मित्र",
            "village": "ग्राम पंचायत",
            "district": "Lucknow",
            "state": "Uttar Pradesh",
            "farm_size_acres": 2.5,
            "current_crop": "गेहूं",
            "soil_type": "जलोढ़",
            "irrigation_type": "ट्यूबवेल",
            "language": "Hindi"
        }
    finally:
        db.close()

def update_farmer_profile(profile_data: Dict[str, Any]) -> bool:
    """Updates or inserts farmer profile in relational database."""
    db = SessionLocal()
    try:
        fid = profile_data.get("farmer_id", "default_farmer")
        profile = db.query(FarmerProfile).filter_by(farmer_id=fid).first()
        if not profile:
            profile = FarmerProfile(farmer_id=fid)
            db.add(profile)

        profile.name = profile_data.get("name", profile.name)
        profile.village = profile_data.get("village", profile.village)
        profile.district = profile_data.get("district", profile.district)
        profile.state = profile_data.get("state", profile.state)
        profile.farm_size_acres = profile_data.get("farm_size_acres", profile.farm_size_acres)
        profile.current_crop = profile_data.get("current_crop", profile.current_crop)
        profile.soil_type = profile_data.get("soil_type", profile.soil_type)
        profile.irrigation_type = profile_data.get("irrigation_type", profile.irrigation_type)
        if "language" in profile_data:
            profile.language = profile_data["language"]
        profile.updated_at = utc_now_naive()

        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def save_chat_turn(
    session_id: str,
    farmer_id: str,
    user_msg: str,
    agent_resp: str,
    intent: str,
    status_badges: Optional[List[Dict[str, Any]]] = None,
    citations: Optional[List[Dict[str, Any]]] = None
):
    """Persists a conversation turn and updates session metadata."""
    db = SessionLocal()
    try:
        # Update or create conversation header
        conv = db.query(Conversation).filter_by(session_id=session_id).first()
        title = user_msg.strip()[:36] + ("..." if len(user_msg.strip()) > 36 else "") if user_msg else "कृषि संवाद"
        if not conv:
            conv = Conversation(
                session_id=session_id,
                farmer_id=farmer_id,
                title=title,
                intent=intent,
                created_at=utc_now_naive(),
                updated_at=utc_now_naive()
            )
            db.add(conv)
        else:
            conv.updated_at = utc_now_naive()
            conv.intent = intent

        # Add message record
        msg = Message(
            session_id=session_id,
            sender="user",
            user_message=user_msg,
            agent_response=agent_resp,
            intent=intent,
            status_badges=json.dumps(status_badges, ensure_ascii=False) if status_badges else None,
            citations=json.dumps(citations, ensure_ascii=False) if citations else None,
            timestamp=utc_now_naive()
        )
        db.add(msg)
        db.commit()
    except Exception as e:
        db.rollback()
    finally:
        db.close()

def get_recent_chat_history(session_id: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Retrieves recent conversation turns for context memory."""
    db = SessionLocal()
    try:
        msgs = db.query(Message).filter_by(session_id=session_id)\
                 .order_by(desc(Message.id))\
                 .limit(limit).all()
        # Return in chronological order
        return [
            {
                "user_message": m.user_message,
                "agent_response": m.agent_response,
                "intent": m.intent,
                "timestamp": str(m.timestamp)
            }
            for m in reversed(msgs)
        ]
    finally:
        db.close()

def get_chat_sessions(farmer_id: str = "default_farmer", limit: int = 20) -> List[Dict[str, Any]]:
    """Retrieves distinct conversation sessions with preview and message count."""
    db = SessionLocal()
    try:
        convs = db.query(Conversation).filter_by(farmer_id=farmer_id)\
                  .order_by(desc(Conversation.updated_at))\
                  .limit(limit).all()
        sessions = []
        for c in convs:
            count = db.query(func.count(Message.id)).filter_by(session_id=c.session_id).scalar() or 0
            sessions.append({
                "session_id": c.session_id,
                "title": c.title,
                "preview": c.title,
                "intent": c.intent,
                "last_activity": str(c.updated_at),
                "message_count": count
            })
        return sessions
    finally:
        db.close()

def get_session_turns(session_id: str) -> List[Dict[str, Any]]:
    """Retrieves full conversation turns for a session in chronological order."""
    db = SessionLocal()
    try:
        msgs = db.query(Message).filter_by(session_id=session_id)\
                 .order_by(Message.id.asc()).all()
        return [
            {
                "user_query": m.user_message,
                "bot_response": m.agent_response,
                "intent": m.intent,
                "status_badges": json.loads(m.status_badges) if m.status_badges else [],
                "citations": json.loads(m.citations) if m.citations else [],
                "timestamp": str(m.timestamp)
            }
            for m in msgs
        ]
    finally:
        db.close()

def delete_chat_session(session_id: str) -> bool:
    """Deletes conversation and associated messages."""
    db = SessionLocal()
    try:
        db.query(Message).filter_by(session_id=session_id).delete()
        db.query(Conversation).filter_by(session_id=session_id).delete()
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        return False
    finally:
        db.close()

def clear_all_chat_history(farmer_id: str = "default_farmer") -> bool:
    """Resets all chat history for a farmer."""
    db = SessionLocal()
    try:
        sessions = [c.session_id for c in db.query(Conversation).filter_by(farmer_id=farmer_id).all()]
        for sid in sessions:
            db.query(Message).filter_by(session_id=sid).delete()
        db.query(Conversation).filter_by(farmer_id=farmer_id).delete()
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        return False
    finally:
        db.close()

# Auto-initialize database schema on import
init_db()
