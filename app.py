"""
StudySpark AI - Main Streamlit Application

Run:
    streamlit run app.py

Project structure:
    app.py          -> Streamlit UI + workflow orchestration
    workflow.py     -> Multi-stage AI workflow
    ai_service.py   -> Groq/OpenAI-compatible AI service
    requirements.txt
"""

import json
import os

import streamlit as st

from workflow import (
    STAGES,
    create_context,
    run_stage,
)


# ------------------------------------------------------------
# Page configuration
# ------------------------------------------------------------

st.set_page_config(
    page_title="StudySpark AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ------------------------------------------------------------
# Styling
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# Header
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------

with st.sidebar:
    st.header("⚙️ Study Settings")

    api_key = st.text_input(
        "Groq API Key",
        value=os.getenv("GROQ_API_KEY", ""),
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


# ------------------------------------------------------------
# User input
# ------------------------------------------------------------

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

    for number, name, description in [
        ("1", "🧭 Planning", "Creates the learning blueprint"),
        ("2", "📚 Content", "Generates learning material"),
        ("3", "📝 Assessment", "Creates questions"),
        ("4", "🔎 Review", "Checks quality"),
        ("5", "✨ Refinement", "Creates final pack"),
    ]:
        st.markdown(
            f"""
            <div class="stage-card">
                <b>{number}. {name}</b><br>
                <small>{description}</small>
            </div>
            """,
            unsafe_allow_html=True,
        )


generate = st.button(
    "🚀 Generate Study Pack",
    type="primary",
    use_container_width=True,
)


# ------------------------------------------------------------
# Run workflow
# ------------------------------------------------------------

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
            context.record_error(stage_name, str(exc))

            st.error(
                f"❌ {stage_name} failed: {exc}"
            )

            break

        progress.progress((index + 1) / len(STAGES))

    status.success("Workflow completed.")

    st.session_state["context"] = context


# ------------------------------------------------------------
# Display workflow results
# ------------------------------------------------------------

context = st.session_state.get("context")

if context:

    st.divider()

    st.header("🤖 Workflow Status")

    columns = st.columns(5)

    for index, stage_name in enumerate(STAGES):
        with columns[index]:

            if stage_name in context.completed_stages:
                st.success(
                    f"✓ {stage_name}"
                )
            else:
                st.warning(
                    f"Not completed: {stage_name}"
                )

    if context.errors:
        st.warning("Some stages encountered errors.")

        for error in context.errors:
            st.error(
                f"{error['stage']}: {error['message']}"
            )

    # --------------------------------------------------------
    # Result tabs
    # --------------------------------------------------------

    tabs = st.tabs(
        [
            "🧭 Plan",
            "📚 Content",
            "📝 Assessment",
            "🔎 Review",
            "✨ Final Pack",
        ]
    )

    with tabs[0]:

        st.subheader("Learning Plan")

        if context.plan:
            st.json(context.plan)
        else:
            st.info("Planning stage did not complete.")

    with tabs[1]:

        st.subheader("Generated Content")

        if context.content:

            st.write(
                context.content.get(
                    "summary",
                    "",
                )
            )

            st.markdown("### 🧠 Key Concepts")

            for item in context.content.get(
                "key_concepts",
                [],
            ):

                if isinstance(item, dict):

                    st.markdown(
                        f"**{item.get('concept', '')}**"
                    )

                    st.write(
                        item.get(
                            "explanation",
                            "",
                        )
                    )

                else:
                    st.write(item)

            st.markdown("### 🃏 Flashcards")

            for index, card in enumerate(
                context.content.get(
                    "flashcards",
                    [],
                ),
                1,
            ):

                with st.expander(
                    f"Card {index}: {card.get('question', '')}"
                ):

                    st.write(
                        card.get(
                            "answer",
                            "",
                        )
                    )

        else:
            st.info("Content stage did not complete.")

    with tabs[2]:

        st.subheader("Assessment")

        if context.assessment:

            st.markdown("### ❓ MCQs")

            for index, mcq in enumerate(
                context.assessment.get(
                    "mcqs",
                    [],
                ),
                1,
            ):

                st.markdown(
                    f"**{index}. {mcq.get('question', '')}**"
                )

                for key, value in mcq.get(
                    "options",
                    {},
                ).items():

                    st.write(
                        f"**{key}.** {value}"
                    )

                with st.expander("Show answer"):

                    st.success(
                        str(
                            mcq.get(
                                "answer",
                                "",
                            )
                        )
                    )

                    st.write(
                        mcq.get(
                            "explanation",
                            "",
                        )
                    )

            st.markdown("### ✍️ Short Questions")

            for item in context.assessment.get(
                "short_questions",
                [],
            ):

                with st.expander(
                    item.get(
                        "question",
                        "",
                    )
                ):

                    st.write(
                        item.get(
                            "answer",
                            "",
                        )
                    )

            st.markdown("### 📖 Long Questions")

            for item in context.assessment.get(
                "long_questions",
                [],
            ):

                with st.expander(
                    item.get(
                        "question",
                        "",
                    )
                ):

                    st.write(
                        item.get(
                            "answer",
                            "",
                        )
                    )

        else:
            st.info("Assessment stage did not complete.")

    with tabs[3]:

        st.subheader("Quality Review")

        if context.review:

            score = context.review.get(
                "score",
                0,
            )

            st.metric(
                "Quality Score",
                f"{score}/100",
            )

            st.write(
                f"Status: **{context.review.get('overall_status', '')}**"
            )

            st.markdown("### Strengths")

            for item in context.review.get(
                "strengths",
                [],
            ):
                st.write(f"• {item}")

            st.markdown("### Issues")

            for issue in context.review.get(
                "issues",
                [],
            ):

                st.warning(
                    f"{issue.get('severity', '').upper()} — "
                    f"{issue.get('area', '')}"
                )

                st.write(
                    issue.get(
                        "problem",
                        "",
                    )
                )

                st.caption(
                    "Recommended fix: "
                    + issue.get(
                        "recommended_fix",
                        "",
                    )
                )

        else:
            st.info("Review stage did not complete.")

    with tabs[4]:

        st.subheader("✨ Final Personalized Study Pack")

        if context.final_pack:

            final = context.final_pack

            st.title(
                final.get(
                    "title",
                    "Study Pack",
                )
            )

            st.caption(
                f"Level: {learner_level} | "
                f"Goal: {learning_goal}"
            )

            st.markdown("## 📌 Summary")

            st.write(
                final.get(
                    "summary",
                    "",
                )
            )

            st.markdown("## 🧠 Key Concepts")

            for item in final.get(
                "key_concepts",
                [],
            ):

                if isinstance(item, dict):

                    st.markdown(
                        f"**{item.get('concept', '')}**"
                    )

                    st.write(
                        item.get(
                            "explanation",
                            "",
                        )
                    )

                else:
                    st.write(item)

            st.markdown("## 🃏 Flashcards")

            for index, card in enumerate(
                final.get(
                    "flashcards",
                    [],
                ),
                1,
            ):

                with st.expander(
                    f"Card {index}: {card.get('question', '')}"
                ):

                    st.write(
                        card.get(
                            "answer",
                            "",
                        )
                    )

            st.markdown("## ❓ MCQs")

            for index, mcq in enumerate(
                final.get(
                    "mcqs",
                    [],
                ),
                1,
            ):

                st.markdown(
                    f"**{index}. {mcq.get('question', '')}**"
                )

                for key, value in mcq.get(
                    "options",
                    {},
                ).items():

                    st.write(
                        f"**{key}.** {value}"
                    )

                with st.expander("Show answer"):

                    st.success(
                        str(
                            mcq.get(
                                "answer",
                                "",
                            )
                        )
                    )

                    st.write(
                        mcq.get(
                            "explanation",
                            "",
                        )
                    )

            st.markdown("## ✍️ Short Questions")

            for item in final.get(
                "short_questions",
                [],
            ):

                with st.expander(
                    item.get(
                        "question",
                        "",
                    )
                ):

                    st.write(
                        item.get(
                            "answer",
                            "",
                        )
                    )

            st.markdown("## 📖 Long Questions")

            for item in final.get(
                "long_questions",
                [],
            ):

                with st.expander(
                    item.get(
                        "question",
                        "",
                    )
                ):

                    st.write(
                        item.get(
                            "answer",
                            "",
                        )
                    )

            st.markdown("## 💡 Study Tips")

            for tip in final.get(
                "study_tips",
                [],
            ):
                st.write(f"• {tip}")

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
            st.info("Final refinement stage did not complete.")
