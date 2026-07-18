import os
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from llama_index.core import PromptTemplate, VectorStoreIndex
from llama_index.core.response_synthesizers import ResponseMode, get_response_synthesizer
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone

load_dotenv()

DEFAULT_CONFIDENCE_THRESHOLD = 0.2
DEFAULT_PINECONE_INDEX = "kiro"
DEFAULT_PINECONE_NAMESPACE = "kiro-shoshana"

TEXT_QA_TEMPLATE = PromptTemplate(
    """You are a helpful assistant.
    Answer the user's question using only the context below.
    If the context does not contain the answer, say that you do not know.

    Context:
    {context_str}

    Question:
    {query_str}

    Answer:"""
)


class WorkflowEvent(Enum):
    START = auto()
    QUERY_INVALID = auto()
    QUERY_VALID = auto()
    RETRIEVAL_EMPTY = auto()
    RETRIEVAL_SUCCESS = auto()
    RETRIEVAL_VALID = auto()
    NEEDS_MORE_CONTEXT = auto()
    SYNTHESIS_SUCCESS = auto()
    SYNTHESIS_FAILED = auto()


@dataclass
class WorkflowContext:
    query: str
    nodes: Optional[List[Any]] = None
    response: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StepResult:
    event: WorkflowEvent
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowResult:
    status: str
    message: str
    event: WorkflowEvent
    metadata: Dict[str, Any] = field(default_factory=dict)


def _get_environment_value(name: str, required: bool = True) -> Optional[str]:
    value = os.getenv(name)
    if required and not value:
        raise ValueError(f"{name} is missing from the environment")
    return value


def load_index() -> VectorStoreIndex:
    api_key = _get_environment_value("PINECONE_API_KEY")
    cohere_key = _get_environment_value("COHERE_API_KEY")

    pinecone_client = Pinecone(api_key=api_key)
    pinecone_index = pinecone_client.Index(DEFAULT_PINECONE_INDEX)

    vector_store = PineconeVectorStore(
        pinecone_index=pinecone_index,
        namespace=DEFAULT_PINECONE_NAMESPACE,
    )

    embed_model = CohereEmbedding(
        api_key=cohere_key,
        model_name="embed-english-v3.0",
        input_type="search_query",
    )

    return VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        embed_model=embed_model,
    )


def build_response_synthesizer() -> Any:
    api_key = _get_environment_value("GEMINI_API_KEY")
    llm = GoogleGenAI(api_key=api_key, model="models/gemini-2.5-flash", temperature=0.1)
    return get_response_synthesizer(
        llm=llm,
        text_qa_template=TEXT_QA_TEMPLATE,
        response_mode=ResponseMode.COMPACT,
    )


class RAGWorkflow:
    def __init__(
        self,
        retriever: Any,
        response_synthesizer: Any,
        confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
    ):
        self.retriever = retriever
        self.response_synthesizer = response_synthesizer
        self.confidence_threshold = confidence_threshold
        self.event_handlers = {
            WorkflowEvent.START: self._validate_query,
            WorkflowEvent.QUERY_VALID: self._retrieve_documents,
            WorkflowEvent.RETRIEVAL_SUCCESS: self._validate_retrieval,
            WorkflowEvent.RETRIEVAL_VALID: self._synthesize_response,
        }

    def run(self, query: str) -> WorkflowResult:
        context = WorkflowContext(query=query)
        current_event = WorkflowEvent.START

        while True:
            handler = self.event_handlers.get(current_event)
            if handler is None:
                break

            step_result = handler(context)
            context.metadata.update(step_result.payload)
            current_event = step_result.event

            if current_event in {
                WorkflowEvent.QUERY_INVALID,
                WorkflowEvent.RETRIEVAL_EMPTY,
                WorkflowEvent.NEEDS_MORE_CONTEXT,
                WorkflowEvent.SYNTHESIS_SUCCESS,
                WorkflowEvent.SYNTHESIS_FAILED,
            }:
                break

        return self._build_result(context, current_event)

    def _validate_query(self, context: WorkflowContext) -> StepResult:
        if not context.query or not context.query.strip():
            return StepResult(
                event=WorkflowEvent.QUERY_INVALID,
                payload={"error": "The question is empty. Please provide a query."},
            )

        if len(context.query.strip()) < 3:
            return StepResult(
                event=WorkflowEvent.QUERY_INVALID,
                payload={"error": "The question is too short. Please ask a more specific question."},
            )

        return StepResult(event=WorkflowEvent.QUERY_VALID)

    def _retrieve_documents(self, context: WorkflowContext) -> StepResult:
        nodes = self.retriever.retrieve(context.query)
        context.nodes = list(nodes) if nodes is not None else []

        if not context.nodes:
            return StepResult(
                event=WorkflowEvent.RETRIEVAL_EMPTY,
                payload={"error": "No relevant context found."},
            )

        return StepResult(event=WorkflowEvent.RETRIEVAL_SUCCESS)

    def _validate_retrieval(self, context: WorkflowContext) -> StepResult:
        scores = self._extract_scores(context.nodes)
        context.metadata["retrieval_scores"] = scores

        if scores and max(scores) < self.confidence_threshold:
            return StepResult(
                event=WorkflowEvent.NEEDS_MORE_CONTEXT,
                payload={
                    "error": (
                        "Search results are too weak for a confident answer. "
                        "Please provide more detail or change the question."
                    ),
                },
            )

        return StepResult(event=WorkflowEvent.RETRIEVAL_VALID)

    def _synthesize_response(self, context: WorkflowContext) -> StepResult:
        try:
            response = self.response_synthesizer.synthesize(context.query, nodes=context.nodes)
            context.response = str(response)
            return StepResult(event=WorkflowEvent.SYNTHESIS_SUCCESS)
        except Exception as exc:
            return StepResult(
                event=WorkflowEvent.SYNTHESIS_FAILED,
                payload={"error": f"Failed to synthesize an answer: {exc}"},
            )

    def _build_result(self, context: WorkflowContext, event: WorkflowEvent) -> WorkflowResult:
        if event == WorkflowEvent.SYNTHESIS_SUCCESS:
            return WorkflowResult(
                status="success",
                message=context.response or "",
                event=event,
                metadata=context.metadata,
            )

        error_message = context.metadata.get("error", "The workflow stopped before producing an answer.")
        return WorkflowResult(
            status="error",
            message=error_message,
            event=event,
            metadata=context.metadata,
        )

    def _extract_scores(self, nodes: List[Any]) -> List[float]:
        scores: List[float] = []
        for node in nodes:
            for candidate in ("score", "similarity", "_score", "node_score"):
                raw_value = getattr(node, candidate, None)
                if raw_value is None:
                    continue
                try:
                    scores.append(float(raw_value))
                except (TypeError, ValueError):
                    continue
                break
        return scores


def create_default_workflow() -> RAGWorkflow:
    index = load_index()
    retriever = index.as_retriever()
    response_synthesizer = build_response_synthesizer()
    return RAGWorkflow(retriever=retriever, response_synthesizer=response_synthesizer)
