from fastapi import FastAPI, HTTPException
from routers import questionnaire, questions, my_submissions, dashboard
from contextlib import asynccontextmanager

#asynccontextmanager

app = FastAPI()

app.include_router(questionnaire.router)
app.include_router(questions.router)
app.include_router(my_submissions.router)
app.include_router(dashboard.router)













