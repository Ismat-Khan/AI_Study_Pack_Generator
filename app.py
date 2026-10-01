"""
StudySpark AI - Main Streamlit Application
"""

import json
import os

import streamlit as st

from workflow import STAGES, create_context, run_stage


# ============================================================
# SAFE HELPERS
# ============================================================

def as_dict(value):
    return value if isinstance(value, dict) else {}


def as_list(value):
    return value if isinstance(value, list) else []


def as_text(value, default=""):
    if value is None:
        return default
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def display_options(options):
    if isinstance(options, dict):
        for key, value in options.items():
            st.write(f"**{as_text(key)}.** {as_text(value)}")
    elif isinstance(options, list):
        for index, option in enumerate(options):
            st.write(f"**{chr(65 + index)}.** {as_text(option)}")
    elif options:
        st.write(as_text(options))
    else:
        st.caption("No options were returned.")


def display_concepts(concepts):
    items = as_list(concepts)

    if not items:
        st.caption("No key concepts were returned.")
        return

    for item in items:
        if isinstance(item, dict):
            concept = as_text(item.get("concept", ""))
            explanation = as_text(item.get("explanation", ""))

            if concept:
                st.markdown(f"**{concept}**")
            if explanation:
                st.write(explanation)
        else:
            st.write(as_text(item))


def display_flashcards(cards):
    items = as_list(cards)

    if not items:
        st.caption("No flashcards were returned.")
        return

    for index, raw_card in enumerate(items, 1):
        card = as_dict(raw_card)
        question = as_text(card.get("question", f"Card {index}"))
        answer = as_text(card.get("answer", ""))

        with st.expander(f"Card {index}: {question}"):
            st.write(answer or "No answer returned.")


def display_mcqs(mcqs):
    st.markdown("### ❓ MCQs")

    items = as_list(mcqs)

    if not items:
        st.info("No MCQs were returned.")
        return

    for index, raw_mcq in enumerate(items, 1):
        mcq = as_dict(raw_mcq)

        question = as_text(mcq.get("question", ""))
        st.markdown(f"**{index}. {question}**")

        display_options(mcq.get("options", {}))

        with st.expander("Show answer"):
            answer = as_text(mcq.get("answer", ""))
            explanation = as_text(mcq.get("explanation", ""))

            st.success(answer or "No answer returned.")

            if explanation:
                st.write(explanation)


