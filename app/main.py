import os

import psycopg
from psycopg.rows import dict_row
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException

app = FastAPI()

DATABASE_URL = os.environ["DATABASE_URL"]


@app.get("/")
def root():
    return {"message": "Hello from Docker project"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/db")
def health_db():
    try:
        with psycopg.connect(DATABASE_URL, connect_timeout=3) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT current_database()")
                row = cursor.fetchone()
    except psycopg.Error:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable",
        ) from None

    return {"status": "ok", "database": row[0]}

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)


class TaskResponse(BaseModel):
    id: int
    title: str
    completed: bool


@app.post("/tasks", response_model=TaskResponse, status_code=201)
def create_task(task: TaskCreate):
    with psycopg.connect(
        DATABASE_URL,
        connect_timeout=3,
        row_factory=dict_row,
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO tasks (title)
                VALUES (%s)
                RETURNING id, title, completed
                """,
                (task.title,),
            )
            created_task = cursor.fetchone()

    return created_task


@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks():
    with psycopg.connect(
        DATABASE_URL,
        connect_timeout=3,
        row_factory=dict_row,
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, title, completed FROM tasks ORDER BY id"
            )
            tasks = cursor.fetchall()

    return tasks
