# API Development and Documentation Final Project

## Trivia App

Udacity is invested in creating bonding experiences for its employees and students. A bunch of team members got the idea to hold trivia on a regular basis and created a webpage to manage the trivia app and play the game, but their API experience is limited and still needs to be built out.

That's where you come in! Help them finish the trivia app so they can start holding trivia and seeing who's the most knowledgeable of the bunch. The application must:

1. Display questions - both all questions and by category. Questions should show the question, category and difficulty rating by default and can show/hide the answer.
2. Delete questions.
3. Add questions and require that they include question and answer text.
4. Search for questions based on a text query string.
5. Play the quiz game, randomizing either all questions or within a specific category.

Completing this trivia app will give you the ability to structure plan, implement, and test an API - skills essential for enabling your future applications to communicate with others.

## Getting Started

### Prerequisites & Installation

#### Backend Dependencies
1. **Python 3.7+** - Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

2. **Virtual Environment** - We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organized. Instructions for setting up a virual environment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

3. **PIP Dependencies** - Once your virtual environment is setup and running, install the required dependencies by navigating to the `/backend` directory and running:
```bash
pip install -r requirements.txt
```

4. **PostgreSQL** - Install and configure PostgreSQL for your platform:
   - [macOS](https://www.postgresql.org/download/macosx/)
   - [Windows](https://www.postgresql.org/download/windows/)
   - [Linux](https://www.postgresql.org/download/linux/)

#### Frontend Dependencies
1. **Node.js** - Download and install Node.js from [https://nodejs.org/en/download/](https://nodejs.org/en/download/)
2. **NPM** - Node Package Manager comes with Node.js
3. Install project dependencies:
```bash
cd frontend
npm install
```

### Local Development

#### Backend Setup
1. Create a `.env` file in the `backend` directory based on `.env.example`:
```bash
cp backend/.env.example backend/.env
```

2. Update the `.env` file with your database credentials:
```
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=trivia
DB_TEST_NAME=trivia_test
```

3. Create the database:
```bash
createdb trivia
createdb trivia_test
```

4. Populate the database:
```bash
psql trivia < backend/trivia.psql
```

5. Run the backend server:
```bash
cd backend
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

#### Frontend Setup
1. Start the frontend development server:
```bash
cd frontend
npm start
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend: http://localhost:5000

### Tests

#### Backend Tests
1. Make sure you have created the test database:
```bash
createdb trivia_test
```

2. Run the tests:
```bash
cd backend
python test_flaskr.py
```

The tests will verify:
- GET /categories
- GET /questions
- DELETE /questions
- POST /questions
- POST /questions/search
- GET /categories/<id>/questions
- POST /quizzes
- Error handling

#### Frontend Tests
1. Run the frontend tests:
```bash
cd frontend
npm test
```

## API Documentation

### Endpoints

#### GET '/categories'
- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns: An object with a single key, categories, that contains an object of id: category_string key: value pairs.

```json
{
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  }
}
```

#### GET '/questions'
- Fetches a paginated list of questions, total number of questions, all categories, and current category
- Request Arguments: page (integer)
- Returns: An object with paginated questions, total questions, object including all categories, and current category string

```json
{
  "questions": [
    {
      "id": 1,
      "question": "This is a question",
      "answer": "This is an answer",
      "difficulty": 5,
      "category": 2
    }
  ],
  "totalQuestions": 100,
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "currentCategory": "History"
}
```

#### DELETE '/questions/${id}'
- Deletes a specified question using the id of the question
- Request Arguments: id (integer)
- Returns: Does not need to return anything besides the appropriate HTTP status code. Optionally can return the id of the question.

#### POST '/questions'
- Sends a post request in order to search for a specific question by search term
- Request Body:
```json
{
  "searchTerm": "this is the term the user is looking for"
}
```
- Returns: any array of questions, a number of totalQuestions that met the search term and the current category string

```json
{
  "questions": [
    {
      "id": 1,
      "question": "This is a question",
      "answer": "This is an answer",
      "difficulty": 5,
      "category": 5
    }
  ],
  "totalQuestions": 100,
  "currentCategory": "Entertainment"
}
```

#### GET '/categories/${id}/questions'
- Fetches questions for a category specified by id request argument
- Request Arguments: id (integer)
- Returns: An object with questions for the specified category, total questions, and current category string

```json
{
  "questions": [
    {
      "id": 1,
      "question": "This is a question",
      "answer": "This is an answer",
      "difficulty": 5,
      "category": 4
    }
  ],
  "totalQuestions": 100,
  "currentCategory": "History"
}
```

#### POST '/quizzes'
- Sends a post request in order to get the next question
- Request Body:
```json
{
  "previous_questions": [1, 4, 20, 15],
  "quiz_category": "current category"
}
```
- Returns: a single new question object

```json
{
  "question": {
    "id": 1,
    "question": "This is a question",
    "answer": "This is an answer",
    "difficulty": 5,
    "category": 4
  }
}
```

### Error Handling

The API will return the following error types when requests fail:

- 400: Bad Request
- 404: Resource Not Found
- 422: Unprocessable Entity
- 500: Internal Server Error

Error responses are returned in the following format:

```json
{
  "success": false,
  "error": 404,
  "message": "Resource not found"
}
```