def display_question_section(items, title):
    st.markdown(title)

    questions = as_list(items)

    if not questions:
        st.caption("No questions were returned.")
        return

    for raw_item in questions:
        item = as_dict(raw_item)

        question = as_text(
            item.get("question", "Question")
        )
        answer = as_text(
            item.get("answer", "")
        )

        with st.expander(question):
            st.write(answer or "No answer returned.")


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="StudySpark AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>
    .hero {
        padding: 28px;
        border-radius: 22px;
        border: 1px solid rgba(128,128,128,.25);
        margin-bottom: 24px;
    }

    .hero h1 {
        margin: 0;
        font-size: 42px;
    }

    .hero p {
        margin-top: 8px;
        opacity: .75;
        font-size: 17px;
    }

    .stage-card {
        padding: 14px 16px;
        border-radius: 14px;
        border: 1px solid rgba(128,128,128,.25);
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">
        <h1>📚 StudySpark AI</h1>
        <p>
            Personalized study packs created through a
            Planning → Content → Assessment → Review → Refinement workflow.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.header("⚙️ Study Settings")

    default_api_key = ""

    try:
        default_api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        default_api_key = os.getenv("GROQ_API_KEY", "")

    api_key = st.text_input(
        "Groq API Key",
        value=default_api_key,
        type="password",
        help="For Streamlit Cloud, store this in Secrets.",
    )

    learner_level = st.selectbox(
        "Student Level",
        ["Beginner", "Intermediate", "Advanced"],
        index=1,
    )

    learning_goal = st.selectbox(
        "Learning Goal",
        [
            "Exam preparation",
            "Quick revision",
            "Concept understanding",
            "Interview preparation",
            "Assignment preparation",
        ],
    )

    pack_type = st.selectbox(
        "Study Pack Type",
        [
            "Complete Study Pack",
            "Quick Revision Pack",
            "Exam Preparation Pack",
        ],
    )

    question_count = st.slider(
        "Questions per section",
        min_value=1,
        max_value=10,
        value=5,
    )

    st.divider()
    st.caption("AI Model: openai/gpt-oss-120b")
    st.caption("Backend: Groq API")
    st.caption("Deployment: Streamlit")


# ============================================================
# INPUT AREA
# ============================================================

left, right = st.columns([1.15, 0.85])

with left:
    st.subheader("📝 Your Study Material")

    topic = st.text_input(
        "Topic",
        placeholder="e.g. Object-Oriented Programming in Dart",
    )

    source_text = st.text_area(
        "Notes / Lecture Material",
        height=280,
        placeholder=(
            "Paste your notes, lecture text, textbook content, "
            "or leave this empty."
        ),
    )


with right:
    st.subheader("🤖 AI Workflow")

    workflow_display = [
        ("1", "🧭 Planning", "Creates the learning blueprint"),
        ("2", "📚 Content", "Generates learning material"),
        ("3", "📝 Assessment", "Creates questions"),
        ("4", "🔎 Review", "Checks quality"),
        ("5", "✨ Refinement", "Creates final pack"),
    ]

    for number, name, description in workflow_display:
        st.markdown(
            f"""
            <div class="stage-card">
                <b>{number}. {name}</b>
                <br>
                <small>{description}</small>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# GENERATE
# ============================================================

generate = st.button(
    "🚀 Generate Study Pack",
    type="primary",
    use_container_width=True,
)


if generate:
    if not api_key:
        st.error("Please enter your Groq API key.")
        st.stop()

    if not topic.strip():
        st.error("Please enter a topic.")
        st.stop()

    context = create_context(
        topic=topic,
        source_text=source_text,
        learner_level=learner_level,
        learning_goal=learning_goal,
        pack_type=pack_type,
        question_count=question_count,
    )

    progress = st.progress(0)
    status = st.empty()
    workflow_failed = False

    for index, stage_name in enumerate(STAGES):
        status.info(
            f"🤖 AI Stage {index + 1}/5: **{stage_name}** is working..."
        )

        try:
            context = run_stage(
                context=context,
                stage_name=stage_name,
                api_key=api_key,
            )
        except Exception as exc:
            workflow_failed = True
            context.record_error(stage_name, str(exc))
            st.error(f"❌ {stage_name} failed: {exc}")
            break

        progress.progress((index + 1) / len(STAGES))

    if workflow_failed:
        status.warning("Workflow stopped because a stage failed.")
    else:
        status.success("Workflow completed successfully.")

    st.session_state["context"] = context


# ============================================================
# RESULTS
# ============================================================

context = st.session_state.get("context")

if context:
    st.divider()
    st.header("🤖 Workflow Status")

    columns = st.columns(5)

    for index, stage_name in enumerate(STAGES):
        with columns[index]:
            if stage_name in context.completed_stages:
                st.success(f"✓ {stage_name}")
            else:
                st.warning(f"Not completed: {stage_name}")

    if context.errors:
        st.warning("Some stages encountered errors.")

        for raw_error in as_list(context.errors):
            error = as_dict(raw_error)

            stage = as_text(
                error.get("stage", "Unknown stage")
            )
            message = as_text(
                error.get("message", "Unknown error")
            )

            st.error(f"{stage}: {message}")

    tabs = st.tabs(
        [
            "🧭 Plan",
            "📚 Content",
            "📝 Assessment",
            "🔎 Review",
            "✨ Final Pack",
        ]
    )

    # ========================================================
    # PLAN
    # ========================================================

    with tabs[0]:
        st.subheader("Learning Plan")

        plan = as_dict(context.plan)

        if plan:
            st.json(plan)
        else:
            st.info("Planning stage did not complete.")

    # ========================================================
    # CONTENT
    # ========================================================

    with tabs[1]:
        st.subheader("Generated Content")

        content = as_dict(context.content)

        if content:
            summary = as_text(content.get("summary", ""))

            if summary:
                st.markdown("### 📌 Summary")
                st.write(summary)

            st.markdown("### 🧠 Key Concepts")
            display_concepts(
                content.get("key_concepts", [])
            )

            st.markdown("### 🃏 Flashcards")
            display_flashcards(
                content.get("flashcards", [])
            )
        else:
            st.info("Content stage did not complete.")

    # ========================================================
    # ASSESSMENT
    # ========================================================

    with tabs[2]:
        st.subheader("Assessment")

        assessment = as_dict(context.assessment)

        if assessment:
            display_mcqs(
                assessment.get("mcqs", [])
            )

            display_question_section(
                assessment.get("short_questions", []),
                "### ✍️ Short Questions",
            )

            display_question_section(
                assessment.get("long_questions", []),
                "### 📖 Long Questions",
            )
        else:
            st.info("Assessment stage did not complete.")

    # ========================================================
    # REVIEW
    # ========================================================

    with tabs[3]:
        st.subheader("Quality Review")

        review = as_dict(context.review)

        if review:
            score = review.get("score", 0)

            if isinstance(score, (int, float)):
                score_text = f"{score}/100"
            else:
                score_text = as_text(score, "Not available")

            st.metric("Quality Score", score_text)

            review_status = as_text(
                review.get(
                    "overall_status",
                    "Not available",
                )
            )

            st.write(
                f"Status: **{review_status}**"
            )

            st.markdown("### Strengths")

            strengths = as_list(
                review.get("strengths", [])
            )

            if strengths:
                for item in strengths:
                    st.write(f"• {as_text(item)}")
            else:
                st.caption("No strengths were returned.")

            st.markdown("### Issues")

            issues = as_list(
                review.get("issues", [])
            )

            if issues:
                for raw_issue in issues:
                    issue = as_dict(raw_issue)

                    severity = as_text(
                        issue.get("severity", "unknown")
                    ).upper()

                    area = as_text(
                        issue.get("area", "")
                    )

                    problem = as_text(
                        issue.get("problem", "")
                    )

                    fix = as_text(
                        issue.get("recommended_fix", "")
                    )

                    st.warning(
                        f"{severity} — {area}"
                    )

                    if problem:
                        st.write(problem)

                    if fix:
                        st.caption(
                            f"Recommended fix: {fix}"
                        )
            else:
                st.caption("No issues were returned.")
        else:
            st.info("Review stage did not complete.")

    # ========================================================
    # FINAL PACK
    # ========================================================

    with tabs[4]:
        st.subheader("✨ Final Personalized Study Pack")

        final = as_dict(context.final_pack)

        if final:
            title = as_text(
                final.get("title", "Study Pack"),
                "Study Pack",
            )

            st.title(title)

            st.caption(
                f"Level: {as_text(learner_level)} | "
                f"Goal: {as_text(learning_goal)}"
            )

            st.markdown("## 📌 Summary")

            summary = as_text(
                final.get("summary", "")
            )

            if summary:
                st.write(summary)
            else:
                st.caption("No summary was returned.")

            st.markdown("## 🧠 Key Concepts")

            display_concepts(
                final.get("key_concepts", [])
            )

            st.markdown("## 🃏 Flashcards")

            display_flashcards(
                final.get("flashcards", [])
            )

            display_mcqs(
                final.get("mcqs", [])
            )

            display_question_section(
                final.get("short_questions", []),
                "## ✍️ Short Questions",
            )

            display_question_section(
                final.get("long_questions", []),
                "## 📖 Long Questions",
            )

            st.markdown("## 💡 Study Tips")

            tips = as_list(
                final.get("study_tips", [])
            )

            if tips:
                for tip in tips:
                    st.write(f"• {as_text(tip)}")
            else:
                st.caption("No study tips were returned.")

            st.download_button(
                "⬇️ Download Study Pack",
                data=json.dumps(
                    final,
                    indent=2,
                    ensure_ascii=False,
                ),
                file_name="study_pack.json",
                mime="application/json",
            )
        else:
            st.info(
                "Final refinement stage did not complete."
            )
