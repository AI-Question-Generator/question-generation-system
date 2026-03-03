from fastapi import APIRouter, status, Request
from fastapi.responses import JSONResponse
from helpers import get_settings, Settings
from models import ResponseSignal
from routes.schemes.question import BaseQuestion, MCQ, TrueOrFalse, ShortAnswer
from routes.schemes.generate import GenerationRequest, GenerationResponse, ProjectQuestionResponse

question_router = APIRouter(
  prefix="/api/v1/question",
  tags=['api_v1', 'question']
)

@question_router.post("/question/generate")
async def generate_question(request: Request, generation_request: GenerationRequest):
  
  # Validate the request
  if not generation_request.content:
    return JSONResponse(
      status_code=status.HTTP_400_BAD_REQUEST,
      content={"signal": ResponseSignal.FAIL, "message": "No projects provided"}
    )
    
  # Process each project's question generation requests
  response_content = []
    
  for project_request in generation_request.content:
    generated_questions = []
    
    # Generate questions for each question type request
    for question_type_request in project_request.questions:
      # Generate questions based on type and count
      for _ in range(question_type_request.count):
        # TODO: Implement actual question generation logic here
        # For now, create a placeholder question
        if question_type_request.type.value == "mcq":
          question = MCQ(
            question_statement="Sample MCQ question",
            explanation="Sample explanation",
            correct_answer="correct_answer",
            plausible_distractors=['choice1', 'choice2', 'choice3', 'choice4']
          )
        elif question_type_request.type.value == "tf":
          question = TrueOrFalse(
            question_statement="Sample True/False question",
            correct_answer="True",
            explanation="Sample explanation",
          )
        else:
          question = ShortAnswer(
            question_statement="Sample Short Answer question",
            explanation="Sample explanation",
            correct_answer="correct_answer",
          )

        generated_questions.append(question)
    
    # Add project questions to response
    project_response = ProjectQuestionResponse(
      project_id=project_request.project_id,
      questions=generated_questions
    )
    response_content.append(project_response)
    
  return GenerationResponse(
    content=response_content
  )