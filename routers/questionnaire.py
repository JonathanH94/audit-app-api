from sqlalchemy import text
from fastapi import APIRouter, HTTPException
from models import Questionnaire, Response, ResponseAnswer
from database import async_engine



router = APIRouter(prefix="/questionnaire", tags=["Questionnaire"])

"""
####################
#CREATE QUESTIONNAIRE
####################
"""

@router.post('/create_questionnaire', summary="Create a new questionnaire type")
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
#READ QUESTIONNAIRES
####################
"""
@router.get('/select_questionnaire/', summary="Select the questionnaire types")
async def select_questionnaire():

    async with async_engine.begin() as conn:
        result = await conn.execute(text("SELECT * FROM main.questionnaire"))
        dict_result = result.mappings().all()

        await async_engine.dispose()
        return dict_result

"""
####################
#READ QUESTIONNAIRE
####################
"""
@router.get('/select_questionnaire/{questionnaire_id}', summary="Select specific questionnaire type")
async def select_questionnaire(questionnaire_id: int):
    async with async_engine.begin() as conn:
        result = await conn.execute(text("SELECT * FROM main.questionnaire WHERE questionnaire_id = :questionnaire_id"),
                                    {"questionnaire_id": questionnaire_id})
        dict_result = result.mappings().all()

        await async_engine.dispose()
        return dict_result

"""
####################
#EDIT QUESTIONNAIRE
####################
"""

@router.put('/edit_questionnaire/{questionnaire_id}', summary="Edit a questionnaire type")
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