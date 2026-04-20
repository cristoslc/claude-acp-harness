#!/usr/bin/env python3
"""Performance benchmark script for ACP Harness.

Measures latency and throughput across different payload sizes and concurrency levels.
"""

import argparse
import asyncio
import json
import statistics
import time
from dataclasses import asdict, dataclass, field
from typing import Optional

import httpx


@dataclass
class BenchmarkResult:
    """Single request result."""

    request_id: str
    latency_ms: float
    payload_size: int
    status_code: int
    success: bool
    error: Optional[str] = None


@dataclass
class BenchmarkSummary:
    """Aggregated benchmark results."""

    total_requests: int
    successful_requests: int
    failed_requests: int
    total_duration_sec: float
    requests_per_second: float
    latency_ms: dict[str, float] = field(default_factory=dict)
    payload_sizes: list[int] = field(default_factory=list)


def generate_payload(size: int) -> str:
    """Generate a payload of approximately the specified size in bytes."""
    # Use a repeating pattern that's compressible but realistic
    words = [
        "Analyze",
        "the",
        "following",
        "code",
        "and",
        "provide",
        "suggestions",
        "for",
        "improvement.",
        "Consider",
        "performance",
        "readability",
        "and",
        "maintainability.",
        "The",
        "function",
        "should",
        "handle",
        "edge",
        "cases",
        "gracefully.",
    ]
    text = " ".join(words * ((size // 50) + 1))
    return text[:size]


async def make_request(
    client: httpx.AsyncClient,
    base_url: str,
    payload_size: int,
    request_id: str,
) -> BenchmarkResult:
    """Make a single benchmark request."""
    start_time = time.time()

    try:
        response = await client.post(
            f"{base_url}/acp/call",
            json={
                "type": "prompt",
                "payload": generate_payload(payload_size),
                "timeout": 300,
            },
            timeout=300.0,
        )

        latency_ms = (time.time() - start_time) * 1000

        return BenchmarkResult(
            request_id=request_id,
            latency_ms=latency_ms,
            payload_size=payload_size,
            status_code=response.status_code,
            success=response.status_code == 200,
        )
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        return BenchmarkResult(
            request_id=request_id,
            latency_ms=latency_ms,
            payload_size=payload_size,
            status_code=0,
            success=False,
            error=str(e),
        )


async def run_concurrent_requests(
    base_url: str,
    num_requests: int,
    concurrency: int,
    payload_sizes: list[int],
) -> list[BenchmarkResult]:
    """Run benchmark requests with controlled concurrency."""
    results: list[BenchmarkResult] = []
    semaphore = asyncio.Semaphore(concurrency)

    async with httpx.AsyncClient() as client:

        async def bounded_request(i: int) -> BenchmarkResult:
            async with semaphore:
                payload_size = payload_sizes[i % len(payload_sizes)]
                return await make_request(
                    client,
                    base_url,
                    payload_size,
                    f"bench-{i}",
                )

        tasks = [bounded_request(i) for i in range(num_requests)]
        results = await asyncio.gather(*tasks)

    return results


def analyze_results(results: list[BenchmarkResult]) -> BenchmarkSummary:
    """Analyze benchmark results and compute statistics."""
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    latencies = [r.latency_ms for r in successful]

    summary = BenchmarkSummary(
        total_requests=len(results),
        successful_requests=len(successful),
        failed_requests=len(failed),
        total_duration_sec=sum(r.latency_ms for r in results) / 1000,
        requests_per_second=len(successful)
        / (sum(r.latency_ms for r in successful) / 1000)
        if successful
        else 0,
        payload_sizes=list(set(r.payload_size for r in results)),
    )

    if latencies:
        summary.latency_ms = {
            "min": round(min(latencies), 2),
            "max": round(max(latencies), 2),
            "mean": round(statistics.mean(latencies), 2),
            "median": round(statistics.median(latencies), 2),
            "p95": round(sorted(latencies)[int(len(latencies) * 0.95)], 2),
            "p99": round(sorted(latencies)[int(len(latencies) * 0.99)], 2),
        }

    return summary


def print_results(summary: BenchmarkSummary, results: list[BenchmarkResult]):
    """Print formatted benchmark results."""
    print("\n" + "=" * 60)
    print("ACP Harness Benchmark Results")
    print("=" * 60)

    print(f"\nTotal Requests: {summary.total_requests}")
    print(f"Successful: {summary.successful_requests}")
    print(f"Failed: {summary.failed_requests}")
    print(
        f"Success Rate: {summary.successful_requests / summary.total_requests * 100:.1f}%"
    )

    print(f"\nTotal Duration: {summary.total_duration_sec:.2f}s")
    print(f"Requests/Second: {summary.requests_per_second:.2f}")

    print("\nLatency (ms):")
    for metric, value in summary.latency_ms.items():
        print(f"  {metric.upper()}: {value}")

    if summary.failed_requests > 0:
        print("\nErrors:")
        errors: dict[str, int] = {}
        for r in results:
            if not r.success and r.error:
                errors[r.error] = errors.get(r.error, 0) + 1
        for error, count in sorted(errors.items(), key=lambda x: -x[1])[:5]:
            print(f"  {count}x: {error[:80]}...")

    print("=" * 60)


async def main() -> None:
    """Main benchmark entry point."""
    parser = argparse.ArgumentParser(
        description="Benchmark ACP Harness performance",
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL of the ACP Harness API",
    )
    parser.add_argument(
        "--requests",
        type=int,
        default=50,
        help="Total number of requests to make",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=5,
        help="Number of concurrent requests",
    )
    parser.add_argument(
        "--payload-sizes",
        nargs="+",
        type=int,
        default=[100, 500, 1000],
        help="Payload sizes to test (in bytes)",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file for detailed results (JSON)",
    )
    parser.add_argument(
        "--warmup",
        type=int,
        default=5,
        help="Number of warmup requests",
    )

    args = parser.parse_args()

    print("ACP Harness Benchmark")
    print(f"URL: {args.url}")
    print(f"Requests: {args.requests}")
    print(f"Concurrency: {args.concurrency}")
    print(f"Payload Sizes: {args.payload_sizes}")
    print(f"Warmup: {args.warmup}")

    # Warmup
    if args.warmup > 0:
        print(f"\nWarmup: {args.warmup} requests...")
        await run_concurrent_requests(
            args.url,
            args.warmup,
            args.concurrency,
            [args.payload_sizes[0]],
        )

    # Benchmark
    print(f"\nRunning benchmark: {args.requests} requests...")
    start_time = time.time()

    results = await run_concurrent_requests(
        args.url,
        args.requests,
        args.concurrency,
        args.payload_sizes,
    )

    actual_duration = time.time() - start_time

    summary = analyze_results(results)
    summary.total_duration_sec = actual_duration

    print_results(summary, results)

    # Save detailed results
    if args.output:
        output_data = {
            "summary": asdict(summary),
            "results": [
                {
                    "request_id": r.request_id,
                    "latency_ms": r.latency_ms,
                    "payload_size": r.payload_size,
                    "status_code": r.status_code,
                    "success": r.success,
                    "error": r.error,
                }
                for r in results
            ],
            "config": {
                "url": args.url,
                "requests": args.requests,
                "concurrency": args.concurrency,
                "payload_sizes": args.payload_sizes,
            },
        }
        with open(args.output, "w") as f:
            json.dump(output_data, f, indent=2)
        print(f"\nDetailed results saved to: {args.output}")


if __name__ == "__main__":
    asyncio.run(main())
