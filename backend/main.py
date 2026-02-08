# main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from dotenv import load_dotenv
import os
from urllib.parse import urlparse

import models
import schemas
from database import SessionLocal, engine

from openai import OpenAI

# =======================
# ENV + GROQ CLIENT
# =======================
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

print(f"GROQ_API_KEY loaded: {'Yes' if GROQ_API_KEY else 'No'}")
print(f"DATABASE_URL loaded: {'Yes' if DATABASE_URL else 'No'}")

if not GROQ_API_KEY:
    raise RuntimeError("❌ GROQ_API_KEY not found in .env file")
if not DATABASE_URL:
    raise RuntimeError("❌ DATABASE_URL not found in .env file")

# Initialize Groq client
client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# =======================
# DB INIT
# =======================
models.Base.metadata.create_all(bind=engine)

# =======================
# FASTAPI APP
# =======================
app = FastAPI(title="Todo App with AI Chat", version="1.0.0")

# =======================
# CORS
# =======================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =======================
# DB DEPENDENCY
# =======================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =======================
# TEST ROUTE
# =======================
@app.get("/test")
def test():
    return {"message": "Backend is working ✅"}

# =======================
# TODO CRUD ROUTES
# =======================
@app.post("/todos/", response_model=schemas.Todo)
def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    try:
        db_todo = models.Todo(title=todo.title, description=todo.description)
        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)
        return schemas.Todo.from_orm(db_todo)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/todos/", response_model=List[schemas.Todo])
def read_todos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Todo).offset(skip).limit(limit).all()

@app.get("/todos/{todo_id}", response_model=schemas.Todo)
def read_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.put("/todos/{todo_id}", response_model=schemas.Todo)
def update_todo(todo_id: int, todo: schemas.TodoUpdate, db: Session = Depends(get_db)):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if todo.title is not None:
        db_todo.title = todo.title
    if todo.description is not None:
        db_todo.description = todo.description
    if todo.completed is not None:
        db_todo.completed = todo.completed
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.delete("/todos/{todo_id}", response_model=schemas.Todo)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(db_todo)
    db.commit()
    return db_todo

@app.post("/todos/delete")
def bulk_delete(todo_delete: schemas.TodoDelete, db: Session = Depends(get_db)):
    num_deleted = (
        db.query(models.Todo)
        .filter(models.Todo.id.in_(todo_delete.ids))
        .delete(synchronize_session=False)
    )
    db.commit()
    return {"message": f"{num_deleted} todos deleted successfully"}

# =======================
# AI CHAT ROUTE (GROQ)
# =======================
@app.post("/chat")
def chat_with_ai(request: schemas.ChatRequest, db: Session = Depends(get_db)):
    if not GROQ_API_KEY:
        # Return a helpful message if no API key is configured
        return {"reply": "AI assistant is not configured. Please add a valid GROQ API key to the .env file."}

    try:
        # Get all todos to provide context to the AI
        all_todos = db.query(models.Todo).all()

        # Format todos for AI context
        todos_context = ""
        if all_todos:
            pending_todos = [t for t in all_todos if not t.completed]
            completed_todos = [t for t in all_todos if t.completed]

            todos_context += f"\n\nUSER'S CURRENT TASKS:\n"
            todos_context += f"- Total tasks: {len(all_todos)}\n"
            todos_context += f"- Pending tasks: {len(pending_todos)}\n"
            todos_context += f"- Completed tasks: {len(completed_todos)}\n"

            if pending_todos:
                todos_context += "\nPENDING TASKS:\n"
                for i, todo in enumerate(pending_todos[:5], 1):  # Limit to first 5 pending tasks
                    todos_context += f"  {i}. {todo.title}\n"

            if completed_todos:
                todos_context += "\nCOMPLETED TASKS:\n"
                for i, todo in enumerate(completed_todos[:5], 1):  # Limit to first 5 completed tasks
                    todos_context += f"  {i}. {todo.title}\n"
        else:
            todos_context += "\n\nUSER HAS NO TASKS YET."

        # Enhanced system message with context
        system_message = f"""You are a helpful and friendly AI assistant for a todo application.
        Your name is ProTo-Do AI Assistant.
        You can help users manage their tasks, suggest productivity tips, and answer questions about their todo list.
        {todos_context}

        Be concise, helpful, and friendly in your responses.
        If asked about specific tasks, refer to the task list provided above.
        If the user wants to add/update/delete tasks, guide them to use the app interface."""

        response = client.chat.completions.create(
            model="llama3-8b-8192",  # Updated to use a reliable Groq model
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": request.message}
            ],
            temperature=0.7,
            max_tokens=500
        )

        # Safely return content
        reply = response.choices[0].message.content if response.choices else "I couldn't generate a response. Please try again."
        return {"reply": reply}

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"AI Service Error: {str(e)}")
        print(f"Full traceback: {error_details}")
        
        # Return a helpful fallback response instead of throwing an exception
        fallback_responses = {
            "auth_error": "⚠️ AI service authentication failed. Please check your API key in the .env file.",
            "network_error": "📡 Unable to connect to AI service. Please check your internet connection.",
            "rate_limit": "⏳ Rate limit exceeded. Please try again later.",
            "model_error": "🔧 Model not found. Please check the model name in the backend configuration.",
            "general_error": f"🤖 AI service temporarily unavailable: {str(e)[:100]}..."
        }
        
        error_msg = str(e).lower()
        if "invalid_api_key" in error_msg or "authentication" in error_msg or "401" in error_msg:
            return {"reply": fallback_responses["auth_error"]}
        elif "rate_limit" in error_msg or "429" in error_msg:
            return {"reply": fallback_responses["rate_limit"]}
        elif "not found" in error_msg or "does not exist" in error_msg:
            return {"reply": fallback_responses["model_error"]}
        else:
            return {"reply": fallback_responses["general_error"]}
