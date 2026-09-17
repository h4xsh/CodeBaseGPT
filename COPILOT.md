# CodebaseGPT — V1

## 1. Project Overview

CodebaseGPT is a full-stack RAG application that allows a user to provide a public GitHub repository URL and then ask questions about the repository using natural language.

The application should

1. Accept a public GitHub repository URL.
2. Downloadclone the repository.
3. Find relevant source-code files.
4. Ignore unnecessary files and directories.
5. Split source code into smaller chunks.
6. Generate embeddings for those chunks.
7. Store the embeddings and metadata in ChromaDB.
8. Accept questions about the repository.
9. Perform similarity search against the repository's code.
10. Send the retrieved code context to an LLM.
11. Generate an answer grounded in the retrieved repository code.
12. Display relevant source filessnippets alongside the answer.

The primary purpose of this project is learning RAG and full-stack AI development.

The code must therefore prioritize

 Simplicity
 Readability
 Understandability
 Correctness
 Easy debugging
 Clear separation of responsibilities

Do not optimize prematurely.

---

# 2. VERY IMPORTANT — Coding Philosophy

## Keep the code as simple as possible.

This is a learning project.

Do NOT turn simple functionality into complicated architecture.

### Rules

 Prefer simple functions over unnecessary classes.
 Prefer straightforward code over clever code.
 Do not create abstractions unless they solve an actual problem.
 Do not create interfacesbase classes unless they are genuinely necessary.
 Do not introduce design patterns just because they are considered best practice.
 Do not create unnecessary utility files.
 Do not create unnecessary folders.
 Do not create unnecessary dependencies.
 Do not duplicate large amounts of code.
 Keep functions reasonably small and understandable.
 Use descriptive variable and function names.
 Add comments when they explain WHY something is done, not obvious comments explaining WHAT the code does.
 Avoid premature optimization.
 Avoid unnecessary asynchronous code.
 Avoid unnecessary dependency injection.
 Avoid unnecessary configuration.
 Avoid unnecessary database abstractions.

### Do NOT introduce these technologies in V1 unless explicitly requested

 Redis
 Celery
 PostgreSQL
 Docker
 Kubernetes
 Microservices
 LangGraph
 Multi-agent systems
 Agent frameworks
 Knowledge graphs
 Elasticsearch
 Reranking models
 Hybrid search
 AST-based complex code analysis
 GitHub OAuth
 Private repository authentication
 Payment systems
 Cloud infrastructure

If a feature can be implemented simply without one of these technologies, do it without the technology.

---

# 3. V1 Scope

## V1 MUST support

### Repository

 Public GitHub repositories only.
 Repository supplied through a GitHub URL.
 Clonedownload the repository locally.
 Assign a unique repository ID.
 Track basic processing status.

### Supported source files

Initially support

```text
.py
.js
.jsx
.ts
.tsx
.java
.c
.cpp
.h
.hpp
.html
.css
.md
.json
```

Additional extensions may be added later.

### Ignored directories

Ignore

```text
.git
node_modules
venv
.venv
__pycache__
dist
build
coverage
.next
target
bin
obj
```

### Ignored files

Ignore files such as

```text
.env
.env.
package-lock.json
yarn.lock
pnpm-lock.yaml
```

Do not embed secrets or environment files.

Large generated files should also be ignored.

---

# 4. Technology Stack

Use the following stack for V1.

## Backend

```text
Python
FastAPI
```

## RAG

```text
LangChain where it genuinely simplifies the implementation
SentenceTransformers
ChromaDB
```

Do not use LangChain for every possible component.

If a small piece is easier and clearer using normal Python, use normal Python.

## Embedding model

Use

```text
BAAIbge-small-en-v1.5
```

Run it locally using SentenceTransformers.

## Chat model

Use

```text
Qwen3-8B
```

Run it locally through

```text
Ollama
```

The application should communicate with Ollama through a simple LLM service.

## Frontend

```text
React
Vite
Tailwind CSS
```

---

# 5. V1 Architecture

Use this architecture

