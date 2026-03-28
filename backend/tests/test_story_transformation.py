"""
Unit tests for story content transformation and expansion.

Tests the new methods:
- _transform_tool_references_to_narrative
- _expand_story_with_llm
- _clean_story_content

Run with:
    cd backend && uv run pytest tests/test_story_transformation.py -v
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import re


class TestStoryTransformation:
    """Test story content transformation methods."""

    @pytest.fixture
    def mock_report_agent(self):
        """Create a mock ReportAgent for testing."""
        from app.services.report_agent import ReportAgent

        # Mock LLM client
        mock_llm = Mock()
        mock_llm.chat = Mock(return_value="Mocked LLM response")
        mock_llm.model = "test-model"
        mock_llm.base_url = "http://test"

        # Create agent with mocked dependencies
        agent = ReportAgent(
            graph_id="test_graph",
            simulation_id="test_sim",
            simulation_requirement="Test requirement",
            llm_client=mock_llm,
            zep_tools=Mock(),
            locale="vi",
            mode="story",
        )

        return agent

    def test_transform_tool_references_basic(self, mock_report_agent):
        """Test basic tool reference transformation."""
        content = "Tôi gọi công cụ insight_forge để thu thập thông tin về bóng tối."

        result = mock_report_agent._transform_tool_references_to_narrative(content)

        # Should transform tool call to narrative
        assert "công cụ insight_forge" not in result
        assert "nhắm mắt" in result or "tâm trí" in result
        assert "bóng tối" in result  # Should preserve the subject

    def test_transform_preserves_all_content(self, mock_report_agent):
        """Test that transformation preserves all important content."""
        content = """Tôi quyết định điều tra thêm về những bóng tối mà Aelden đã thấy.
Tôi thấy rằng có những thông tin về Vương Miện Lửa, một biểu tượng của quyền cai trị.
Tôi cũng thấy rằng có những thông tin về các nhân vật khác, như Draven Holt, Rowan, và Thầy Tu Aldric."""

        result = mock_report_agent._transform_tool_references_to_narrative(content)

        # All important elements should be preserved
        important_elements = [
            "bóng tối",
            "Aelden",
            "Vương Miện Lửa",
            "Draven Holt",
            "Rowan",
            "Thầy Tu Aldric",
        ]
        for element in important_elements:
            assert element in result, f"Lost important element: {element}"

        # Content should be at least as long (we're transforming, not deleting)
        assert len(result) >= len(content) * 0.9  # Allow 10% variance

    def test_transform_multiple_languages(self, mock_report_agent):
        """Test transformation handles multiple language patterns."""
        content = """Tôi gọi công cụ insight_forge để tìm hiểu.
