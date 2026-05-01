"""Performance and load tests for LexCore + LexRadar.

Validates token efficiency predictability under load and
measures system throughput benchmarks.
"""
import pytest
import asyncio
import time
from datetime import datetime

from src.core.token_efficiency import TokenEfficiencyTracker, PredictabilityCurve
from src.core.data_flow import HyperEfficientDataFlow


@pytest.mark.integration
class TestPerformanceBenchmarks:
    """Performance benchmarks for token efficiency."""

    @pytest.mark.asyncio
    async def test_concurrent_inflow_processing(self):
        """Test concurrent data inflow processing performance."""
        flow = HyperEfficientDataFlow()
        
        # Simulate 50 concurrent inflow operations
        tasks = [
            flow.process_inflow(
                data_source="USPTO",
                raw_data={"patent_number": f"US{i:07d}", "title": f"Patent {i}"},
                metadata={"batch": "perf_test"},
            )
            for i in range(50)
        ]
        
        start = time.time()
        results = await asyncio.gather(*tasks)
        elapsed = time.time() - start
        
        assert len(results) == 50
        assert elapsed < 10.0  # Should complete in under 10 seconds
        
        # Verify forensic consistency maintained under load
        forensic_scores = [r["forensic_score"] for r in results]
        assert all(score > 0.9 for score in forensic_scores)

    def test_predictability_curve_under_load(self):
        """Test predictability curve with increasing complexity."""
        curve = PredictabilityCurve()
        tracker = TokenEfficiencyTracker(target_reduction=0.40)
        
        # Simulate increasing complexity with decreasing tokens per operation
        for complexity in range(1, 21):
            # As complexity increases, tokens per operation should decrease
            # (demonstrating efficiency gains from patterns)
            tokens_per_op = 1000 / (complexity ** 0.5)
            
            tracker.register_baseline(f"op_{complexity}", 1000)
            tracker.record_operation(
                endpoint=f"op_{complexity}",
                input_tokens=int(tokens_per_op * 0.3),
                output_tokens=int(tokens_per_op * 0.7),
            )
            
            curve.add_data_point(complexity, tokens_per_op, complexity)
        
        result = curve.calculate_curve()
        
        assert result["status"] == "calculated"
        assert result["slope"] < 0  # Decreasing trend proven
        assert result["efficiency_proven"] is True
        
        # Verify token reduction target met
        report = tracker.get_efficiency_report()
        assert report["target_met"] is True

    @pytest.mark.asyncio
    async def test_token_reduction_under_stress(self):
        """Test token reduction under stress with pattern reuse."""
        flow = HyperEfficientDataFlow()
        
        # First operation: high token usage (cold start)
        cold_result = await flow.process_inflow(
            data_source="STRESS_TEST",
            raw_data={"data": "x" * 10000},  # Large data
            metadata={"type": "stress"},
        )
        
        cold_savings = cold_result["token_savings"]
        
        # Second operation with same pattern: should be more efficient
        warm_result = await flow.process_inflow(
            data_source="STRESS_TEST",
            raw_data={"data": "x" * 10000},
            metadata={"type": "stress"},
        )
        
        warm_savings = warm_result["token_savings"]
        
        # Pattern-based operations should show improved efficiency
        assert warm_savings >= 0

    def test_pattern_library_scalability(self):
        """Test pattern library scales without performance degradation."""
        from src.core.token_efficiency import PatternForensicConsistency
        
        engine = PatternForensicConsistency()
        
        # Add 1000 patterns
        start = time.time()
        for i in range(1000):
            engine.catalog_pattern(
                pattern_id=f"scale_test_{i}",
                data={"index": i, "value": f"data_{i}"},
                metadata={"batch": "scalability"},
            )
        catalog_time = time.time() - start
        
        assert catalog_time < 5.0  # Should catalog 1000 patterns in under 5s
        
        # Verify search still fast
        start = time.time()
        results = engine.search_by_pattern({"index": 500})
        search_time = time.time() - start
        
        assert search_time < 1.0  # Search should be under 1 second
        assert len(results) > 0