```text
Frontend
    
    v
FastAPI
    
    +--------------------+
                        
    v                    v
Repository API       Chat API
                        
    v                    v
Ingestion Service    RAG Service
                        
    +----+----+          
                       
         v    v          v
      GitHub Files    ChromaDB
                        
         v               
      Chunking           
                        
         v               
     Embeddings --------+
         
         v
      ChromaDB
         
         v
      Retrieved Chunks
         
         v
      Qwen3-8B
         
         v
       Answer
```

---

# 6. Backend File Structure

Use this structure

```text
backend
│
├── app
│   ├── main.py
│   │
│   ├── api
│   │   ├── repositories.py
│   │   └── chat.py
│   │
│   ├── services
│   │   ├── github.py
│   │   ├── file_loader.py
│   │   ├── chunker.py
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │   ├── ingestion.py
│   │   ├── llm.py
│   │   └── rag.py
│   │
│   ├── models
│   │   └── schemas.py
│   │
│   └── core
│       └── config.py
│
├── tests
│   ├── test_file_loader.py
│   ├── test_chunker.py
│   ├── test_repositories.py
│   └── test_chat.py
│
├── data
│   └── repositories
│
├── chroma_db
│
├── requirements.txt
├── .env
└── .env.example
```

Do not add files to this structure unless there is a concrete reason.

---

# 7. Backend File Responsibilities

## `appmain.py`

FastAPI entry point.

Responsibilities

 Create the FastAPI application.
 Configure CORS.
 Register API routers.
 Configure basic application startup behavior.

Do not put business logic here.

---

## `appapirepositories.py`

Repository-related HTTP endpoints.

Responsibilities

 Receive GitHub repository URLs.
 Validate requests.
 Call the ingestion service.
 Return repository informationstatus.

Example endpoints

```text
POST repositories
GET repositories{repository_id}
DELETE repositories{repository_id}
```

The API layer should not directly implement cloning, chunking, embedding, or vector search.

---

## `appapichat.py`

Chat-related HTTP endpoints.

Example

```text
POST chat
```

The request should contain

```json
{
    repository_id ...,
    question How does authentication work
}
```

The endpoint should call the RAG service.

Do not put RAG implementation inside this file.

---

# 8. Services

## `servicesgithub.py`

Responsible only for interacting with public GitHub repositories.

Responsibilities

 Validateparse GitHub URLs.
 Clonedownload repositories.
 Determine repository name.
 Return local repository path.

It should not

 Generate embeddings.
 Chunk files.
 Talk to the LLM.
 Perform vector searches.

---

## `servicesfile_loader.py`

Responsible for discovering and reading relevant repository files.

Responsibilities

 Recursively walk through repository directories.
 Filter supported file extensions.
 Ignore configured directories.
 Ignore configured files.
 Ignore excessively large files.
 Read file contents.

Return simple Python structures.

Example

```python
{
    path backendauth.py,
    content ...
}
```

Keep this service simple.

---

## `serviceschunker.py`

Responsible for splitting source code into chunks.

V1 should use a simple chunking strategy.

Do NOT implement sophisticated AST parsing.

Each chunk should contain

```python
{
    content ...,
    file_path backendauth.py,
    chunk_index 0
}
```

The chunker should preserve enough metadata to identify where a chunk came from.

---

## `servicesembeddings.py`

Responsible for generating embeddings.

Use

```text
BAAIbge-small-en-v1.5
```

Use SentenceTransformers.

Provide simple functions for

 Embedding one query.
 Embedding multiple documentschunks.

The rest of the application should not need to know the details of the embedding model.

---

## `servicesvector_store.py`

Responsible for interacting with ChromaDB.

Responsibilities

 Createget collections.
 Add document chunks.
 Store embeddings.
 Store metadata.
 Search for similar chunks.
 Delete repository data.

Use repository IDs to keep repositories separate.

Example metadata

```python
{
    repository_id repo_123,
    file_path backendauth.py,
    file_extension .py,
    chunk_index 2
}
```

Do not put ChromaDB calls throughout the application.

Only this service should directly interact with ChromaDB.

---

## `servicesingestion.py`

This service coordinates repository ingestion.

Pipeline

```text
GitHub URL
    ↓
Clone repository
    ↓
Find relevant files
    ↓
Read files
    ↓
Split into chunks
    ↓
Generate embeddings
    ↓
Store in ChromaDB
    ↓
Repository ready
```