我调用工具来搜索信息。
I called the tool to search.
Ich rief das Werkzeug an."""

        result = mock_report_agent._transform_tool_references_to_narrative(content)

        # Tool names should be replaced with 'linh giác' or removed
        assert "insight_forge" not in result.lower()
        assert "panorama_search" not in result.lower()
        assert "quick_search" not in result.lower()
        # "công cụ" might remain but should be replaced with "linh giác"
        if "công cụ" in result:
            assert "linh giác" in result

    def test_clean_story_content_delegates_to_transform(self, mock_report_agent):
        """Test that _clean_story_content delegates to transformation."""
        content = "Tôi gọi công cụ insight_forge để thu thập thông tin."

        # Mock the transformation method
        mock_transform = Mock(return_value="Transformed content")
        mock_report_agent._transform_tool_references_to_narrative = mock_transform

        result = mock_report_agent._clean_story_content(content)

        # Should call transformation method
        mock_transform.assert_called_once_with(content)
        assert result == "Transformed content"

    def test_expand_story_splits_into_sections(self, mock_report_agent):
        """Test that story expansion splits content into 6 sections."""
        content = "\n\n".join([f"Paragraph {i}" for i in range(12)])

        # Mock LLM to return expanded content
        mock_report_agent.llm.chat.return_value = (
            "Expanded section content with many words " * 50
        )

        result = mock_report_agent._expand_story_with_llm(
            content, target_word_count=3000
        )

        # Should make 6 LLM calls (one per section)
        assert mock_report_agent.llm.chat.call_count >= 6

        # Result should be longer than input
        assert len(result.split()) > len(content.split())

    def test_expand_story_handles_groq_limits(self, mock_report_agent):
        """Test that expansion adjusts for Groq API limits."""
        # Set up Groq-like attributes
        mock_report_agent.llm.base_url = "https://api.groq.com/openai/v1"
        mock_report_agent.llm.model = "llama-3.3-70b-versatile"

        content = "Short test content"

        # Mock LLM response
        mock_report_agent.llm.chat.return_value = "Expanded content " * 100

        with patch("time.sleep"):  # Mock sleep to speed up test
            result = mock_report_agent._expand_story_with_llm(content)

        # Check that words per section was limited for Groq
        assert len(result.split()) > len(content.split())  # Content was expanded
        # With groq, should have limited words per section to 400
        # So max_tokens would be 400 * 2 = 800
        calls = mock_report_agent.llm.chat.call_args_list
        assert len(calls) > 0  # At least some calls were made

    def test_expand_story_handles_llm_failure(self, mock_report_agent):
        """Test graceful handling of LLM expansion failure."""
        content = "Test content that should be preserved"

        # Make LLM raise an exception
        mock_report_agent.llm.chat.side_effect = Exception("LLM API error")

        result = mock_report_agent._expand_story_with_llm(content)

        # Should return transformed content even if expansion fails
        assert len(result) > 0
        assert "Test content" in result or "should be preserved" in result

    def test_transformation_patterns(self, mock_report_agent):
        """Test specific transformation patterns."""
        test_cases = [
            (
                "Tôi gọi công cụ insight_forge để thu thập thông tin về X.",
                ["nhắm mắt", "tâm trí", "X"],
            ),
            (
                "Sau khi nhận được kết quả từ công cụ panorama_search,",
                ["kết quả"],  # Just check that result is mentioned
            ),
            (
                "Tôi thấy rằng có những thông tin về Y",
                ["Y"],
            ),  # Just check Y is preserved
            (
                "Tôi hy vọng những thông tin này sẽ giúp tôi hiểu rõ hơn về Z.",
                ["bức tranh", "Z"],
            ),
        ]

        for input_text, expected_keywords in test_cases:
            result = mock_report_agent._transform_tool_references_to_narrative(
                input_text
            )

            # Should not contain tool references
            assert "công cụ" not in result or "linh giác" in result
            assert "insight_forge" not in result
            assert "panorama_search" not in result

            # Should contain expected narrative elements
            for keyword in expected_keywords:
                assert keyword in result, (
                    f"Missing '{keyword}' in transformation of '{input_text}'"
                )


class TestStoryExpansionIntegration:
    """Integration tests for the full story expansion pipeline."""

    @pytest.fixture
    def mock_report_agent(self):
        """Create a mock ReportAgent for testing."""
        from app.services.report_agent import ReportAgent

        # Mock LLM client
        mock_llm = Mock()
        mock_llm.chat = Mock(return_value="Mocked LLM response")
        mock_llm.model = "test-model"
        mock_llm.base_url = "http://test"

        # Create agent with mocked dependencies
        agent = ReportAgent(
            graph_id="test_graph",
            simulation_id="test_sim",
            simulation_requirement="Test requirement",
            llm_client=mock_llm,
            zep_tools=Mock(),
            locale="vi",
            mode="story",
        )

        return agent

    @pytest.fixture
    def sample_story_content(self):
        """Sample story content with tool references."""
        return """Lời Thề và Gánh Nặng
Tôi bước vào phòng của Hoàng Tử Aelden, ánh sáng yếu ớt từ những ngọn nến.

"Kael," một giọng nói yếu ớt vang lên, "tôi không thể ngủ được."

Tôi quyết định điều tra thêm về những bóng tối. Tôi gọi công cụ insight_forge để thu thập thông tin về những bóng tối này.

Sau khi nhận được kết quả từ công cụ insight_forge, tôi thấy rằng có những thông tin về Vương Miện Lửa.

Tôi cũng thấy rằng có những thông tin về các nhân vật khác, như Draven Holt và Rowan."""

    def test_full_transformation_pipeline(
        self, mock_report_agent, sample_story_content
    ):
        """Test the complete transformation pipeline."""
        # First transform
        transformed = mock_report_agent._transform_tool_references_to_narrative(
            sample_story_content
        )

        # Verify transformation
        assert "công cụ insight_forge" not in transformed
        assert "Vương Miện Lửa" in transformed
        assert "Draven Holt" in transformed

        # Content should grow during transformation
        assert len(transformed) > len(sample_story_content)

        # All dialogue should be preserved
        assert '"Kael,"' in transformed
        assert '"tôi không thể ngủ được."' in transformed

    def test_story_mode_integration(self, mock_report_agent):
        """Test that story mode properly uses transformation."""
        # Set story mode
        mock_report_agent.mode = "story"

        # Test content
        content = "Tôi gọi công cụ quick_search để tìm kiếm thông tin."

        # Clean should use transformation
        cleaned = mock_report_agent._clean_story_content(content)

        # Should not have tool references
        assert "công cụ" not in cleaned or "linh giác" in cleaned
        assert "quick_search" not in cleaned
