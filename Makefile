
ingest:
	@echo "Ingesting data into vector stores..."
	poetry run python -m app.services.ingest_data

dev:
	@echo "Starting FastAPI development server..."
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

ui:
	@echo "Starting Streamlit UI..."
	poetry run streamlit run app/ui/chatbot.py --server.port 8501

both:
	@echo "Starting both backend and UI"
	poetry run  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 & poetry run streamlit run app/ui/chatbot.py --server.port 8501


clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -delete
	find . -name "*.pyc" -delete

test:
	@echo "Running tests..."
	poetry run pytest