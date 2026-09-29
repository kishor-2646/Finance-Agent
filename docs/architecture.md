# Architecture

## Overview

Finance Agent is a full-stack AI-powered personal finance assistant.

## Components

### Backend (FastAPI)
- REST API serving financial data and AI agent responses
- Pydantic models for request/response validation
- Integration with LLM for natural-language financial queries

### Frontend (Next.js + Tailwind)
- Dashboard with charts and transaction views
- Chat interface for interacting with the finance agent
- Responsive design with Tailwind CSS

### Data Flow

```
User ──► Next.js Frontend ──► FastAPI Backend ──► LLM / Data Store
                                    │
                                    ▼
                              CSV / Mock Data
```
