from pydantic import BaseModel, Field
from datetime import datetime


class Questionnaire(BaseModel):
    name : str = Field(serialization_alias="questionnaire_name")
    description: str = Field(serialization_alias="questionnaire_description")
    is_active: bool = Field(default=1)

class ResponseAnswer(BaseModel):
    question_id: int
    question_name: str
    answer: str


class Response(BaseModel):
    questionnaire_id: int
    user_id: int
    team_id: int
    completed_date: datetime
    response_answer: list[ResponseAnswer]