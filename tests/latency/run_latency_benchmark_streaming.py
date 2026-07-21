"""
Latency Benchmark for Legal RAG Pipeline (Streaming version).

Measures Time-To-First-Token (TTFT), per-node, and end-to-end latency across 10 sample queries.
Instruments the LangGraph pipeline directly via astream_events to catch token streams.

Usage:
    cd d:/CaNhan/LegalChatbot_FastAPI
    python tests/latency/run_latency_benchmark_streaming.py
"""

import sys
import os
import time
import json
import asyncio
import statistics
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from functools import wraps

# Allow importing app modules from project root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


# =========================================================
# 10 Sample Questions (diverse intents and complexity)
# =========================================================

BENCHMARK_QUESTIONS = [
    {
        "id": "Q01",
        "category": "penal",
        "question": "Tội giết người bị xử phạt như thế nào theo Bộ luật Hình sự?",
    },
    {
        "id": "Q02",
        "category": "civil",
        "question": "Quyền thừa kế theo pháp luật được quy định ra sao?",
    },
    {
        "id": "Q03",
        "category": "business",
        "question": "Phạm vi điều chỉnh của Luật Doanh nghiệp 2020 là gì?",
    },
    {
        "id": "Q04",
        "category": "marriage",
        "question": "Điều kiện kết hôn theo Luật Hôn nhân và Gia đình là gì?",
    },
    {
        "id": "Q05",
        "category": "procedure",
        "question": "Thủ tục đăng ký thành lập doanh nghiệp gồm những bước nào?",
    },
    {
        "id": "Q06",
        "category": "penal",
        "question": "Tội trộm cắp tài sản có giá trị từ 50 triệu trở lên bị xử phạt thế nào?",
    },
    {
        "id": "Q07",
        "category": "civil",
        "question": "Hợp đồng dân sự vô hiệu trong trường hợp nào?",
    },
    {
        "id": "Q08",
        "category": "business",
        "question": "Doanh nghiệp xã hội cần đáp ứng những tiêu chí gì?",
    },
    {
        "id": "Q09",
        "category": "marriage",
        "question": "Quyền và nghĩa vụ của cha mẹ đối với con cái theo luật hôn nhân gia đình?",
    },
    {
        "id": "Q10",
        "category": "procedure",
        "question": "Quy trình giải quyết tranh chấp lao động cá nhân được thực hiện như thế nào?",
    },
]


# =========================================================
# Node Timing Instrumentation
# =========================================================

class NodeTimer:
    """Collects timing data for each node in a single pipeline run."""

    def __init__(self):
        self.timings: Dict[str, float] = {}
        self.sub_timings: Dict[str, Dict[str, float]] = {}

    def record(self, node_name: str, duration: float):
        """Record total time for a node."""
        self.timings[node_name] = duration

    def record_sub(self, node_name: str, sub_step: str, duration: float):
        """Record sub-step time within a node (e.g., embedding vs qdrant_search)."""
        if node_name not in self.sub_timings:
            self.sub_timings[node_name] = {}
        self.sub_timings[node_name][sub_step] = duration


def wrap_node(original_fn, node_name: str, timer: NodeTimer):
    """Wrap a node function to measure its execution time. Supports both async and sync."""
    if asyncio.iscoroutinefunction(original_fn):
        @wraps(original_fn)
        async def timed_async_node(state):
            start = time.perf_counter()
            result = await original_fn(state)
            elapsed = time.perf_counter() - start
            timer.record(node_name, elapsed)
            return result
        return timed_async_node
    else:
        @wraps(original_fn)
        def timed_node(state):
            start = time.perf_counter()
            result = original_fn(state)
            elapsed = time.perf_counter() - start
            timer.record(node_name, elapsed)
            return result
        return timed_node


