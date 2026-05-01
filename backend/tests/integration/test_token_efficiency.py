"""Integration tests for token efficiency and predictability curve."""
import pytest
from datetime import datetime

from src.core.token_efficiency import (
    TokenEfficiencyTracker,
    PatternForensicConsistency,
    PredictabilityCurve,
)
from src.core.data_flow import HyperEfficientDataFlow, DataFlowStage


@pytest.mark.integration
class TestTokenEfficiency:
    """Test token efficiency tracking and optimization."""

    def test_tracker_initialization(self):
        """Test tracker initializes with correct target reduction."""
        tracker = TokenEfficiencyTracker(target_reduction=0.40)
        assert tracker.target_reduction == 0.40
        assert len(tracker.metrics) == 0

    def test_baseline_registration(self):
        """Test baseline token registration."""
        tracker = TokenEfficiencyTracker()
        tracker.register_baseline("/api/v1/documents", 1000)
        assert "/api/v1/documents" in tracker.baseline_tokens
        assert tracker.baseline_tokens["/api/v1/documents"] == 1000

    def test_operation_recording(self):
        """Test recording token usage for an operation."""
        tracker = TokenEfficiencyTracker()
        tracker.register_baseline("/api/v1/documents", 1000)
        
        metric = tracker.record_operation(
            endpoint="/api/v1/documents",
            input_tokens=200,
            output_tokens=300,
        )
        
        assert metric.endpoint == "/api/v1/documents"
        assert metric.total_tokens == 500
        assert metric.compression_ratio > 1.0  # 1000/500 = 2.0

    def test_efficiency_report(self):
        """Test efficiency report generation."""
        tracker = TokenEfficiencyTracker()
        tracker.register_baseline("/api/v1/documents", 1000)
        tracker.record_operation("/api/v1/documents", 200, 300)
        
        report = tracker.get_efficiency_report()
        assert report["total_operations"] == 1
        assert report["reduction_percentage"] == 50.0
        assert report["target_met"] is True

    def test_pattern_match_score(self):
        """Test pattern match scoring."""
        tracker = TokenEfficiencyTracker()
        tracker.register_baseline("/api/v1/documents", 1000)
        tracker.pattern_cache["test_pattern"] = "cached"
        
        metric = tracker.record_operation(
            endpoint="/api/v1/documents",
            input_tokens=200,
            output_tokens=300,
            pattern_used="test_pattern",
        )
        
        assert metric.pattern_match_score == 0.95


@pytest.mark.integration
class TestPatternForensicConsistency:
    """Test pattern forensic consistency engine."""

    def test_morse_binary_encoding(self):
        """Test morse binary encoding and decoding."""
        engine = PatternForensicConsistency()
        
        # Test simple encoding
        encoded = engine.encode_morse_binary("ABC")
        assert len(encoded) > 0
        assert isinstance(encoded, str)

    def test_pattern_cataloging(self):
        """Test pattern cataloging with forensic consistency."""
        engine = PatternForensicConsistency()
        
        result = engine.catalog_pattern(
            pattern_id="test_001",
            data={"title": "Test Patent", "inventors": ["Alice", "Bob"]},
            metadata={"source": "USPTO", "date": "2024-01-01"},
        )
        
        assert "forward_hash" in result
        assert "reverse_hash" in result
        assert "morse_binary" in result
        assert result["pattern_id"] == "test_001"

    def test_consistency_verification(self):
        """Test multi-directional consistency verification."""
        engine = PatternForensicConsistency()
        
        engine.catalog_pattern(
            pattern_id="test_002",
            data={"claim": "A method for..."},
            metadata={"type": "patent_claim"},
        )
        
        verification = engine.verify_consistency("test_002")
        assert verification["status"] == "consistent"
        assert verification["consistency_score"] == 1.0
        assert verification["forward_match"] is True
        assert verification["reverse_match"] is True

    def test_pattern_search(self):
        """Test pattern search functionality."""
        engine = PatternForensicConsistency()
        
        engine.catalog_pattern(
            pattern_id="search_test",
            data={"keyword": "semiconductor", "classification": "H01L"},
            metadata={"jurisdiction": "US"},
        )
        
        results = engine.search_by_pattern({"keyword": "semiconductor"})
        assert len(results) > 0
        assert results[0]["match_type"] in ["exact", "partial"]


