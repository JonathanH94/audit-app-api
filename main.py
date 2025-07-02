from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from contextlib import asynccontextmanager

async_engine = create_async_engine("sqlite+aiosqlite:///db.sqlite3")


app = FastAPI()

#asynccontextmanager


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

"""
####################
#READ QUESTIONNAIRE
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
#CREATE SUBMISSION
####################
"""
@app.post('/create_submission/{questionnaire_id}')
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


"""
####################
#DELETE SUBMISSION
####################
"""

@app.delete('/delete_submission/{response_id}')
async def delete_submission(response_id: int):
    try:
        async with async_engine.begin() as conn:
            await conn.execute(text("PRAGMA foreign_keys = ON"))
            await conn.execute(text("DELETE FROM response WHERE response_id = :response_id"), {"response_id": response_id})

            await async_engine.dispose()

        return {"submission deleted": response_id}
    except Exception:
        await conn.rollback()
        raise HTTPException(status_code=500)


"""
####################
#MY SUBMISSIONS
####################
"""
@app.get('/my_submissions/{user_id}')
async def my_submissions(user_id: int):
    async with async_engine.begin() as conn:
       result = await conn.execute(text("SELECT r.response_id, q.questionnaire_name, t.team_name, r.completed_date, r.updated_at FROM response r left join questionnaire q on r.questionnaire_id = q.questionnaire_id left join team t on r.team_id = t.team_id where r.user_id = :user_id"),
                           {"user_id": user_id})
       dict_result = result.mappings().all()
       await async_engine.dispose()
       return dict_result


"""
####################
#VIEW SUBMISSION
####################
"""
@app.get('/my_submissions/view_submission/{response_id}')
async def view_submission(response_id: int):
    async with async_engine.begin() as conn:
       result = await conn.execute(text("SELECT ra.response_answer_id, q2.questionnaire_name, t.team_name, ra.question_id, qc.category_name, q.question_name, ra.answer, ra.created_at, ra.updated_at "
                                        "FROM response_answer ra inner join response r on ra.response_id = r.response_id left join questionnaire q2 on r.questionnaire_id = q2.questionnaire_id "
                                        "left join team t on r.team_id = t.team_id  left join question q on ra.question_id = q.question_id left join question_category qc on q.category_id = qc.category_id where ra.response_id = :response_id"),
                           {"response_id": response_id})
       dict_result = result.mappings().all()

       return dict_result
"""
####################
#EDIT SUBMISSION
####################
"""
@app.put('/edit_submission/{response_id}')
async def edit_submission(response: Response, response_id: int):

    try:
        ##RESPONSE BLOCK###
        async with async_engine.begin() as conn:
           response_result = await conn.execute(text("SELECT r.team_id, r.completed_date FROM response r left join team t on r.team_id = t.team_id where r.response_id = :response_id"),
                               {"response_id": response_id})
           current_response = response_result.mappings().all()
           current_data = current_response[0]

           new_data = {"team_id": response.team_id, "completed_date": response.completed_date}
           changes = {key: new_value for key, new_value in new_data.items() if key in current_data and current_data[key] != new_value }

           ##RESPONSE ANSWER BLOCK
           ra_result = await conn.execute(text("SELECT ra.response_answer_id, ra.response_id, ra.question_id, ra.answer FROM response_answer ra where ra.response_id = :response_id"),
                                        {"response_id": response_id})
           current_ra = ra_result.mappings().all()

          ##CHANE LOGIC
           changes_ra = []

           current_ra_dict = {item['question_id']: item for item in current_ra}

           for item in response.response_answer:
               if item.question_id in current_ra_dict:
                   if item.answer != current_ra_dict[item.question_id]['answer']:
                       changes_ra.append({"response_answer_id": current_ra_dict[item.question_id]['response_answer_id'],
                                          "question_id": current_ra_dict[item.question_id]['question_id'],
                                          "answer": item.answer})

           ##RESPONSE SQL STATEMENT

           if changes:
               set_parts = [f"{key} = :{key}" for key, value in changes.items()]
               set_clause = ', '.join(set_parts)
               param_dict = changes
               param_dict['response_id'] = response_id

               query = f"UPDATE response SET {set_clause}, updated_at = datetime('now') WHERE response_id = :response_id"
               print(query)
               print(param_dict)
               await conn.execute(text(query), param_dict)

           ##RESPONSE ANSWER SQL STATEMENT
           if changes_ra:
               for item in changes_ra:
                   query_ra = "UPDATE response_answer SET answer = :answer, updated_at = datetime('now')  WHERE response_answer_id = :response_answer_id"
                   await conn.execute(text(query_ra), {"answer": item['answer'], "response_answer_id": item['response_answer_id']})
        await async_engine.dispose()
        return "Successfully updated"
    except Exception as e:
        await conn.rollback()
        await async_engine.dispose()
        raise HTTPException(status_code=500)

"""
####################
#EDIT QUESTIONNAIRE
####################
"""

@app.put('/edit_questionnaire/{questionnaire_id}')
async def edit_questionnaire(questionnaire: Questionnaire, questionnaire_id):

    try:
        async with async_engine.begin() as conn:
            result = await conn.execute(text("SELECT questionnaire_id, questionnaire_name, questionnaire_description, is_active FROM questionnaire WHERE questionnaire_id = :questionnaire_id"),
                               {"questionnaire_id": questionnaire_id})
            result_mapped = result.mappings().all()

            old_data = result_mapped[0]
            new_data = questionnaire.model_dump(by_alias=True)


            changes = {key: new_value for key, new_value in new_data.items() if key in old_data and old_data[key] != new_value}
            if changes:
                changes['questionnaire_id'] = questionnaire_id

                set_clause = [f"{key} = :{key}" for key, value in changes.items()]
                set_parts = ", ".join(set_clause)

                query = f"UPDATE questionnaire SET {set_parts}, updated_at = datetime('now') WHERE questionnaire_id = :questionnaire_id"

                await conn.execute(text(query), changes)
                await async_engine.dispose()
                return "successfully updated"
            else:
                return "No changes to update"
    except:
        await conn.rollback()
        await async_engine.dispose()
        raise HTTPException(status_code=500)



