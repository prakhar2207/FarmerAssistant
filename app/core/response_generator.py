from app.core.response_planner import ResponsePlan

def generate_response_text(plan: ResponsePlan, lang: str = "hi") -> str:
    """
    Renders structured ResponsePlan into an authentic, localized agricultural advisory.
    Format:
    1. Direct Answer First (1-2 clear sentences)
    2. Agronomic / Scientific Rationale
    3. Immediate Practical Action Steps
    4. Critical Pitfalls to Avoid
    5. Environmental / Weather Context
    6. KVK Help / Escalation
    """
    sections = []

    # 1. Direct Answer
    direct = plan.direct_answer_en if lang == "en" else plan.direct_answer_hi
    if direct:
        header = "🌾 **कृषि परामर्श (Agricultural Advisory):**" if lang == "hi" else "🌾 **Agricultural Expert Advisory:**"
        sections.append(f"{header}\n{direct.strip()}")

    # 2. Agronomic / Scientific Rationale
    rationale = plan.agronomic_rationale_en if lang == "en" else plan.agronomic_rationale_hi
    if rationale:
        heading = "🔬 **वैज्ञानिक विश्लेषण एवं कारण:**" if lang == "hi" else "🔬 **Agronomic Rationale & Cause:**"
        sections.append(f"{heading}\n{rationale.strip()}")

    # 3. Immediate Practical Action Steps
    actions = plan.immediate_actions_en if lang == "en" else plan.immediate_actions_hi
    if actions:
        heading = "🚜 **त्वरित व्यावहारिक कदम (Immediate Action Plan):**" if lang == "hi" else "🚜 **Immediate Practical Action Steps:**"
        act_lines = "\n".join([f"• {a}" for a in actions])
        sections.append(f"{heading}\n{act_lines}")

    # 4. What to Avoid
    avoids = plan.avoid_actions_en if lang == "en" else plan.avoid_actions_hi
    if avoids:
        heading = "⚠️ **क्या न करें (Things to Avoid):**" if lang == "hi" else "⚠️ **What to Avoid:**"
        avoid_lines = "\n".join([f"• {av}" for av in avoids])
        sections.append(f"{heading}\n{avoid_lines}")

    # 5. Environmental & Context Facts
    facts = plan.context_facts_en if lang == "en" else plan.context_facts_hi
    if facts:
        heading = "📊 **मौसम एवं कृषि संदर्भ:**" if lang == "hi" else "📊 **Environmental & Agro-Context:**"
        fact_lines = " | ".join(facts)
        sections.append(f"{heading}\n{fact_lines}")

    # 6. KVK Escalation / Follow-up Clarification
    kvk = plan.kvk_advisory_en if lang == "en" else plan.kvk_advisory_hi
    if kvk:
        heading = "💡 **सटीक समाधान हेतु जानकारी:**" if lang == "hi" else "💡 **Additional Information Needed:**"
        sections.append(f"{heading}\n{kvk.strip()}")

    return "\n\n".join(sections)
