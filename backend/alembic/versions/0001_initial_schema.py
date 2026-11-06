"""Create the initial Document Copilot schema.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-11-06
"""

from collections.abc import Sequence

from alembic import op

revision = "0001_initial_schema"
down_revision = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create extensions, tables, indexes, and RLS policies."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.execute(
        """
        CREATE TABLE users (
            id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
            email varchar(320),
            display_name varchar(200),
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )
    op.execute(
        """
        CREATE TABLE chat_threads (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title varchar(200),
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )
    op.execute(
        """
        CREATE TABLE chat_messages (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            thread_id uuid NOT NULL REFERENCES chat_threads(id) ON DELETE CASCADE,
            role varchar(20) NOT NULL,
            content text NOT NULL,
            message_data jsonb,
            created_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )
    op.execute(
        """
        CREATE TABLE source_documents (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            company_name varchar(200) NOT NULL,
            ticker varchar(20) NOT NULL,
            filing_type varchar(20) NOT NULL,
            fiscal_year integer NOT NULL,
            filing_date date,
            accession_number varchar(30) NOT NULL UNIQUE,
            source_url text NOT NULL,
            content_markdown text NOT NULL,
            metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )
    op.execute(
        """
        CREATE TABLE document_chunks (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            document_id uuid NOT NULL REFERENCES source_documents(id) ON DELETE CASCADE,
            chunk_index integer NOT NULL,
            section varchar(300),
            page_number integer,
            source_start integer,
            source_end integer,
            chunk_text text NOT NULL,
            token_count integer NOT NULL,
            metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
            embedding vector(1536),
            search_vector tsvector GENERATED ALWAYS AS
                (to_tsvector('english', chunk_text)) STORED,
            CONSTRAINT uq_document_chunks_document_id_chunk_index
                UNIQUE (document_id, chunk_index)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE message_citations (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            message_id uuid NOT NULL REFERENCES chat_messages(id) ON DELETE CASCADE,
            chunk_id uuid NOT NULL REFERENCES document_chunks(id) ON DELETE RESTRICT,
            citation_label varchar(100),
            excerpt text NOT NULL,
            created_at timestamptz NOT NULL DEFAULT now(),
            CONSTRAINT uq_message_citations_message_id_chunk_id
                UNIQUE (message_id, chunk_id)
        )
        """
    )

    op.execute(
        "CREATE INDEX ix_chat_threads_user_id_updated_at "
        "ON chat_threads (user_id, updated_at)"
    )
    op.execute(
        "CREATE INDEX ix_chat_messages_thread_id_created_at "
        "ON chat_messages (thread_id, created_at)"
    )
    op.execute(
        "CREATE INDEX ix_source_documents_ticker_fiscal_year "
        "ON source_documents (ticker, fiscal_year)"
    )
    op.execute(
        "CREATE INDEX ix_document_chunks_document_id_chunk_index "
        "ON document_chunks (document_id, chunk_index)"
    )
    op.execute(
        "CREATE INDEX ix_document_chunks_embedding_hnsw "
        "ON document_chunks USING hnsw (embedding vector_cosine_ops)"
    )
    op.execute(
        "CREATE INDEX ix_document_chunks_search_vector "
        "ON document_chunks USING gin (search_vector)"
    )

    op.execute("GRANT USAGE ON SCHEMA public TO authenticated, service_role")
    op.execute(
        "GRANT SELECT ON source_documents, document_chunks "
        "TO authenticated, service_role"
    )
    op.execute(
        "GRANT SELECT, INSERT, UPDATE, DELETE "
        "ON users, chat_threads, chat_messages, message_citations "
        "TO authenticated, service_role"
    )

    for table in (
        "users",
        "chat_threads",
        "chat_messages",
        "message_citations",
        "source_documents",
        "document_chunks",
    ):
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")

    op.execute(
        """
        CREATE POLICY users_owner_policy ON users
        FOR ALL TO authenticated
        USING (id = auth.uid())
        WITH CHECK (id = auth.uid())
        """
    )
    op.execute(
        """
        CREATE POLICY chat_threads_owner_policy ON chat_threads
        FOR ALL TO authenticated
        USING (user_id = auth.uid())
        WITH CHECK (user_id = auth.uid())
        """
    )
    op.execute(
        """
        CREATE POLICY chat_messages_owner_policy ON chat_messages
        FOR ALL TO authenticated
        USING (
            EXISTS (
                SELECT 1 FROM chat_threads
                WHERE chat_threads.id = chat_messages.thread_id
                AND chat_threads.user_id = auth.uid()
            )
        )
        WITH CHECK (
            EXISTS (
                SELECT 1 FROM chat_threads
                WHERE chat_threads.id = chat_messages.thread_id
                AND chat_threads.user_id = auth.uid()
            )
        )
        """
    )
    op.execute(
        """
        CREATE POLICY message_citations_owner_policy ON message_citations
        FOR ALL TO authenticated
        USING (
            EXISTS (
                SELECT 1
                FROM chat_messages
                JOIN chat_threads ON chat_threads.id = chat_messages.thread_id
                WHERE chat_messages.id = message_citations.message_id
                AND chat_threads.user_id = auth.uid()
            )
        )
        WITH CHECK (
            EXISTS (
                SELECT 1
                FROM chat_messages
                JOIN chat_threads ON chat_threads.id = chat_messages.thread_id
                WHERE chat_messages.id = message_citations.message_id
                AND chat_threads.user_id = auth.uid()
            )
        )
        """
    )
    op.execute(
        """
        CREATE POLICY source_documents_read_policy ON source_documents
        FOR SELECT TO authenticated
        USING (true)
        """
    )
    op.execute(
        """
        CREATE POLICY document_chunks_read_policy ON document_chunks
        FOR SELECT TO authenticated
        USING (true)
        """
    )


def downgrade() -> None:
    """Drop the initial schema in dependency order."""
    for table in (
        "message_citations",
        "document_chunks",
        "chat_messages",
        "source_documents",
        "chat_threads",
        "users",
    ):
        op.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
    op.execute("DROP EXTENSION IF EXISTS vector")
