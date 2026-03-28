# Story Mode Transformation Guide

## Overview
The story mode transformation system converts technical tool references into smooth narrative text while preserving 100% of the content.

## Key Features

### 1. Tool Reference Transformation
Transforms phrases like:
- `"Tôi quyết định gọi công cụ linh giác"` → `"Tôi nhắm mắt, tập trung tâm trí"`
- `"Kết quả từ công cụ cho thấy"` → `"Trong tầm nhìn của tôi, sự thật dần hiện rõ"`
- `"Tôi đọc thấy:"` → `"Trí nhớ của tôi gợi lên:"`

### 2. Groq API Optimizations
To fit within the 12,000 TPM limit (not 14,400 as documented):
- MAX_TOOL_RESULT_CHARS: 2000 (reduced from 4000)
- MAX_PREV_TOTAL: 1500 for Groq (reduced from 3000)
- Minimal system prompt for Groq (~150 tokens vs ~2500)
- max_tokens: 2048 for story generation
- min_tool_calls: 2 (reduced from 3)
- max_iterations: 4 (reduced from 5)

### 3. Story Expansion
After transformation, content is expanded to ~3000 words:
- Splits into 6 sections
- Each section expanded to 400-500 words
- 2-second delays between API calls for Groq
- Preserves narrative flow and consistency

## Frontend Integration

### Report Regeneration
When regenerating a failed report:
1. Backend creates new report with new ID
2. Frontend receives new report_id in response
3. Navigation automatically updates to new report URL
4. New report data loads fresh

## Testing
Run tests with:
```bash
cd backend
python -m pytest tests/test_story_transformation.py -v
```

All 10 tests should pass, covering:
- Tool reference transformation
- Content preservation (100%)
- Multi-language support
- Groq API limit handling
- Story expansion
- Error handling