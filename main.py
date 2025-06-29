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
#CREATE QUESTIONS
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




