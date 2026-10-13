.PHONY: setup run test lint redteam

setup:          ## install Python deps
	uv sync

run:            ## start the chatbot on http://localhost:8000
	uv run uvicorn app.main:app --reload

test:           ## run unit tests (mock model, no Ollama needed)
	uv run pytest -q

lint:
	uv run ruff check .

redteam:        ## generate and run promptfoo attacks against the running app
	npx promptfoo@latest redteam run -c redteam/promptfoo/promptfooconfig.yaml