This service should coordinate the other services.

Do not duplicate GitHub, file loading, chunking, or embedding logic here.

---

## `servicesllm.py`

Responsible for communicating with Ollama.

Use

```text
Qwen3-8B
```

Expose a simple function such as

```python
generate_answer(prompt)
```

The rest of the application should not need to know how Ollama requests work.

Do not add multiple LLM providers in V1.

---

## `servicesrag.py`

This is the main RAG orchestration service.

Pipeline

```text
Question
    ↓
Create query embedding
    ↓
Search ChromaDB
    ↓
Retrieve relevant chunks
    ↓
Build context
    ↓
Build prompt
    ↓
Send to Qwen3-8B
    ↓
Return answer + sources
```

Start with

```text
top_k = 5
```

Make this configurable later if necessary.

The RAG service should not blindly answer from the model's general knowledge.

The prompt should instruct the model to use the supplied repository context.

If the retrieved context does not contain enough information, the model should say so rather than inventing an answer.

---

# 9. Repository Processing Status

A repository should have a simple status

```text
pending
processing
ready
failed
```

Example flow

```text
User submits repository
        ↓
pending
        ↓
processing
        ↓
embeddingindexing
        ↓
ready
```

If something fails

```text
failed
```

Return a useful error message.

Do not introduce a background task queue such as Celery for V1.

For V1, a simple implementation is sufficient.

---

# 10. Conversation Context

The chat should support basic conversational context.

Example

```text
User
How does authentication work

AI
Authentication uses JWT...

User
Where is the token generated

AI
The token is generated in...
```

The second question should have access to recent conversation messages.

Do not implement a sophisticated memory system.

For V1, recent messages can simply be sent along with the current question.

---

# 11. Prompt Rules

The LLM system prompt should establish the following behavior

```text
You are CodebaseGPT.

You answer questions about a software repository.

Use the provided repository context to answer the user's question.

Do not invent files, functions, classes, APIs, variables, or behavior.

If the retrieved context does not provide enough information,
clearly say that you do not have enough information.

When possible, mention the relevant file paths.

Explain technical concepts clearly and concisely.

If multiple files are involved, explain how they relate to each other.
```

The prompt should contain

```text
User question
+
Relevant retrieved code
+
Recent conversation context
```

Do not send the entire repository to the LLM.

---

# 12. Retrieval

V1 uses

```text
Embedding similarity search
```

with ChromaDB.

Initial configuration

```text
top_k = 5
```

Do not implement

 Reranking
 BM25
 Hybrid search
 Query expansion
 Multi-query retrieval
 Knowledge graphs

Those can be explored later.

The purpose of V1 is to understand basic vector retrieval.

---

# 13. Source Information

Every answer should be accompanied by relevant sources when available.

Example

```json
{
    answer Authentication is handled using JWT...,
    sources [
        {
            file_path backendauth.py,
            snippet ...
        },
        {
            file_path backendrouteslogin.py,
            snippet ...
        }
    ]
}
```

The frontend should display these sources.

Do not initially implement GitHub-style line highlighting.

---

# 14. Frontend Structure

Use

```text
frontend
└── src
    ├── components
    │   ├── RepositoryInput.jsx
    │   ├── FileTree.jsx
    │   ├── ChatWindow.jsx
    │   ├── ChatMessage.jsx
    │   └── SourceCard.jsx
    │
    ├── pages
    │   └── Home.jsx
    │
    ├── services
    │   └── api.js
    │
    ├── App.jsx
    ├── main.jsx
    └── index.css
```

---

# 15. Frontend Responsibilities

## `RepositoryInput.jsx`

Allows the user to enter

```text
GitHub repository URL
```

and start repository processing.

Show

 Loading state
 Success state
 Error state

---

## `FileTree.jsx`

Displays the repository's filesdirectories.

Keep it simple.

It does not need to be a full IDE-like file explorer.

---

## `ChatWindow.jsx`

Displays the conversation and manages the basic chat state.

Should allow

 Sending questions.
 Displaying answers.
 Displaying loading state.
 Displaying errors.

---

## `ChatMessage.jsx`

Displays an individual user or AI message.

Keep this component focused only on message presentation.

---

## `SourceCard.jsx`

