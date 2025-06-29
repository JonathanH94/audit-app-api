from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from contextlib import asynccontextmanager

async_engine = create_async_engine("sqlite+aiosqlite:///db.sqlite3")


app = FastAPI()

#@asynccontextmanager


class Questionnaire(BaseModel):
    name : str
    description: str

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

"""
####################
#SELECT AUDIT
####################
"""

@app.get('/select_audit')
async def select_audit():

    async with async_engine.begin() as conn:
        result = await conn.execute(text("SELECT * FROM main.questionnaire"))
        dict_result = result.mappings().all()

        await async_engine.dispose()
        return dict_result

"""
####################
#CREATE QUESTIONNAIRE
####################
"""

@app.post('/create_questionnaire')
async def create_questionnaire(questionnaire: Questionnaire):

    try:
        async with async_engine.begin() as conn:
            await conn.execute(text(f"insert into questionnaire (questionnaire_name, questionnaire_description, created_at, updated_at) VALUES (:name, :description, datetime('now'), datetime('now'))"),
                              {"name": questionnaire.name, "description": questionnaire.description})
            await async_engine.dispose()
            return {"message": f"success - questionnaire {questionnaire.name} added"}
    except Exception as e:
        await conn.rollback()
        print(e)
        raise HTTPException(status_code=500)

"""
####################
#SELECT QUESTIONS
####################
"""
@app.get('/select_questions/{questionnaire_id}')
async def select_questions(questionnaire_id: int):
    async with async_engine.begin() as conn:
        result = await conn.execute(text(f"SELECT question_id, question_name, question_type, ques.order_index, is_required, qc.category_id, qc.category_name, qc.order_index, q.questionnaire_id, q.questionnaire_name, q.is_active FROM question ques left join question_category qc on ques.category_id = qc.category_id left join questionnaire q on qc.questionnaire_id = q.questionnaire_id WHERE q.questionnaire_id = :questionnaire_id"),
                                    {"questionnaire_id": questionnaire_id})

        dict_result = result.mappings().all()
        await async_engine.dispose()
        return dict_result

"""
####################
#CREATE AUDIT
####################
"""
@app.post('/create_audit/{questionnaire_id}')
async def create_audit(response: Response, questionnaire_id: int):
    async with async_engine.begin() as conn:

        await conn.execute(text("INSERT INTO response (questionnaire_id, user_id, team_id, completed_date, created_at, updated_at) VALUES (:questionnaire_id, :user_id, :team_id, :completed_date, datetime('now'), datetime('now'))"),
                           {"questionnaire_id": response.questionnaire_id, "user_id": response.user_id, "team_id": response.team_id, "completed_date": response.completed_date})

        result = await conn.execute(text("select last_insert_rowid()"))
        response_id = result.scalar()


        for item in response.response_answer:
            await conn.execute(text("insert into response_answer (response_id, question_id, answer, created_at, updated_at) VALUES (:response_id, :question_id, :answer, datetime('now'), datetime('now'))"),
                               {"response_id": response_id, "question_id": item.question_id, "answer": item.answer})

        await async_engine.dispose()
    return {"success": "audit received"}


"""
####################
#DELETE SUBMISSION
####################
"""

@app.delete('/delete_submission/{response_id}')
async def delete_submission(response_id: int):
    async with async_engine.begin() as conn:
        await conn.execute(text("PRAGMA foreign_keys = ON"))
        await conn.execute(text("DELETE FROM response WHERE response_id = :response_id"), {"response_id": response_id})

        await async_engine.dispose()

    return {"submission deleted": response_id}
