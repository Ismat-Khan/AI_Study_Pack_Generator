from dataclasses import dataclass, field
from typing import Any, Dict, List
from ai_service import ask_ai

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
    def record_error(self, stage: str, message: str):
        self.errors.append({"stage": stage, "message": message})

def create_context(topic, source_text, learner_level, learning_goal, pack_type, question_count):
    return WorkflowContext(topic.strip(), source_text.strip(), learner_level, learning_goal, pack_type, question_count)

def planning_stage(ctx, api_key):
    prompt=f'''Create a concise personalized study plan.\nTopic: {ctx.topic}\nStudent level: {ctx.learner_level}\nLearning goal: {ctx.learning_goal}\nStudy material: {ctx.source_text or "No material supplied."}\nReturn ONLY JSON with keys learning_objectives, key_topics, recommended_sequence, difficulty_strategy, content_requirements, assessment_requirements. Keep arrays concise.'''
    ctx.plan=ask_ai(api_key,"You are an expert instructional designer. Return valid JSON only.",prompt); ctx.completed_stages.append("Planning")

def content_stage(ctx, api_key):
    prompt=f'''Generate concise study content.\nTopic: {ctx.topic}\nStudent level: {ctx.learner_level}\nLearning goal: {ctx.learning_goal}\nLearning plan: {ctx.plan}\nSource material: {ctx.source_text or "No source material supplied."}\nReturn ONLY JSON with exactly these keys: summary, key_concepts, examples, flashcards. key_concepts must contain 4 to 6 objects with concept and explanation. examples 2 to 4 objects with concept and example. flashcards 4 to 6 objects with question and answer. Keep explanations short. No Markdown or text outside JSON.'''
    ctx.content=ask_ai(api_key,"You are an expert educational content creator. Output JSON only.",prompt); ctx.completed_stages.append("Content Generation")

def assessment_stage(ctx, api_key):
    prompt=f'''Create an assessment from the study plan and generated content.\nTopic: {ctx.topic}\nStudent level: {ctx.learner_level}\nQuestion count: {ctx.question_count}\nPLAN: {ctx.plan}\nCONTENT: {ctx.content}\nReturn ONLY JSON with keys mcqs, short_questions, long_questions. Create up to {ctx.question_count} in each section. Keep answers concise.'''
    ctx.assessment=ask_ai(api_key,"You are an expert educational assessment designer. Output JSON only.",prompt); ctx.completed_stages.append("Assessment")

def review_stage(ctx, api_key):
    prompt=f'''Review this study pack for factual consistency, objective alignment, coverage, difficulty, MCQ correctness, ambiguity, duplicates, and missing explanations. PLAN: {ctx.plan}\nCONTENT: {ctx.content}\nASSESSMENT: {ctx.assessment}\nReturn ONLY JSON with keys overall_status, score, strengths, issues, revision_instructions. Keep it concise.'''
    ctx.review=ask_ai(api_key,"You are a strict educational quality reviewer. Output JSON only.",prompt); ctx.completed_stages.append("Review")

def refinement_stage(ctx, api_key):
    prompt=f'''Create the final student-ready study pack. PLAN: {ctx.plan}\nCONTENT: {ctx.content}\nASSESSMENT: {ctx.assessment}\nREVIEW: {ctx.review}\nReturn ONLY JSON with keys title, summary, key_concepts, examples, flashcards, mcqs, short_questions, long_questions, study_tips, review_status, quality_score. Keep content concise. Do not mention internal workflow details.'''
    ctx.final_pack=ask_ai(api_key,"You are the final educational editor. Output JSON only.",prompt); ctx.completed_stages.append("Refinement")

STAGES=["Planning","Content Generation","Assessment","Review","Refinement"]

def run_stage(context, stage_name, api_key):
    funcs={"Planning":planning_stage,"Content Generation":content_stage,"Assessment":assessment_stage,"Review":review_stage,"Refinement":refinement_stage}
    if stage_name not in funcs: raise ValueError(f"Unknown workflow stage: {stage_name}")
    funcs[stage_name](context,api_key); return context