def wrap_retriever_with_substeps(timer: NodeTimer):
    """
    Build an instrumented retriever that measures sub-steps.
    """
    from app.core.config import settings
    from app.core.clients import get_qdrant_client, get_embeddings
    from app.services.law_agent.state import LawAgentState, RetrievedDocument
    from app.services.law_agent.nodes.retrieval_agent import (
        HARD_THRESHOLD,
        DOMAIN_KEYWORDS,
    )

    def instrumented_retriever(state: LawAgentState) -> LawAgentState:
        total_start = time.perf_counter()

        try:
            query = state.standalone_query or state.query
            is_procedural = state.intent == "SEARCH_PROCEDURE"
            limit = state.search_limit or (3 if is_procedural else 4)

            qdrant = get_qdrant_client()
            embeddings = get_embeddings()

            # Sub-step 1: Embedding
            t0 = time.perf_counter()
            query_vector = embeddings.embed_query(query)
            timer.record_sub("retriever", "embedding", time.perf_counter() - t0)

            # Sub-step 2: Qdrant search
            t0 = time.perf_counter()
            results = qdrant.query_points(
                collection_name=settings.COLLECTION_NAME,
                query=query_vector,
                limit=limit,
                with_payload=True,
            ).points
            timer.record_sub("retriever", "qdrant_search", time.perf_counter() - t0)

            # Sub-step 3: Filtering
            t0 = time.perf_counter()
            documents = []
            for hit in results:
                score = hit.score
                payload = hit.payload or {}
                loai_van_ban = payload.get("loai_van_ban", "")

                if score < HARD_THRESHOLD:
                    continue

                domain_filter = DOMAIN_KEYWORDS.get(state.intent, [])
                if domain_filter and not any(kw in loai_van_ban for kw in domain_filter):
                    continue

                content = payload.get("page_content") or payload.get(
                    "combine_Article_Content", ""
                )
                documents.append(
                    RetrievedDocument(
                        law_id=payload.get("so_hieu", ""),
                        law_name=payload.get("loai_van_ban", ""),
                        content=content,
                        score=score,
                    )
                )
            timer.record_sub("retriever", "filtering", time.perf_counter() - t0)

            state.retrieved_docs = documents
            if not documents:
                state.check_status = "NO_LAW"
            state.node_trace.append("retriever")

        except Exception as e:
            state.error_message = f"Retriever error: {str(e)}"
            state.check_status = "NO_LAW"

        timer.record("retriever", time.perf_counter() - total_start)
        return state

    return instrumented_retriever


# =========================================================
# Build Instrumented Graph
# =========================================================

def build_instrumented_graph(timer: NodeTimer):
    """Compile a LangGraph pipeline with timing wrappers on every node."""
    from langgraph.graph import StateGraph, END
    from typing import Literal
    from app.services.law_agent.state import LawAgentState

    # Import original node functions
    from app.services.law_agent.nodes.contextualize_agent import contextualize_node
    from app.services.law_agent.nodes.router_agent import router_node
    from app.services.law_agent.nodes.checker_agent import sufficiency_checker_node
    from app.services.law_agent.nodes.writer_agent import answer_node
    from app.services.law_agent.nodes.fallback_agent import fallback_node
    from app.services.law_agent.nodes.clarifier_agent import clarifier_node

    workflow = StateGraph(LawAgentState)

    # Register instrumented nodes
    workflow.add_node("contextualize", wrap_node(contextualize_node, "contextualize", timer))
    workflow.add_node("router", wrap_node(router_node, "router", timer))
    workflow.add_node("retriever", wrap_retriever_with_substeps(timer))
    workflow.add_node("checker", wrap_node(sufficiency_checker_node, "checker", timer))
    workflow.add_node("answer", wrap_node(answer_node, "answer", timer))
    workflow.add_node("fallback", wrap_node(fallback_node, "fallback", timer))
    workflow.add_node("clarifier", wrap_node(clarifier_node, "clarifier", timer))

    # Same graph topology as production
    workflow.set_entry_point("contextualize")
    workflow.add_edge("contextualize", "router")
    workflow.add_edge("router", "retriever")
    workflow.add_edge("retriever", "checker")

    def route_after_check(state: LawAgentState) -> Literal["answer", "clarifier", "fallback"]:
        if state.check_status is None:
            return "fallback"
        if state.check_status == "SUFFICIENT":
            return "answer"
        if state.check_status == "MISSING_INFO":
            return "clarifier"
        return "fallback"

    workflow.add_conditional_edges(
        "checker",
        route_after_check,
        {"answer": "answer", "clarifier": "clarifier", "fallback": "fallback"},
    )

    workflow.add_edge("answer", END)
    workflow.add_edge("clarifier", END)
    workflow.add_edge("fallback", END)

    return workflow.compile()


