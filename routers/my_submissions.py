from sqlalchemy import text
from fastapi import APIRouter, HTTPException
from models import Questionnaire, Response, ResponseAnswer
from database import async_engine



router = APIRouter(prefix="/my_submissions", tags=["My Submissions"])


"""
####################
#MY SUBMISSIONS
####################
"""
@router.get('/{user_id}')
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
@router.get('/view_submission/{response_id}')
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
@router.put('/edit_submission/{response_id}')
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
#DELETE SUBMISSION
####################
"""

@router.delete('/delete_submission/{response_id}')
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