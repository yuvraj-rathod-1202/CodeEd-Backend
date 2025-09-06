# Summarizer API Quick Reference

## Endpoint
```
POST /summarize
```

## Request Formats

### 📄 Paragraph Format
```json
{
  "text": "Your text content here...",
  "format": "paragraph",
  "length": "medium"
}
```
**Output:** Coherent narrative summary as string + title.
**Lengths:** small (1-3 sentences), medium (2-5 sentences), large (4-8 sentences)

### 🔸 Bullet Points Format
```json
{
  "text": "Your text content here...", 
  "format": "bullet_points",
  "length": "small"
}
```
**Output:** Key points as array of strings + title.
**Lengths:** small (2-4 bullets), medium (4-7 bullets), large (6-12 bullets)

## Response Structure
```json
{
  "success": boolean,
  "summary": "string" | ["array", "of", "bullets"],
  "title": "Summary Title",
  "error": null | "error message",
  "format": "paragraph" | "bullet_points",
  "chunks_processed": number,
  "original_length": number,
  "summary_length": number,
  "estimated_tokens": number | null,
  "compression_ratio": float | null
}
```

## Quick Test Commands

### Paragraph Summary (Medium)
```bash
curl -X POST "http://localhost:8000/summarize" \
  -H "Content-Type: application/json" \
  -d '{"text": "AI is transforming industries...", "format": "paragraph", "length": "medium"}'
```

### Short Bullet Points Summary  
```bash
curl -X POST "http://localhost:8000/summarize" \
  -H "Content-Type: application/json" \
  -d '{"text": "AI is transforming industries...", "format": "bullet_points", "length": "small"}'
```

## Features
- ✅ Automatic text chunking for large inputs
- ✅ Two output formats: paragraph (string) / bullet points (array)
- ✅ Three summary lengths: small, medium, large
- ✅ Generated titles for all summaries
- ✅ Comprehensive metadata in response
- ✅ Error handling with detailed messages
- ✅ Token estimation and compression ratio

## Access Interactive Docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
