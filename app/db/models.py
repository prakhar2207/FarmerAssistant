from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.session import Base

def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    role = Column(String(50), default="farmer")
    created_at = Column(DateTime, default=utc_now)

class FarmerProfile(Base):
    __tablename__ = "farmer_profiles"

    farmer_id = Column(String(100), primary_key=True, index=True)
    name = Column(String(150), default="किसान")
    village = Column(String(150), nullable=True)
    district = Column(String(100), default="Lucknow")
    state = Column(String(100), default="Uttar Pradesh")
    farm_size_acres = Column(Float, default=2.5)
    current_crop = Column(String(100), default="गेहूं")
    soil_type = Column(String(100), default="जलोढ़")
    irrigation_type = Column(String(100), default="ट्यूबवेल")
    language = Column(String(20), default="Hindi")
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

class Farm(Base):
    __tablename__ = "farms"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(String(100), ForeignKey("farmer_profiles.farmer_id"), index=True)
    farm_name = Column(String(150), default="मुख्य खेत")
    total_acres = Column(Float, default=2.5)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime, default=utc_now)

class Plot(Base):
    __tablename__ = "plots"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), index=True)
    plot_name = Column(String(100), default="प्लॉट 1")
    acres = Column(Float, default=1.0)
    soil_type = Column(String(100), default="दोमट")
    created_at = Column(DateTime, default=utc_now)

class CropCycle(Base):
    __tablename__ = "crop_cycles"

    id = Column(Integer, primary_key=True, index=True)
    plot_id = Column(Integer, ForeignKey("plots.id"), index=True)
    crop = Column(String(100), nullable=False)
    variety = Column(String(100), nullable=True)
    season = Column(String(50), default="Rabi")
    sowing_date = Column(DateTime, nullable=True)
    stage = Column(String(100), default="वेजिटेटिव (Vegetative)")
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=utc_now)

class SoilReport(Base):
    __tablename__ = "soil_reports"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(String(100), ForeignKey("farmer_profiles.farmer_id"), index=True)
    filename = Column(String(255), nullable=True)
    lab_name = Column(String(200), nullable=True)
    test_date = Column(DateTime, default=utc_now)
    health_score = Column(Integer, default=75)
    classification = Column(String(100), default="सामान्य")
    created_at = Column(DateTime, default=utc_now)

class SoilParameter(Base):
    __tablename__ = "soil_parameters"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("soil_reports.id"), index=True)
    parameter_name = Column(String(50), nullable=False)  # pH, OC, N, P, K, EC, Zn, S, Fe
    extracted_value = Column(Float, nullable=False)
    unit = Column(String(30), default="kg/ha")
    status = Column(String(50), default="optimal")

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    farmer_id = Column(String(100), default="default_farmer", index=True)
    title = Column(String(255), default="कृषि संवाद / Farm Chat")
    intent = Column(String(50), default="GENERAL_AGRI")
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), ForeignKey("conversations.session_id"), index=True)
    sender = Column(String(20), default="user")  # "user" or "assistant"
    user_message = Column(Text, nullable=True)
    agent_response = Column(Text, nullable=True)
    intent = Column(String(50), nullable=True)
    status_badges = Column(Text, nullable=True)  # JSON serialized
    citations = Column(Text, nullable=True)      # JSON serialized
    timestamp = Column(DateTime, default=utc_now)

class ToolRun(Base):
    __tablename__ = "tool_runs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True)
    tool_name = Column(String(100), nullable=False)
    execution_time_ms = Column(Float, default=0.0)
    success = Column(Boolean, default=True)
    output_summary = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=utc_now)

class WeatherCache(Base):
    __tablename__ = "weather_cache"

    id = Column(Integer, primary_key=True, index=True)
    district = Column(String(100), index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    payload = Column(Text, nullable=False)  # JSON string
    cached_at = Column(DateTime, default=utc_now)
    expires_at = Column(DateTime, nullable=False)

class DiseasePrediction(Base):
    __tablename__ = "disease_predictions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True, nullable=True)
    crop = Column(String(100), nullable=True)
    disease_detected = Column(String(150), nullable=False)
    confidence = Column(Float, nullable=False)
    bounding_boxes = Column(Text, nullable=True)  # JSON
    image_path = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=utc_now)
