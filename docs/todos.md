# Document Copilot Roadmap

This roadmap turns the architecture and client brief into an ordered MVP plan.
Complete each phase in order unless a task is explicitly marked independent.

## Project constraints and stack

- Backend: Python 3.12+, FastAPI, Pydantic v2, Uvicorn.
- Frontend: Vite, React SPA, TypeScript, React Router, Tailwind, shadcn/ui.
- Database: Supabase Postgres.
- Schema management: SQLAlchemy models and Alembic migrations from `backend/`.
- Retrieval: Supabase `pgvector` plus PostgreSQL full-text search.
- Authentication: Supabase Auth with email sign-in.
- Hosting: separate Railway frontend and backend services.
- LLM and embeddings: the repository-standard local Studio LM
  `qwen/qwen3-4b-thinking-2507` through its OpenAI-compatible API.
- Source corpus: SEC filings downloaded by `data/download.py`; start with the
  five companies and five years defined in the client brief.
- Do not add alternative infrastructure or libraries without a stated reason.
- Keep secrets in environment configuration; never expose service-role keys or
  LLM credentials to the browser.

## Definition of MVP complete

- [ ] Authorized Driftwood analysts can sign in and use the application.
- [ ] The pilot corpus is ingested without duplicate documents or chunks.
- [ ] Analysts can create, revisit, and delete their own chat threads.
- [ ] Questions receive streamed answers from the FastAPI backend.
- [ ] Supported factual claims have citations linked to retrieved passages.
- [ ] Unsupported questions receive an explicit insufficient-evidence response.
- [ ] Users cannot access another user's threads or messages.
- [ ] Retrieval, grounding, authentication, and API tests pass.
- [ ] Frontend and backend deploy successfully on Railway.
- [ ] A five-analyst pilot measures whether the product saves at least three
  hours per analyst per week.

## Phase 1 — Confirm scope and configuration

- [ ] Confirm the pilot corpus: Apple, Amazon, Alphabet, Microsoft, and NVIDIA
  10-K filings for fiscal years 2021–2025.
- [ ] Confirm the authorized Driftwood email domain or explicit allowlist.
- [ ] Decide the citation fallback when SEC HTML has no reliable page number:
  section, chunk index, source offsets, stable URL, and excerpt.
- [ ] Choose and document the local LLM endpoint, embedding model, and vector
  dimension.
- [ ] Add backend settings in `backend/app/config.py`.
- [ ] Add frontend settings in `frontend/lib/env.ts`.
- [ ] Add safe placeholders and comments to `.env.example` files.
- [ ] Fail fast when required configuration is missing.

## Phase 2 — Scaffold the services

- [ ] Initialize the backend package, FastAPI app, health endpoint, and
  dependency management with `uv`.
- [ ] Initialize the frontend Vite React TypeScript app with `pnpm`.
- [ ] Configure Ruff, pytest, TypeScript checking, and frontend linting.
- [ ] Add structured backend logging and request IDs.
- [ ] Add backend CORS configuration from settings.
- [ ] Add Supabase browser client and shared frontend HTTP client.
- [ ] Verify the installed AI SDK version before implementing its transport.

## Phase 3 — Create the database schema

- [ ] Add SQLAlchemy models for `profiles`, `chat_threads`,
  `chat_messages`, `message_citations`, `source_documents`, and
  `document_chunks`.
- [ ] Initialize Alembic and configure it with the direct/session Supabase
  database connection.
- [ ] Create the migration for the `vector` extension and embedding column.
- [ ] Add generated full-text search vectors and GIN indexes.
- [ ] Add the vector HNSW index.
- [ ] Add foreign keys, ownership indexes, timestamps, and uniqueness rules.
- [ ] Add and review RLS policies and role permissions explicitly in the
  migration.
- [ ] Verify both `alembic upgrade head` and `alembic downgrade`.

## Phase 4 — Implement authentication and authorization

- [ ] Build email sign-in, sign-up, sign-out, session restoration, and
  protected routes in the frontend.
- [ ] Implement FastAPI bearer-token extraction and Supabase token
  verification.
- [ ] Expose a typed `CurrentUser` dependency.
- [ ] Enforce the Driftwood domain or allowlist at the backend boundary.
- [ ] Enforce thread ownership on every thread and message operation.
- [ ] Add tests for missing, expired, invalid, and unauthorized credentials.

## Phase 5 — Build the SEC ingestion pipeline

- [ ] Run and verify `uv run data/download.py` against the pilot parameters.
- [ ] Normalize each filing into Markdown while preserving headings, tables,
  sections, and source offsets.
- [ ] Extract filing metadata: company, ticker, filing type, fiscal year,
  filing date, accession number, and SEC URL.
- [ ] Define a non-fabricated citation strategy for filings without page
  numbers.
- [ ] Implement section-aware chunking with token counts and metadata.
- [ ] Generate embeddings in bounded batches through the configured
  OpenAI-compatible endpoint.