@pytest.mark.integration
class TestPredictabilityCurve:
    """Test predictability curve generation and validation."""

    def test_curve_initialization(self):
        """Test curve initialization."""
        curve = PredictabilityCurve()
        assert len(curve.data_points) == 0
        assert curve.statistical_confidence == 0.95

    def test_data_point_addition(self):
        """Test adding data points to curve."""
        curve = PredictabilityCurve()
        curve.add_data_point(complexity_score=1, tokens_per_operation=100.0, feature_count=1)
        
        assert len(curve.data_points) == 1
        assert curve.data_points[0]["complexity_score"] == 1

    def test_curve_calculation(self):
        """Test predictability curve calculation."""
        curve = PredictabilityCurve()
        
        # Add monotonically decreasing points
        curve.add_data_point(1, 100.0, 1)
        curve.add_data_point(2, 80.0, 2)
        curve.add_data_point(3, 60.0, 3)
        curve.add_data_point(4, 45.0, 4)
        
        result = curve.calculate_curve()
        assert result["status"] == "calculated"
        assert result["slope"] < 0  # Decreasing trend
        assert result["is_monotonically_decreasing"] is True

    def test_efficiency_proven(self):
        """Test efficiency proof with sufficient data."""
        curve = PredictabilityCurve()
        
        # Generate strong decreasing trend
        for i in range(1, 11):
            curve.add_data_point(i, 100.0 / i, i)
        
        result = curve.calculate_curve()
        assert result["efficiency_proven"] is True
        assert result["statistical_significance"] is True

    def test_insufficient_data(self):
        """Test handling of insufficient data."""
        curve = PredictabilityCurve()
        result = curve.calculate_curve()
        
        assert result["status"] == "insufficient_data"
        assert result["points_required"] == 2

    def test_recommendations(self):
        """Test recommendation generation."""
        curve = PredictabilityCurve()
        curve.add_data_point(1, 100.0, 1)
        curve.add_data_point(2, 120.0, 2)  # Increasing - not efficient
        
        recommendations = curve.get_recommendations()
        assert len(recommendations) > 0
        assert any("pattern caching" in r.lower() for r in recommendations)


@pytest.mark.integration
class TestHyperEfficientDataFlow:
    """Test hyper-efficient data flow orchestration."""

    @pytest.fixture
    def data_flow(self):
        return HyperEfficientDataFlow()

    @pytest.mark.asyncio
    async def test_inflow_processing(self, data_flow):
        """Test data inflow processing."""
        result = await data_flow.process_inflow(
            data_source="USPTO",
            raw_data={"patent_number": "US1234567", "title": "Test"},
            metadata={"jurisdiction": "US", "type": "patent"},
        )
        
        assert "pattern_id" in result
        assert "consistency_verified" in result
        assert "token_savings" in result
        assert result["forensic_score"] > 0

    @pytest.mark.asyncio
    async def test_analysis_processing(self, data_flow):
        """Test analysis processing."""
        # First catalog a pattern
        inflow = await data_flow.process_inflow(
            data_source="USPTO",
            raw_data={"claim": "A system comprising..."},
            metadata={},
        )
        
        result = await data_flow.process_analysis(
            pattern_id=inflow["pattern_id"],
            analysis_type="prior_art_search",
            parameters={"jurisdiction": "US", "date_range": "2020-2024"},
        )
        
        assert result["status"] == "completed"
        assert "token_cost" in result

    @pytest.mark.asyncio
    async def test_outflow_processing(self, data_flow):
        """Test outflow distribution."""
        analysis_result = {
            "status": "completed",
            "pattern_id": "test_123",
            "forensic_score": 0.98,
        }
        
        result = await data_flow.process_outflow(
            analysis_results=analysis_result,
            output_format="compressed",
        )
        
        assert result["status"] == "distributed"
        assert "compression_ratio" in result
        assert result["quality_score"] > 0.9

    @pytest.mark.asyncio
    async def test_full_pipeline(self, data_flow):
        """Test complete inflow → analysis → outflow pipeline."""
        result = await data_flow.execute_full_pipeline(
            data_source="USPTO",
            raw_data={"invention": "Test invention", "claims": ["Claim 1", "Claim 2"]},
            analysis_type="novelty_check",
            parameters={"threshold": 0.85, "jurisdiction": "US"},
        )
        
        assert result["status"] == "completed"
        assert result["pipeline_stages"] == 3
        assert "inflow" in result
        assert "analysis" in result
        assert "outflow" in result
        assert "predictability" in result

    def test_efficiency_dashboard(self, data_flow):
        """Test efficiency dashboard generation."""
        dashboard = data_flow.get_efficiency_dashboard()
        
        assert "token_tracker" in dashboard
        assert "predictability_curve" in dashboard
        assert "pattern_library_size" in dashboard
        assert "recommendations" in dashboard
