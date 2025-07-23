# VAA GenAI Technical Test — AI Travel Assistant

Welcome to the technical assessment for an AI Software Developer role at VAA.  
This test is designed to evaluate your Python, FastAPI, and prompt engineering skills using OpenAI's API and structured seed data.

---

## 🧠 Objective

Build a GenAI-powered **Travel Assistant** that responds to natural language travel queries via an API.  
You should use FastAPI, Pydantic (or a similar framework like Langchain), and OpenAI's GPT model to interpret queries and return structured, helpful travel advice.

---

## 📋 Prerequisites

- **Python 3.10+** (tested with Python 3.13)
- **OpenAI API Key** (for AI agents and embeddings)

---

## 🏃 Running the app

Assuming python is already installed. 


## ⚡ Quick Start


### 1. Create Virtual Environment

```bash
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
make install
# Or manually:
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the project root:

```bash
# Copy the example environment file
cp .env.example .env  # If you have one
# Or create manually:
touch .env
```

Add your OpenAI API key to `.env`:

```env
OPENAI_API_KEY=sk-proj-your-api-key-here
GPT_MODEL=gpt-3.5-turbo
```

### 4. Data Ingestion

Populate the vector databases with seed data:

```bash
make ingest
```

This will:
- Load travel data from `app/seed_data/`
- Create embeddings using OpenAI
- Store in local Chroma vector databases

### 5. Start the Application

#### Option A: API Server Only
```bash
make dev
```
API will be available at: http://localhost:8000

#### Option B: Web UI Only
```bash
make ui
```
Streamlit UI will be available at: http://localhost:8501

#### Option C: Both Together (Recommended when running the app)
```bash
make both 
```
### 6. Running unit tests

```bash
make test 
```
---

## 📌 Requirements

- Python 3.10+
- FastAPI
- OpenAI API Key
- Pydantic
- Seed data (provided as `.json`)

---

## 📋 Rules

You must adhere to the following conditions:

- **Original Work**: The code must be your own work. If you have a strong case to use a small code snippet from someone else's work (e.g., a boilerplate function), it must be clearly commented and attributed to the original author.

- **Testing**: You must include any unit tests you think are appropriate. Consider testing your API endpoints, data processing logic, and OpenAI integration.

- **Evaluations**: Implement evaluation methods to assess your AI responses. Consider testing for accuracy, relevance, proper use of seed data (vs hallucination), response consistency, and guardrail effectiveness.

- **Performance & Quality**: Give consideration to performance, security, and code quality. Your implementation should be production-ready.

- **Code Standards**: Code must be clear, concise, and human readable. Simplicity is often key. We want to see your problem-solving approach and clean architecture.

- **Focus on Implementation**: This is a test of your backend development and AI integration skills. We want to see what you can create with the core technologies. We suggest you spend 4 to 8 hours on the test but the actual amount of time is down to you.

---

## ✅ Your Task

Implement a `POST /travel-assistant` endpoint that:
- Accepts a user travel query e.g. `"I'm looking for a beach destination in July"`.
- Uses OpenAI to generate a structured response (e.g., recommended destination, reason, budget, tips).
- Utilise real data in the seed files (e.g., hotels, flights, experiences) i.e. don't rely on AI knowledge.
- Implement appropriate guardrails.
- Update or add a new README file with the python run time version and a summary of what you would improve to boost code clarity, maintainability, and production readiness if you had more time.

### Example Request

```json
POST /travel-assistant
Content-Type: application/json

{
  "query": "Where should I go for a solo foodie trip to Asia in September?"
}

```

---

## 📤 Supplying Your Code

Please create and commit your code into a **public GitHub repository** and supply the link to the recruiter for review.

Thanks for your time, we look forward to hearing from you!
