import json
import pytest
from pathlib import Path
from app.core.orchestrator import agent_orchestrator

EVAL_PATH = Path(__file__).resolve().parent / "eval_dataset.json"

GENERIC_PHRASES = [
    "based on standard agronomic practices, maintain balanced fertilization",
    "सामान्य कृषि संस्तुतियों के अनुसार संतुलित उर्वरक, समय पर निराई-गुड़ाई",
    "appropriate irrigation schedules"
]

@pytest.fixture(scope="module")
def eval_data():
    with open(EVAL_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def test_eval_dataset_integrity(eval_data):
    assert len(eval_data) >= 100, f"Evaluation dataset must contain at least 100 scenarios, found {len(eval_data)}"
    for item in eval_data:
        assert "id" in item
        assert "query" in item
        assert "expected_intent" in item

def test_ai_benchmark_execution(eval_data):
    total = len(eval_data)
    passed_intent = 0
    passed_safety = 0
    passed_clarification = 0
    generic_responses = 0

    print("\n" + "="*70)
    print(f"RUNNING KRISHISAATHI AI EVALUATION BENCHMARK ({total} SCENARIOS)")
    print("="*70)

    for case in eval_data:
        q_id = case["id"]
        query = case["query"]
        expected_intent = case["expected_intent"]
        is_banned = case.get("is_banned", False)
        needs_clar = case.get("needs_clarification", False)

        # Execute using distinct fresh session to prevent cross-test turn leakage
        res = agent_orchestrator.process_query(
            query=query,
            session_id=f"eval_session_{q_id}",
            farmer_id=f"eval_farmer_{q_id}"
        )

        detected_intent = res.get("intent")
        resp_text = res.get("response", "")

        # 1. Zero Generic Response Validation
        resp_lower = resp_text.lower()
        for gp in GENERIC_PHRASES:
            if gp in resp_lower:
                generic_responses += 1
                print(f"Generic response detected on {q_id} ({query}): {resp_text[:100]}...")
                break

        # 2. Check Safety Filter
        if is_banned:
            assert detected_intent in ["SAFETY_BLOCKED", "OUT_OF_DOMAIN"] or "प्रतिबंधित" in resp_text or "Prohibited" in resp_text or "banned" in resp_text.lower()
            passed_safety += 1
        else:
            # 3. Check Intent
            if detected_intent == expected_intent:
                passed_intent += 1
            else:
                # Allow minor category flexibility between disease & pest or forecast & query
                if expected_intent in ["DISEASE_DIAGNOSIS", "PEST_CONTROL", "CROP_DISEASE", "PEST_IDENTIFICATION"] and detected_intent in ["DISEASE_DIAGNOSIS", "PEST_CONTROL", "CROP_DISEASE", "PEST_IDENTIFICATION"]:
                    passed_intent += 1
                elif expected_intent in ["WEATHER_QUERY", "WEATHER_FORECAST", "RAINFALL_QUERY"] and detected_intent in ["WEATHER_QUERY", "WEATHER_FORECAST", "RAINFALL_QUERY"]:
                    passed_intent += 1
                elif expected_intent in ["FERTILIZER_RECOMMENDATION", "FERTILIZER_ADVISORY"] and detected_intent in ["FERTILIZER_RECOMMENDATION", "FERTILIZER_ADVISORY"]:
                    passed_intent += 1
                elif expected_intent in ["GOVERNMENT_SCHEME", "GOVT_SCHEME"] and detected_intent in ["GOVERNMENT_SCHEME", "GOVT_SCHEME"]:
                    passed_intent += 1
                elif expected_intent in ["SOIL_ANALYSIS", "SOIL_TYPE"] and detected_intent in ["SOIL_ANALYSIS", "SOIL_TYPE"]:
                    passed_intent += 1
                else:
                    print(f"Intent Mismatch on {q_id}: Expected '{expected_intent}', got '{detected_intent}' (Query: {query})")

        # 4. Check Clarification requirement
        if needs_clar:
            assert "फसल" in resp_text or "crop" in resp_text.lower() or "स्पष्टीकरण" in resp_text or "?" in resp_text or "का पता" in resp_text
            passed_clarification += 1

        # Response must not be empty
        assert len(resp_text) > 20, f"Empty response on query {query}"

    intent_acc = (passed_intent / (total - passed_safety)) * 100
    generic_rate = (generic_responses / total) * 100

    print(f"\nBenchmark Results:")
    print(f"Total Evaluated: {total}")
    print(f"Intent Accuracy: {intent_acc:.1f}%")
    print(f"Generic Response Rate: {generic_rate:.1f}% ({generic_responses}/{total})")
    print(f"Safety Interceptions Verified: {passed_safety}")

    # Strict Assertions: Zero Generic Responses and High Accuracy
    assert generic_responses == 0, f"Zero generic response failure: {generic_responses} generic responses found"
    assert intent_acc >= 85.0, f"Intent accuracy {intent_acc:.1f}% is below minimum required 85%"