Displays retrieved repository sources.

Show

```text
File path
Code snippet
```

Keep the design simple.

---

## `pagesHome.jsx`

Main application page.

Should combine

```text
Repository input
File tree
Chat interface
```

---

## `servicesapi.js`

Contains frontend functions for communicating with FastAPI.

For example

```text
createRepository()
getRepository()
askQuestion()
deleteRepository()
```

Components should use these functions rather than repeating raw HTTP requests everywhere.

---

# 16. Data Flow

## Repository ingestion

```text
React
  ↓
POST repositories
  ↓
repositories.py
  ↓
ingestion.py
  ↓
github.py
  ↓
file_loader.py
  ↓
chunker.py
  ↓
embeddings.py
  ↓
vector_store.py
  ↓
ChromaDB
```

## Question answering

```text
React
  ↓
POST chat
  ↓
chat.py
  ↓
rag.py
  ↓
embeddings.py
  ↓
vector_store.py
  ↓
Relevant chunks
  ↓
Prompt
  ↓
llm.py
  ↓
Ollama
  ↓
Qwen3-8B
  ↓
Answer + Sources
  ↓
React
```

---

# 17. API Design

Keep the initial API small.

## Create repository

```text
POST repositories
```

Request

```json
{
    github_url httpsgithub.comuserrepository
}
```

Response should contain a repository ID and processing status.

---

## Get repository

```text
GET repositories{repository_id}
```

Returns basic information and processing status.

---

## Chat

```text
POST chat
```

Request

```json
{
    repository_id repo_123,
    question How does authentication work,
    messages []
}
```

Response

```json
{
    answer ...,
    sources []
}
```

---

## Delete repository

```text
DELETE repositories{repository_id}
```

Should remove the repository's local data and vector data when possible.

---

# 18. Configuration

Use `.env` for configurable values.

Example

```text
OLLAMA_BASE_URL=httplocalhost11434
OLLAMA_MODEL=qwen38b
CHROMA_PATH=.chroma_db
EMBEDDING_MODEL=BAAIbge-small-en-v1.5
```

Use `.env.example` as a template.

Never commit secrets.

---

# 19. Error Handling

Handle common errors

### GitHub

 Invalid GitHub URL
 Repository doesn't exist
 Clone failure
 Unsupported repository

### Files

 Unsupported encoding
 File too large
 Empty repository
 No supported source files

### Embeddings

 Embedding model failure

### ChromaDB

 Collection failure
 Search failure

### Ollama

 Ollama unavailable
 Model unavailable
 Generation failure

Return clear error messages.

Do not create a complicated custom exception framework unless it becomes necessary.

---

# 20. Logging

Use Python's standard logging system.

Log important events such as

```text
Repository cloning started
Repository cloned
Files discovered
Files skipped
Chunks created
Embeddings generated
Documents stored
Repository processing complete
Question received
Chunks retrieved
LLM request started
LLM response received
```

Do not add external loggingobservability services in V1.

---

# 21. Testing

Create basic tests.

Focus on meaningful behavior.

### `test_file_loader.py`

Test

 Supported files are loaded.
 Ignored directories are skipped.
 Ignored files are skipped.

### `test_chunker.py`

Test

 Large text is split.
 Metadata is preserved.

### `test_repositories.py`

Test

 Valid repository request.
 Invalid repository URL.
 Basic repository creation behavior.

### `test_chat.py`

Test

 Chat request validation.
 Basic RAG response behavior.

Do not spend excessive time building a huge test suite.

---

# 22. Security Basics

V1 is a local learning application.

Still follow basic rules

 Never commit `.env`.
 Never expose API keys in the frontend.
 Never embed `.env` files.
 Do not execute arbitrary repository code.
 Do not run repository scripts.
 Do not install dependencies from submitted repositories.
 Treat repository contents as untrusted text.
 Do not execute code retrieved from ChromaDB.

CodebaseGPT should read source code, not execute it.

---

# 23. Implementation Phases

Implement the project incrementally.

Do NOT attempt to build the entire application in one step.

## Phase 1 — FastAPI Foundation

Build

```text
FastAPI
main.py
basic API routes
Pydantic schemas
configuration
```

Verify the server works.

---

