from src.ai import LangGraphWorkflow, RAGPipeline
from src.ai.rag_pipeline import InMemoryRetriever


def test_inmemory_retriever_filters_documents():
    retriever = InMemoryRetriever(["alpha", "beta", "Alfa Beta"])
    assert retriever.retrieve("beta") == ["beta", "Alfa Beta"]


def test_rag_pipeline_fallback_without_dependencies():
    retriever = InMemoryRetriever(["alpha context", "other"])
    pipeline = RAGPipeline(retriever=retriever)
    response = pipeline.answer("alpha")
    assert "alpha context" in response.answer or "fallback" in response.answer
    assert response.sources == ["alpha context"]


def test_langgraph_workflow_applies_steps():
    workflow = LangGraphWorkflow()

    def step1(state):
        return {"a": state.get("a", 0) + 1}

    def step2(state):
        return {"b": state["a"] * 2}

    workflow.add_step(step1)
    workflow.add_step(step2)

    result = workflow.run({"a": 1})
    assert result == {"a": 2, "b": 4}
