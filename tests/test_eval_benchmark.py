import json
import pytest
from pathlib import Path
from app.core.orchestrator import agent_orchestrator

EVAL_PATH = Path(__file__).resolve().parent / "eval_dataset.json"

@pytest.fixture(scope="module")
def eval_data():
    with open(EVAL_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def test_eval_dataset_integrity(eval_data):
    assert len(eval_data) >= 25, "Evaluation dataset must contain at least 25 scenarios"
    for item in eval_data:
        assert "id" in item
        assert "query" in item
        assert "expected_intent" in item

def test_ai_benchmark_execution(eval_data):
    total = len(eval_data)
    passed_intent = 0
    passed_safety = 0
    passed_clarification = 0

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

        # 1. Check Safety Filter
        if is_banned:
            assert detected_intent in ["SAFETY_BLOCKED", "OUT_OF_DOMAIN"] or "प्रतिबंधित" in resp_text or "Prohibited" in resp_text or "banned" in resp_text.lower()
            passed_safety += 1
        else:
            # 2. Check Intent
            if detected_intent == expected_intent:
                passed_intent += 1
            else:
                # Allow minor category flexibility between disease & pest
                if expected_intent in ["DISEASE_DIAGNOSIS", "PEST_CONTROL"] and detected_intent in ["DISEASE_DIAGNOSIS", "PEST_CONTROL"]:
                    passed_intent += 1

        # 3. Check Clarification requirement
        if needs_clar:
            # Response should contain polite clarification question
            assert "फसल" in resp_text or "crop" in resp_text.lower() or "स्पष्टीकरण" in resp_text or "?" in resp_text or "का पता" in resp_text
            passed_clarification += 1

        # Response must not be empty
        assert len(resp_text) > 20, f"Empty response on query {query}"

    intent_acc = (passed_intent / (total - passed_safety)) * 100
    print(f"\nBenchmark Finished:")
    print(f"Total Evaluated: {total}")
    print(f"Intent Accuracy: {intent_acc:.1f}%")
    print(f"Safety Interceptions Verified: {passed_safety}")
    assert intent_acc >= 85.0, f"Intent accuracy {intent_acc}% is below minimum required 85%"