# =========================================================
# Single Query Runner
# =========================================================

async def run_single_query_streaming(question_data: dict, timer: NodeTimer) -> Dict[str, Any]:
    """Run one query through the instrumented pipeline using astream_events to get TTFT."""
    graph = build_instrumented_graph(timer)

    inputs = {
        "query": question_data["question"],
        "chat_history": "",
    }

    e2e_start = time.perf_counter()
    ttft_elapsed = None
    first_token_received = False
    
    full_answer = ""
    output_state = {}

    # Stream events instead of ainvoke
    async for event in graph.astream_events(inputs, version="v2"):
        if event["event"] == "on_chat_model_stream":
            if "writer_node_llm" in event.get("tags", []):
                chunk_text = event["data"]["chunk"].content
                if chunk_text and not first_token_received:
                    ttft_elapsed = time.perf_counter() - e2e_start
                    first_token_received = True
                if chunk_text:
                    full_answer += chunk_text
                    
        if event["event"] == "on_chain_end" and event["name"] == "LangGraph":
            output_state = event["data"]["output"]
            if not full_answer and output_state.get("generation"):
                full_answer = output_state.get("generation", "")

    e2e_elapsed = time.perf_counter() - e2e_start
    
    # If the response doesn't stream (e.g. clarifier or fallback), TTFT is essentially equal to E2E
    if ttft_elapsed is None:
        ttft_elapsed = e2e_elapsed

    node_trace = output_state.get("node_trace", [])
    terminal_node = node_trace[-1] if node_trace else "unknown"

    return {
        "question_id": question_data["id"],
        "category": question_data["category"],
        "question": question_data["question"],
        "terminal_node": terminal_node,
        "node_trace": node_trace,
        "ttft_s": round(ttft_elapsed, 4),
        "e2e_latency_s": round(e2e_elapsed, 4),
        "node_latencies_s": {k: round(v, 4) for k, v in timer.timings.items()},
        "retriever_substeps_s": {
            k: round(v, 4) for k, v in timer.sub_timings.get("retriever", {}).items()
        },
        "full_answer": full_answer,
        "num_docs_retrieved": len(output_state.get("retrieved_docs", [])),
    }


# =========================================================
# Aggregation and Reporting
# =========================================================

