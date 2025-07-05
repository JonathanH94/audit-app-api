from sqlalchemy import text
from fastapi import APIRouter, HTTPException
from models import Questionnaire, Response, ResponseAnswer
from database import async_engine



router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

"""
####################
#CREATE SUBMISSION
####################
"""
@router.post('/create_submission/{questionnaire_id}')
async def create_submission(response: Response, questionnaire_id: int):

    try:
        async with async_engine.begin() as conn:

            await conn.execute(text("INSERT INTO response (questionnaire_id, user_id, team_id, completed_date, created_at, updated_at) VALUES (:questionnaire_id, :user_id, :team_id, :completed_date, datetime('now'), datetime('now'))"),
                               {"questionnaire_id": response.questionnaire_id, "user_id": response.user_id, "team_id": response.team_id, "completed_date": response.completed_date})

            result = await conn.execute(text("select last_insert_rowid()"))
            response_id = result.scalar()


            for item in response.response_answer:
                await conn.execute(text("insert into response_answer (response_id, question_id, answer, created_at, updated_at) VALUES (:response_id, :question_id, :answer, datetime('now'), datetime('now'))"),
                                   {"response_id": response_id, "question_id": item.question_id, "answer": item.answer})

            await async_engine.dispose()
        return {"success": "audit submitted"}
    except Exception as e:
        await conn.rollback()
        raise HTTPException(status_code=500)