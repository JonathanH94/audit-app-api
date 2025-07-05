from sqlalchemy import text
from fastapi import APIRouter, HTTPException
from models import Questionnaire, Response, ResponseAnswer
from database import async_engine



router = APIRouter(prefix="/question", tags=["Question"])


"""
####################
#SELECT QUESTIONS
####################
"""
@router.get('/select_questions/{questionnaire_id}', summary="Select questions linked to a questionnaire")
async def select_questions(questionnaire_id: int):
    async with async_engine.begin() as conn:
        result = await conn.execute(text(f"SELECT question_id, question_name, question_type, ques.order_index, is_required, qc.category_id, qc.category_name, qc.order_index, q.questionnaire_id, q.questionnaire_name, q.is_active FROM question ques left join question_category qc on ques.category_id = qc.category_id left join questionnaire q on qc.questionnaire_id = q.questionnaire_id WHERE q.questionnaire_id = :questionnaire_id"),
                                    {"questionnaire_id": questionnaire_id})

        dict_result = result.mappings().all()
        await async_engine.dispose()
        return dict_result