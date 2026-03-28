# Story Mode Optimization for Groq API

## Groq API Limits (Free Tier)
- **Context**: 128,000 tokens (sufficient for 3000 words)
- **Rate Limits**: 
  - 30 requests/minute
  - 14,400 tokens/minute (TPM)
  - 500,000 tokens/day

## Story Expansion Optimization

### Problem
Original design: 3000 words = 6 sections × 500 words ≈ 18,000 tokens
This exceeds the 14,400 TPM limit!

### Solution Implemented
1. **Reduced words per section**: 400 words (from 500)
2. **Total output**: 2400 words (6 × 400)
3. **Token usage**: ~10,000 tokens per story (within limits)
4. **Added delays**: 2 seconds between sections

### Load Balancer Configuration
With 8 Groq API keys in rotation:
- Effective TPM: 14,400 × 8 = 115,200 tokens/minute
- Can handle multiple concurrent story generations

## Configuration Example

### .env file:
```env
# Groq Load Balancer (8 APIs)
LLM_PROVIDER_1=groq
LLM_API_KEY_1=gsk_key1...
LLM_BASE_URL_1=https://api.groq.com/openai/v1
LLM_MODEL_1=llama-3.3-70b-versatile

LLM_PROVIDER_2=groq  
LLM_API_KEY_2=gsk_key2...
LLM_BASE_URL_2=https://api.groq.com/openai/v1
LLM_MODEL_2=llama-3.3-70b-versatile

# ... repeat for 3-8
```

### Code Detection
The system automatically detects Groq API and applies optimizations:

```python
if 'groq' in str(getattr(self.llm, 'base_url', '')).lower():
    words_per_section = min(words_per_section, 400)
    logger.info(f"Using Groq API, limiting to {words_per_section} words per section")
```

## Story Quality
- **Original length**: 3000 words → **Optimized**: 2400 words
- Still provides rich, detailed narrative
- Transformation preserves 100% of content
- Each chapter is substantial (~400 words)

## Alternative Solutions
If you need full 3000-word stories:
1. Use paid Groq tier (higher TPM)
2. Mix providers (Groq for transform, OpenAI for expansion)
3. Increase delay between sections (slower but works)
4. Cache and reuse common expansions