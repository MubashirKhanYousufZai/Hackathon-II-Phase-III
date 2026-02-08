"""
Simple test script to verify backend functionality
"""
import requests
import json

API_URL = "http://127.0.0.1:8000"

def test_connection():
    """Test if backend is running"""
    try:
        response = requests.get(f"{API_URL}/test", timeout=5)
        if response.status_code == 200:
            print("✅ Backend connection successful:", response.json())
            return True
        else:
            print("❌ Backend connection failed:", response.status_code)
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running. Please start the FastAPI server first.")
        return False

def test_chat():
    """Test AI chat functionality"""
    try:
        response = requests.post(
            f"{API_URL}/chat",
            json={"message": "Hello, how are you?"},
            timeout=10
        )
        if response.status_code == 200:
            result = response.json()
            print("✅ AI Chat test successful:", result.get('reply', 'No reply received'))
            return True
        else:
            print("❌ AI Chat test failed:", response.status_code, response.text)
            return False
    except requests.exceptions.RequestException as e:
        print("❌ AI Chat test failed with exception:", str(e))
        return False

def test_todo_crud():
    """Test basic todo CRUD operations"""
    try:
        # Create a test todo
        todo_data = {"title": "Test task", "description": "Test description"}
        response = requests.post(f"{API_URL}/todos/", json=todo_data, timeout=5)
        if response.status_code != 200:
            print("❌ Failed to create todo:", response.status_code, response.text)
            return False
        
        created_todo = response.json()
        print("✅ Created todo:", created_todo)
        
        # Get all todos
        response = requests.get(f"{API_URL}/todos/", timeout=5)
        if response.status_code != 200:
            print("❌ Failed to get todos:", response.status_code)
            return False
            
        todos = response.json()
        print(f"✅ Retrieved {len(todos)} todos")
        
        # Clean up - delete the test todo
        response = requests.delete(f"{API_URL}/todos/{created_todo['id']}", timeout=5)
        if response.status_code != 200:
            print("❌ Failed to delete todo:", response.status_code)
            return False
        
        print("✅ Deleted test todo")
        return True
    except requests.exceptions.RequestException as e:
        print("❌ Todo CRUD test failed with exception:", str(e))
        return False

if __name__ == "__main__":
    print("Testing Full Stack Todo App Backend...\n")
    
    if not test_connection():
        print("\nPlease start the backend server using:")
        print("cd backend")
        print("uvicorn main:app --reload")
        exit(1)
    
    print()
    test_todo_crud()
    print()
    test_chat()
    
    print("\nTesting complete!")