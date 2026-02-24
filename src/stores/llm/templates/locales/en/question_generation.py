from string import Template
from stores.llm.templates.locales.PromptTemplate import PromptTemplate
from stores.llm.templates.response_models import ListOf
from stores.llm.templates.response_models.questions import MCQ, ShortAnswer, TrueOrFalse

#### QUESTION GENERATION PROMPT ####

# Multiple Choice Question Generation
mcq_prompt = PromptTemplate(
  system=Template("\n".join([
    "Instructions:",
    "Based on the following main idea and its relevant passages, create $num_questions multiple-choice questions that require deep understanding, critical thinking, and detailed analysis. The questions should go beyond mere factual recall, involving higher-order thinking skills like analysis, synthesis, and evaluation.",
    'Do not use the phrases "main idea" or "passages" in the question statement. Instead, directly address the content or concepts described.',
    "Provide four answer choices for each question:",
    "- One correct answer.",
    "- Three plausible distractors that are contextually appropriate, relevant to the content, and reflect common misunderstandings or errors without introducing contradictory or irrelevant information.",
    "Note: The questions should be focused on one concept and not very long, DO NOT ask multiple questions in one.",
  ])),
  user=Template("\n".join([
    "Main Idea:",
    "$main_idea",
    "",
    "Passages:",
    "$passages",
  ])),
  response_model=ListOf[MCQ]
)

# True/False Question Generation
tf_prompt = PromptTemplate(
  system=Template("\n".join([
    "Instructions:",
    "Based on the following main idea and its relevant passages, create $num_questions true/false questions that test comprehension and understanding of key concepts.",
    'Do not use the phrases "main idea" or "passages" in the question statement. Instead, directly address the content or concepts described.',
    "For each question:",
    "- Create a clear, definitive statement (not ambiguous)",
    "- Provide the correct answer (true or false)",
    "- Include a brief explanation (2-3 sentences) of why the answer is correct",
    "- The statement should test understanding, not just memorization",
    "Note: The statements should be focused on one concept and not very long.",
  ])),
  user=Template("\n".join([
    "Main Idea:",
    "$main_idea",
    "",
    "Passages:",
    "$passages",
  ])),
  response_model=ListOf[TrueOrFalse]
)

# Short Answer Question Generation
short_answer_prompt = PromptTemplate(
  system=Template("\n".join([
    "Instructions:",
    "Based on the following main idea and its relevant passages, create $num_questions short-answer questions that require brief, focused responses demonstrating understanding.",
    'Do not use the phrases "main idea" or "passages" in the question statement. Instead, directly address the content or concepts described.',
    "For each question:",
    "- Create a clear question that requires a brief answer (1-3 sentences)",
    "- Provide an expected answer or key points that should be included",
    "- Include guidance on what constitutes a good answer",
    "- The question should test understanding and synthesis, not just recall",
    "Note: The questions should be focused and encourage concise, meaningful responses.",
  ])),
  user=Template("\n".join([
    "Main Idea:",
    "$main_idea",
    "",
    "Passages:",
    "$passages",
  ])),
  response_model=ListOf[ShortAnswer]
)