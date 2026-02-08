# Full Stack To-Do Application

A full-stack To-Do application with AI-powered chatbot assistance. Built with Python/FastAPI backend, Streamlit frontend, and powered by Groq's LLM API for intelligent task management.

## 🚀 Features

- **CRUD Operations**: Create, read, update, and delete tasks
- **Task Management**: Mark tasks as complete/incomplete
- **Bulk Operations**: Delete multiple tasks at once
- **AI-Powered Chatbot**: Context-aware assistant using Groq's LLM API
- **Real-time Updates**: Interactive UI with live task updates
- **Responsive Design**: Works across devices

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL (NeonDB)
- **ORM**: SQLAlchemy
- **AI Integration**: Groq API with Llama3 model
- **Environment Management**: python-dotenv

### Frontend
- **Framework**: Streamlit (Python)
- **API Communication**: requests library

### Dependencies
- fastapi
- uvicorn
- sqlalchemy
- python-dotenv
- openai
- groq
- psycopg2-binary

## 📁 Project Structure

```
Full_Stack-todo_app/
├── README.md
├── plan.md
├── test_backend.py
├── todos.db
├── backend/
│   ├── __init__.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── requirements.txt
│   ├── schemas.py
│   └── test_groq.py
├── frontend/
└── venv/
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL database (or NeonDB account)

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the backend directory with your configuration:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   DATABASE_URL=postgresql://username:password@host:port/database_name
   ```

5. Run the backend server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install Streamlit:
   ```bash
   pip install streamlit
   ```

4. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

## 🌐 API Endpoints

### Todo Management
- `GET /todos/` - Retrieve all todos
- `POST /todos/` - Create a new todo
- `GET /todos/{todo_id}` - Retrieve a specific todo
- `PUT /todos/{todo_id}` - Update a specific todo
- `DELETE /todos/{todo_id}` - Delete a specific todo
- `POST /todos/delete` - Bulk delete todos

### AI Chat
- `POST /chat` - Send message to AI assistant with task context

### Test Endpoint
- `GET /test` - Health check endpoint

## 🤖 AI Chatbot Features

The integrated AI assistant provides:
- Context-aware responses based on your current tasks
- Productivity suggestions
- Answers to questions about your task list
- Natural language processing for task-related queries

## 🧪 Testing

Run backend tests:
```bash
python test_backend.py
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the backend directory:

```
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=postgresql://username:password@host:port/database_name
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- Groq for the powerful AI API
- Streamlit for the easy-to-use UI framework
- SQLAlchemy for robust database management
