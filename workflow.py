"""
StudySpark AI - Workflow Engine

This file contains:
- Shared workflow context
- Five AI stages
- Stage orchestration
- Error recording

The UI stays in app.py.
The AI API call stays in ai_service.py.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List

from ai_service import ask_ai


# ============================================================
# Shared Context
# ============================================================

@dataclass
class WorkflowContext:

    topic: str
    source_text: str
    learner_level: str
    learning_goal: str
    pack_type: str
    question_count: int

    plan: Dict[str, Any] = field(default_factory=dict)
    content: Dict[str, Any] = field(default_factory=dict)
    assessment: Dict[str, Any] = field(default_factory=dict)
    review: Dict[str, Any] = field(default_factory=dict)
    final_pack: Dict[str, Any] = field(default_factory=dict)

    completed_stages: List[str] = field(default_factory=list)

    errors: List[Dict[str, str]] = field(default_factory=list)

    def record_error(
        self,
        stage: str,
        message: str,
    ):
        self.errors.append(
            {
                "stage": stage,
                "message": message,
            }
        )


def create_context(
    topic: str,
    source_text: str,
    learner_level: str,
    learning_goal: str,
    pack_type: str,
    question_count: int,
) -> WorkflowContext:

    return WorkflowContext(
        topic=topic.strip(),
        source_text=source_text.strip(),
        learner_level=learner_level,
        learning_goal=learning_goal,
        pack_type=pack_type,
        question_count=question_count,
    )


# ============================================================
# Stage 1 — Planning
# ============================================================

def planning_stage(
    ctx: WorkflowContext,
    api_key: str,
):

    prompt = f"""
Create a personalized study plan.

Student level:
{ctx.learner_level}

Learning goal:
{ctx.learning_goal}

Topic:
{ctx.topic}

Study material:
{ctx.source_text or "No material supplied. Use general knowledge."}

Return ONLY JSON:

{{
  "learning_objectives": [],
  "key_topics": [],
  "recommended_sequence": [],
  "difficulty_strategy": "",
  "content_requirements": [],
  "assessment_requirements": []
}}
"""

    ctx.plan = ask_ai(
        api_key=api_key,
        system_prompt=(
            "You are an expert instructional designer."
        ),
        user_prompt=prompt,
    )

    ctx.completed_stages.append("Planning")


# ============================================================
# Stage 2 — Content Generation
# ============================================================

def content_stage(
    ctx: WorkflowContext,
    api_key: str,
):

    prompt = f"""
Generate study content using this learning plan.

Topic:
{ctx.topic}

Student level:
{ctx.learner_level}

Learning goal:
{ctx.learning_goal}

PLAN:
{ctx.plan}

SOURCE MATERIAL:
{ctx.source_text or "No source material supplied."}

Return ONLY JSON:

{{
  "summary": "",
  "key_concepts": [
    {{
      "concept": "",
      "explanation": ""
    }}
  ],
  "examples": [
    {{
      "concept": "",
      "example": ""
    }}
  ],
  "flashcards": [
    {{
      "question": "",
      "answer": ""
    }}
  ]
}}

The content must follow the learning objectives.
"""

    ctx.content = ask_ai(
        api_key=api_key,
        system_prompt=(
            "You are an expert educational content creator."
        ),
        user_prompt=prompt,
    )

    ctx.completed_stages.append("Content Generation")


# ============================================================
# Stage 3 — Assessment
# ============================================================

def assessment_stage(
    ctx: WorkflowContext,
    api_key: str,
):

    prompt = f"""
Create an assessment from the plan and generated content.

Topic:
{ctx.topic}

Student level:
{ctx.learner_level}

Question count:
{ctx.question_count}

PLAN:
{ctx.plan}

CONTENT:
{ctx.content}

Return ONLY JSON:

{{
  "mcqs": [
    {{
      "question": "",
      "options": {{
        "A": "",
        "B": "",
        "C": "",
        "D": ""
      }},
      "answer": "A",
      "explanation": ""
    }}
  ],
  "short_questions": [
    {{
      "question": "",
      "answer": ""
    }}
  ],
  "long_questions": [
    {{
      "question": "",
      "answer": ""
    }}
  ]
}}

Questions must test the actual generated content.
"""

    ctx.assessment = ask_ai(
        api_key=api_key,
        system_prompt=(
            "You are an expert educational assessment designer."
        ),
        user_prompt=prompt,
    )

    ctx.completed_stages.append("Assessment")


# ============================================================
# Stage 4 — Review
# ============================================================

def review_stage(
    ctx: WorkflowContext,
    api_key: str,
):

    prompt = f"""
Review this study pack.

PLAN:
{ctx.plan}

CONTENT:
{ctx.content}

ASSESSMENT:
{ctx.assessment}

Check:

- factual consistency
- learning-objective alignment
- important-topic coverage
- difficulty
- MCQ correctness
- ambiguity
- duplicate questions
- missing explanations
- unsupported claims

Return ONLY JSON:

{{
  "overall_status": "pass or needs_revision",
  "score": 0,
  "strengths": [],
  "issues": [
    {{
      "severity": "high|medium|low",
      "area": "",
      "problem": "",
      "recommended_fix": ""
    }}
  ],
  "revision_instructions": []
}}
"""

    ctx.review = ask_ai(
        api_key=api_key,
        system_prompt=(
            "You are a strict educational quality reviewer."
        ),
        user_prompt=prompt,
    )

    ctx.completed_stages.append("Review")


# ============================================================
# Stage 5 — Refinement
# ============================================================

def refinement_stage(
    ctx: WorkflowContext,
    api_key: str,
):

    prompt = f"""
Create the final student-ready study pack.

PLAN:
{ctx.plan}

CONTENT:
{ctx.content}

ASSESSMENT:
{ctx.assessment}

REVIEW:
{ctx.review}

Apply the important fixes identified by the reviewer.

Return ONLY JSON:

{{
  "title": "",
  "summary": "",
  "key_concepts": [],
  "examples": [],
  "flashcards": [],
  "mcqs": [],
  "short_questions": [],
  "long_questions": [],
  "study_tips": [],
  "review_status": "",
  "quality_score": 0
}}

Do not mention internal workflow details.
"""

    ctx.final_pack = ask_ai(
        api_key=api_key,
        system_prompt=(
            "You are the final educational editor. "
            "Produce accurate, clear, student-ready material."
        ),
        user_prompt=prompt,
    )

    ctx.completed_stages.append("Refinement")


# ============================================================
# Stage Registry
# ============================================================

STAGES = [
    "Planning",
    "Content Generation",
    "Assessment",
    "Review",
    "Refinement",
]


# ============================================================
# Stage Runner
# ============================================================

def run_stage(
    context: WorkflowContext,
    stage_name: str,
    api_key: str,
) -> WorkflowContext:

    stage_functions = {
        "Planning": planning_stage,
        "Content Generation": content_stage,
        "Assessment": assessment_stage,
        "Review": review_stage,
        "Refinement": refinement_stage,
    }

    function = stage_functions.get(stage_name)

    if function is None:
        raise ValueError(
            f"Unknown workflow stage: {stage_name}"
        )

    function(
        context,
        api_key,
    )

    return context
