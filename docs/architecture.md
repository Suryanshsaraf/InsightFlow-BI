# InsightFlow Architecture Overview

InsightFlow is built as a modern, decoupled monorepo featuring a Next.js frontend and a FastAPI backend.

## Architecture Highlights
- **Decoupled Frontend**: Next.js App Router communicating with the API via REST.
- **Layered Backend**: FastAPI utilizing Routers -> Services -> Database models pattern.
- **Dynamic Table Storage**: SQLite/PostgreSQL dynamically isolated tables created on-the-fly for uploaded CSV datasets.
- **AI Analytics**: OpenAI-compatible client routing to Groq for extremely low latency SQL translation and insight generation.