def compute_statistics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute aggregate statistics from individual query results."""

    e2e_times = [r["e2e_latency_s"] for r in results]
    ttft_times = [r["ttft_s"] for r in results]

    # Collect per-node latency lists
    all_node_names = set()
    for r in results:
        all_node_names.update(r["node_latencies_s"].keys())

    node_stats = {}
    for name in sorted(all_node_names):
        values = [r["node_latencies_s"].get(name, 0) for r in results if name in r["node_latencies_s"]]
        if values:
            node_stats[name] = {
                "mean_s": round(statistics.mean(values), 4),
                "median_s": round(statistics.median(values), 4),
                "min_s": round(min(values), 4),
                "max_s": round(max(values), 4),
                "stdev_s": round(statistics.stdev(values), 4) if len(values) > 1 else 0,
                "count": len(values),
            }

    # Retriever sub-step stats
    substep_names = set()
    for r in results:
        substep_names.update(r["retriever_substeps_s"].keys())

    retriever_substep_stats = {}
    for name in sorted(substep_names):
        values = [r["retriever_substeps_s"].get(name, 0) for r in results if name in r["retriever_substeps_s"]]
        if values:
            retriever_substep_stats[name] = {
                "mean_s": round(statistics.mean(values), 4),
                "median_s": round(statistics.median(values), 4),
                "min_s": round(min(values), 4),
                "max_s": round(max(values), 4),
            }

    slowest_node = max(node_stats, key=lambda n: node_stats[n]["mean_s"]) if node_stats else "N/A"

    return {
        "total_queries": len(results),
        "e2e_stats": {
            "mean_s": round(statistics.mean(e2e_times), 4),
            "median_s": round(statistics.median(e2e_times), 4),
            "min_s": round(min(e2e_times), 4),
            "max_s": round(max(e2e_times), 4),
            "stdev_s": round(statistics.stdev(e2e_times), 4) if len(e2e_times) > 1 else 0,
            "p90_s": round(sorted(e2e_times)[int(len(e2e_times) * 0.9)], 4),
        },
        "ttft_stats": {
            "mean_s": round(statistics.mean(ttft_times), 4),
            "median_s": round(statistics.median(ttft_times), 4),
            "min_s": round(min(ttft_times), 4),
            "max_s": round(max(ttft_times), 4),
        },
        "per_node_stats": node_stats,
        "retriever_substep_stats": retriever_substep_stats,
        "slowest_node": slowest_node,
        "slowest_node_mean_s": node_stats.get(slowest_node, {}).get("mean_s", 0),
    }


def format_report(results: List[Dict[str, Any]], stats: Dict[str, Any]) -> str:
    """Build a human-readable markdown report from benchmark results."""
    lines = []
    lines.append("# Streaming RAG Pipeline Latency Benchmark Report")
    lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Total queries: {stats['total_queries']}")

    # End-to-end and TTFT summary
    lines.append("\n## 1. Latency Summary")
    lines.append("")
    lines.append("| Metric | E2E Value | TTFT Value |")
    lines.append("|--------|-----------|------------|")
    for key in stats["e2e_stats"].keys():
        label = key.replace("_s", "").replace("_", " ").upper()
        e2e_val = stats["e2e_stats"].get(key, 0)
        ttft_val = stats["ttft_stats"].get(key, "-")
        ttft_str = f"{ttft_val:.4f}s" if isinstance(ttft_val, (int, float)) else ttft_val
        lines.append(f"| {label} | {e2e_val:.4f}s | {ttft_str} |")

    # Per-node breakdown
    lines.append("\n## 2. Per-Node Latency Breakdown (seconds)")
    lines.append("")
    lines.append("| Node | Mean | Median | Min | Max | Stdev | Runs |")
    lines.append("|------|------|--------|-----|-----|-------|------|")
    for name, s in stats["per_node_stats"].items():
        lines.append(
            f"| {name} | {s['mean_s']:.4f} | {s['median_s']:.4f} | "
            f"{s['min_s']:.4f} | {s['max_s']:.4f} | {s['stdev_s']:.4f} | {s['count']} |"
        )

    lines.append(f"\n**Slowest node (avg):** `{stats['slowest_node']}` at {stats['slowest_node_mean_s']:.4f}s")

    # Retriever sub-step analysis
    lines.append("\n## 3. Retriever Sub-Step Analysis (seconds)")
    lines.append("")
    lines.append("| Sub-Step | Mean | Median | Min | Max |")
    lines.append("|----------|------|--------|-----|-----|")
    for name, s in stats["retriever_substep_stats"].items():
        lines.append(
            f"| {name} | {s['mean_s']:.4f} | {s['median_s']:.4f} | "
            f"{s['min_s']:.4f} | {s['max_s']:.4f} |"
        )

    # Per-query detailed results
    lines.append("\n## 4. Per-Query Detail")
    lines.append("")
    for i, r in enumerate(results):
        lines.append(f"### 4.{i+1}. [{r['question_id']}] {r['category'].upper()}")
        lines.append("")
        lines.append(f"**Question:** {r['question']}")
        lines.append("")
        lines.append(f"**Latency:** TTFT: {r['ttft_s']:.4f}s | E2E: {r['e2e_latency_s']:.4f}s total | "
                     f"Docs retrieved: {r['num_docs_retrieved']} | "
                     f"Path: {' -> '.join(r['node_trace'])}")
        lines.append("")

    # Compact summary table
    lines.append("## 5. Quick Comparison Table")
    lines.append("")
    lines.append("| ID | Category | TTFT (s) | E2E (s) | Docs | Terminal | Question |")
    lines.append("|----|----------|----------|---------|------|----------|----------|")
    for r in results:
        q_short = r["question"][:40] + ("..." if len(r["question"]) > 40 else "")
        lines.append(
            f"| {r['question_id']} | {r['category']} | {r['ttft_s']:.4f} | {r['e2e_latency_s']:.4f} | "
            f"{r['num_docs_retrieved']} | {r['terminal_node']} | {q_short} |"
        )

    return "\n".join(lines)


# =========================================================
# Main Entry Point
# =========================================================

async def main():
    print("=" * 60)
    print("  RAG Pipeline Latency Benchmark (Streaming)")
    print("=" * 60)

    from app.core.clients import init_clients
    print("\n[INIT] Initializing clients (Qdrant, Embeddings, LLM, Redis)...")
    init_clients()
    print("[INIT] All clients ready.\n")

    results = []

    for i, q in enumerate(BENCHMARK_QUESTIONS):
        print(f"\n--- [{i+1}/{len(BENCHMARK_QUESTIONS)}] {q['id']}: {q['question'][:60]}...")
        timer = NodeTimer()

        try:
            result = await run_single_query_streaming(q, timer)
            results.append(result)
            print(f"    TTFT: {result['ttft_s']:.4f}s | "
                  f"E2E: {result['e2e_latency_s']:.4f}s | "
                  f"Docs: {result['num_docs_retrieved']} | "
                  f"Path: {' -> '.join(result['node_trace'])}")
        except Exception as e:
            print(f"    ERROR: {e}")
            results.append({
                "question_id": q["id"],
                "category": q["category"],
                "question": q["question"],
                "terminal_node": "ERROR",
                "node_trace": [],
                "ttft_s": 0,
                "e2e_latency_s": 0,
                "node_latencies_s": {},
                "retriever_substeps_s": {},
                "full_answer": f"ERROR: {str(e)}",
                "num_docs_retrieved": 0,
            })

    valid_results = [r for r in results if r["terminal_node"] != "ERROR"]
    stats = compute_statistics(valid_results) if valid_results else {}

    output_dir = Path(__file__).parent / "results"
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    json_path = output_dir / f"latency_stream_raw_{timestamp}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"results": results, "statistics": stats}, f, indent=2, ensure_ascii=False)

    if valid_results and stats:
        report = format_report(results, stats)
        md_path = output_dir / f"latency_stream_report_{timestamp}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\n[SAVED] Report: {md_path}")

    print(f"[SAVED] Raw data: {json_path}")

    if stats:
        print("\n" + "=" * 60)
        print("  SUMMARY")
        print("=" * 60)
        print(f"  Mean TTFT:           {stats['ttft_stats']['mean_s']:.4f}s")
        print(f"  Mean E2E latency:    {stats['e2e_stats']['mean_s']:.4f}s")
        print(f"  Median TTFT:         {stats['ttft_stats']['median_s']:.4f}s")
        print(f"  Slowest node (avg):  {stats['slowest_node']} ({stats['slowest_node_mean_s']:.4f}s)")


if __name__ == "__main__":
    asyncio.run(main())