## Phase 2 — GitHub Repository Ingestion

Build

```text
GitHub URL
    ↓
Clone repository
    ↓
Store locally
```

Test it independently.

---

## Phase 3 — File Loading

Build

```text
Repository
    ↓
Walk files
    ↓
Filter files
    ↓
Read source code
```

Printlog the files discovered.

---

## Phase 4 — Chunking

Build

```text
Source files
    ↓
Chunks
```

Inspect the generated chunks manually.

Do not move forward until chunking works correctly.

---

## Phase 5 — Embeddings

Add

```text
BAAIbge-small-en-v1.5
```

Generate embeddings for chunks.

---

## Phase 6 — ChromaDB

Store

```text
chunks
+
embeddings
+
metadata
```

Then implement similarity search.

At this point, test

```text
Question
    ↓
Embedding
    ↓
ChromaDB
    ↓
Top 5 chunks
```

before adding the LLM.

---

## Phase 7 — Qwen + Ollama

Add

```text
Ollama
    ↓
Qwen3-8B
```

Test the model independently first.

---

## Phase 8 — Basic RAG

Connect

```text
Question
 ↓
Retrieval
 ↓
Context
 ↓
Prompt
 ↓
Qwen
 ↓
Answer
```

This is the first complete CodebaseGPT backend.

---

## Phase 9 — Sources

Return

```text
Answer
+
Relevant file paths
+
Code snippets
```

---

## Phase 10 — Frontend

Build the React UI around the working backend.

Do not start with frontend complexity.

---

## Phase 11 — Basic Conversation Context

Add recent chat messages to the request.

---

## Phase 12 — Testing + Polish

Add

 Error handling
 Loading states
 Basic tests
 Logging
 UI polish
 Repository deletion

Only after the core system works.

---

# 24. Definition of Done for V1

V1 is complete when a user can

```text
1. Open CodebaseGPT
        ↓
2. Enter a public GitHub URL
        ↓
3. Wait for repository processing
        ↓
4. See the repository files
        ↓
5. Ask a question
        ↓
6. CodebaseGPT retrieves relevant code
        ↓
7. Qwen3-8B answers using that context
        ↓
8. User can see the relevant source filessnippets
        ↓
9. User can ask follow-up questions
```

Example

```text
Repository
httpsgithub.comexampleproject

Question
How does authentication work

Answer
Authentication is handled through JWT tokens.
The login route validates the user's credentials and
generates a token. Protected routes then validate
that token through the authentication dependency.

Sources
- backendauth.py
- backendrouteslogin.py
- backenddependencies.py
```

If this works reliably, V1 is successful.

---

# 25. Things to Leave for V2+

Do not implement these unless explicitly requested

```text
Private GitHub repositories
GitHub OAuth
GitHub webhooks
Automatic repository updates
Branch selection
Commit history analysis
Pull request analysis
Code modification
Automatic code fixes
Pull request generation
Agentic coding
LangGraph
Multi-agent systems
Reranking
Hybrid retrieval
AST-based retrieval
Knowledge graphs
Advanced memory
Multiple LLM providers
Multiple embedding models
PostgreSQL
Redis
Celery
Docker
Cloud deployment
Authentication
User accounts
Team collaboration
Billing
```

These are separate features and should not creep into V1.

---

# 26. Copilot Behavior

When implementing this project

### Before coding

Understand the current phase and inspect the existing code.

Do not implement future phases prematurely.

### When modifying existing code

Prefer modifying the existing implementation over creating a new parallel implementation.

Do not duplicate functionality.

### When choosing between two approaches

Choose the approach that

1. Is easier to understand.
2. Has fewer dependencies.
3. Has fewer files.
4. Is easier to debug.
5. Is sufficient for V1.

### If uncertain

Choose the simpler implementation.

Do not introduce complexity just in case.

### If a requested feature requires significant architectural changes

Explain the change briefly before implementing it.

Do not silently redesign the project.

---

# 27. Core Principle

The most important rule for this project is

 Build the simplest working version first. Understand it completely. Then improve it.

CodebaseGPT V1 is a learning-focused RAG application, not a production-scale autonomous coding platform.

A simple implementation that you understand completely is more valuable than a sophisticated implementation that you cannot explain.