- [ ] Write documents and chunks to Supabase.
- [ ] Make ingestion idempotent using accession numbers and checksums.
- [ ] Record and report failed documents instead of silently skipping them.
- [ ] Verify all 25 pilot filings and inspect representative chunks manually.

## Phase 6 — Implement hybrid retrieval

- [ ] Add semantic vector search over `document_chunks.embedding`.
- [ ] Add PostgreSQL full-text search over `search_vector`.
- [ ] Add filters for company, ticker, fiscal year, filing type, and date.
- [ ] Fuse semantic and lexical rankings with Reciprocal Rank Fusion.
- [ ] Retrieve neighboring chunks when additional context is needed.
- [ ] Bound result count, context size, and query length.
- [ ] Add retrieval tests for exact terms, cross-year comparisons,
  cross-company questions, risk factors, and financial metrics.
- [ ] Measure retrieval latency and relevance on the ten client questions.

## Phase 7 — Implement grounded answer generation

- [ ] Add typed `Citation`, `SourcePassage`, and `GroundedAnswer` models.
- [ ] Add the PydanticAI agent and explicit runtime dependencies.
- [ ] Add the product instruction contract:
  answer only from retrieved passages, cite claims, refuse unsupported
  conclusions, and do not provide investment recommendations.
- [ ] Add bounded retrieval tools such as `search_filings`, `read_chunk`, and
  `read_surrounding_chunks`.
- [ ] Validate that every citation belongs to a retrieved chunk.
- [ ] Validate citation metadata and excerpt consistency.
- [ ] Reject or retry supported answers with missing citations.
- [ ] Return a controlled insufficient-evidence answer when context is weak.
- [ ] Add regression tests for invalid citations, unsupported claims, and
  answers that infer beyond the filings.

## Phase 8 — Build chat APIs and streaming

- [ ] Implement `GET /health`.
- [ ] Implement thread list, create, read, and delete endpoints.
- [ ] Implement `POST /chat/stream` with authenticated request models.
- [ ] Define and test text-delta, citation, source, completion, and error
  events for the frontend transport.
- [ ] Translate AI SDK wire messages into internal typed models.
- [ ] Persist user messages, assistant messages, citations, usage, latency,
  and model metadata after successful completion.
- [ ] Return explicit 401, 403, 404, 422, and upstream failure responses.
- [ ] Add timeout and bounded retry behavior for model and database calls.
- [ ] Test streaming with a fake model; never call a real model in unit tests.

## Phase 9 — Build the frontend product experience

- [ ] Add application routing and protected layout.
- [ ] Add thread sidebar, new-thread flow, history loading, and deletion.
- [ ] Connect the chat UI to FastAPI using the verified AI SDK transport.
- [ ] Render streamed Markdown assistant responses.
- [ ] Render clickable citations with company, filing, year, section, and URL.
- [ ] Render expandable underlying source passages.
- [ ] Add loading, empty, authentication-expired, network, retrieval, and
  grounding-failure states.
- [ ] Add responsive layout and keyboard-accessible controls.
- [ ] Add frontend component and API-client tests where practical.

## Phase 10 — Evaluate and harden trust

- [ ] Turn the ten client questions into a fixed evaluation set.
- [ ] Define expected filings, concepts, citations, and refusal behavior for
  each question.
- [ ] Measure retrieval recall, citation validity, citation completeness,
  unsupported-claim rate, latency, and error rate.
- [ ] Test that cross-year questions do not lose older filings through a
  naive top-k limit.
- [ ] Test that the assistant refuses claims such as “the filings prove
  generative AI improved margins” when the corpus does not prove causation.
- [ ] Add per-user rate limits, maximum message length, maximum context, and
  maximum agent/tool steps.
- [ ] Remove sensitive prompt, token, and document content from normal logs.

## Phase 11 — Deploy and run the pilot

- [ ] Configure Railway frontend and backend services.
- [ ] Configure production environment variables and CORS origins.
- [ ] Apply reviewed Alembic migrations to production Supabase.
- [ ] Configure Supabase email confirmation and production RLS.
- [ ] Add service health checks and deployment smoke tests.
- [ ] Add operational metrics for request, retrieval, model, and ingestion
  latency.
- [ ] Invite five senior analysts to a one-week pilot.
- [ ] Record baseline and post-pilot time spent on source-document intake.
- [ ] Collect citation corrections, unsupported-answer reports, and trust
  feedback.
- [ ] Roll out firm-wide only if the pilot demonstrates at least three hours
  saved per analyst per week.

## Deferred after MVP

- [ ] Add 10-Q filings after the 10-K pilot is reliable.
- [ ] Add local JWT verification only if Supabase Auth verification latency
  becomes material.
- [ ] Add object storage for raw filings if local ingestion inputs are no
  longer sufficient.
- [ ] Add advanced analyst feedback and retrieval tuning from pilot data.
