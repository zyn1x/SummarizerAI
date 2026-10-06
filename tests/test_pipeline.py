import pytest
from httpx import AsyncClient, ASGITransport
from summarizerai.main import app
from summarizerai.database.session import init_db

@pytest.mark.asyncio
async def test_full_api_pipeline():
    await init_db()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Health check
        resp = await client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "llm" in data
        assert "default_provider" in data["llm"]

        # 2. Ingest a sample document (direct text via multipart file)
        test_content = b"""# Introduction to Neural Networks
Neural networks are computing systems inspired by the biological neural networks that constitute animal brains.
Such systems learn to perform tasks by considering examples, generally without being programmed with task-specific rules.

## Convolutional Neural Networks
CNNs are specialized neural structures for processing grid-structured data such as imagery.
They utilize parameter sharing and pooling layers to achieve spatial invariance.

## Transformers and Self-Attention
Introduced in 2017, the Transformer architecture discards recurrence completely.
Self-attention computes dynamic weights between token pairs, enabling parallel training over sequence length."""

        files = {"file": ("neural_networks.md", test_content, "text/markdown")}
        resp = await client.post("/api/ingest/file", files=files)
        assert resp.status_code == 200
        ingest_res = resp.json()
        assert "job_id" in ingest_res
        job_id = ingest_res["job_id"]

        # Wait or check job status
        resp = await client.get(f"/api/jobs/{job_id}")
        assert resp.status_code == 200

        # Fetch documents
        docs_resp = await client.get("/api/documents")
        assert docs_resp.status_code == 200
        docs = docs_resp.json()
        assert len(docs) >= 1
        doc_id = docs[0]["id"]

        # 3. Request Actionable Insights with Goal
        insights_payload = {
            "user_goal": "study_exam",
            "custom_context": "Focus on Convolutional Neural Networks and Transformers."
        }
        act_resp = await client.post(f"/api/documents/{doc_id}/actions/insights", json=insights_payload)
        assert act_resp.status_code == 200
        insights_data = act_resp.json()
        assert "STUDY" in insights_data["result_markdown"] or "Exam" in insights_data["result_markdown"]
        assert len(insights_data["citations"]) > 0

        # 4. Request Q&A
        qa_payload = {
            "question": "What architecture was introduced in 2017 and discards recurrence?",
            "top_k": 3
        }
        qa_resp = await client.post(f"/api/documents/{doc_id}/qa", json=qa_payload)
        assert qa_resp.status_code == 200
        qa_data = qa_resp.json()
        assert len(qa_data["answer"]) > 10
        assert len(qa_data["citations"]) > 0
