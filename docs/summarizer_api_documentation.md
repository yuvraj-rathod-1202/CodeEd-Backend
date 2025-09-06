# Summarizer API Endpoint Documentation

## Overview
The Summarizer API provides intelligent text summarization using Google's Gemini AI. It automatically handles large texts by chunking them when they exceed token limits and supports multiple output formats.

## Endpoint Information

**URL:** `/summarize`  
**Method:** `POST`  
**Content-Type:** `application/json`

---

## Request Schema

### Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `text` | string | ✅ Yes | - | The text content to be summarized |
| `format` | string | ❌ No | "paragraph" | Output format: "paragraph" or "bullet_points" |
| `length` | string | ❌ No | "medium" | Summary length: "small", "medium", or "large" |

### Request Body Structure

```json
{
  "text": "string",
  "format": "paragraph" | "bullet_points",
  "length": "small" | "medium" | "large"
}
```

---

## Response Schema

### Output Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `success` | boolean | Indicates if the summarization was successful |
| `summary` | string/array/null | Generated summary - string for paragraph, array for bullet_points |
| `title` | string/null | Generated title for the summary |
| `error` | string/null | Error message if summarization failed |
| `format` | string | The format used for summarization |
| `chunks_processed` | integer | Number of text chunks processed |
| `original_length` | integer | Character count of input text |
| `summary_length` | integer | Character count of output summary |
| `estimated_tokens` | integer/null | Estimated token count of input text |
| `compression_ratio` | float/null | Ratio of summary_length to original_length |

### Response Body Structure

```json
{
  "success": true,
  "summary": "string" | ["array", "of", "bullets"],
  "title": "Summary Title",
  "error": null,
  "format": "paragraph",
  "chunks_processed": 1,
  "original_length": 1500,
  "summary_length": 300,
  "estimated_tokens": 375,
  "compression_ratio": 0.2
}
```

---

## Format Examples

### 1. Paragraph Format with Different Lengths

#### Small Length Request
```json
{
  "text": "Artificial Intelligence (AI) has revolutionized numerous industries by automating complex tasks and providing intelligent solutions. Machine learning, a subset of AI, enables systems to learn from data without explicit programming. Deep learning, which uses neural networks with multiple layers, has achieved remarkable success in image recognition, natural language processing, and speech recognition. These technologies are transforming healthcare, finance, transportation, and many other sectors. However, AI also raises ethical concerns about job displacement, privacy, and algorithmic bias that society must address.",
  "format": "paragraph",
  "length": "small"
}
```

#### Response Example (Small)
```json
{
  "success": true,
  "summary": "AI has revolutionized industries through automation and intelligent solutions, with machine learning and deep learning driving advances in various applications, though ethical concerns about job displacement and bias remain.",
  "title": "AI Revolution and Ethical Considerations",
  "error": null,
  "format": "paragraph",
  "chunks_processed": 1,
  "original_length": 573,
  "summary_length": 189,
  "estimated_tokens": 143,
  "compression_ratio": 0.33
}
```

#### Medium Length Request
```json
{
  "text": "Artificial Intelligence (AI) has revolutionized numerous industries by automating complex tasks and providing intelligent solutions. Machine learning, a subset of AI, enables systems to learn from data without explicit programming. Deep learning, which uses neural networks with multiple layers, has achieved remarkable success in image recognition, natural language processing, and speech recognition. These technologies are transforming healthcare, finance, transportation, and many other sectors. However, AI also raises ethical concerns about job displacement, privacy, and algorithmic bias that society must address.",
  "format": "paragraph",
  "length": "medium"
}
```

#### Response Example (Medium)
```json
{
  "success": true,
  "summary": "Artificial Intelligence has transformed multiple industries through automation and intelligent solutions, with machine learning and deep learning leading advances in image recognition, natural language processing, and speech recognition. While AI is revolutionizing sectors like healthcare, finance, and transportation, it also presents ethical challenges including job displacement, privacy concerns, and algorithmic bias that require societal attention.",
  "title": "AI Revolution and Its Impact on Industries",
  "error": null,
  "format": "paragraph",
  "chunks_processed": 1,
  "original_length": 573,
  "summary_length": 389,
  "estimated_tokens": 143,
  "compression_ratio": 0.68
}
```

#### Large Length Request
```json
{
  "text": "Artificial Intelligence (AI) has revolutionized numerous industries by automating complex tasks and providing intelligent solutions. Machine learning, a subset of AI, enables systems to learn from data without explicit programming. Deep learning, which uses neural networks with multiple layers, has achieved remarkable success in image recognition, natural language processing, and speech recognition. These technologies are transforming healthcare, finance, transportation, and many other sectors. However, AI also raises ethical concerns about job displacement, privacy, and algorithmic bias that society must address.",
  "format": "paragraph",
  "length": "large"
}
```

#### Response Example (Large)
```json
{
  "success": true,
  "summary": "Artificial Intelligence (AI) has fundamentally revolutionized numerous industries by automating complex tasks and providing sophisticated intelligent solutions that were previously impossible. Machine learning, which represents a crucial subset of AI technology, enables computer systems to learn patterns and make decisions from data without requiring explicit programming for every scenario. Deep learning technology, which utilizes neural networks with multiple interconnected layers, has achieved remarkable and groundbreaking success in critical areas including image recognition, natural language processing, and speech recognition capabilities. These transformative technologies are actively revolutionizing essential sectors such as healthcare diagnostics, financial services, transportation systems, and many other industries. However, the rapid advancement of AI also raises significant ethical concerns about potential job displacement, privacy protection, and algorithmic bias that modern society must carefully address and regulate.",
  "title": "Comprehensive Analysis of AI Revolution and Challenges",
  "error": null,
  "format": "paragraph",
  "chunks_processed": 1,
  "original_length": 573,
  "summary_length": 756,
  "estimated_tokens": 143,
  "compression_ratio": 1.32
}
```

### 2. Bullet Points Format with Different Lengths

#### Request Example (Medium Length)
```json
{
  "text": "Climate change is one of the most pressing challenges of our time. Rising global temperatures are causing ice caps to melt, leading to sea level rise. Extreme weather events are becoming more frequent and severe. Greenhouse gas emissions from human activities are the primary cause. Renewable energy sources like solar and wind power offer solutions. Governments and organizations worldwide are implementing carbon reduction strategies. Individual actions such as reducing energy consumption and using sustainable transportation also make a difference.",
  "format": "bullet_points",
  "length": "medium"
}
```

#### Response Example
```json
{
  "success": true,
  "summary": [
    "Climate change is a critical global challenge with rising temperatures causing ice cap melting and sea level rise",
    "Extreme weather events are increasing in frequency and severity", 
    "Human greenhouse gas emissions are the primary cause of climate change",
    "Renewable energy sources like solar and wind power provide viable solutions",
    "Governments and organizations are implementing carbon reduction strategies worldwide",
    "Individual actions like reducing energy consumption and sustainable transportation contribute to solutions"
  ],
  "title": "Climate Change: Challenges and Solutions",
  "error": null,
  "format": "bullet_points",
  "chunks_processed": 1,
  "original_length": 567,
  "summary_length": 486,
  "estimated_tokens": 142,
  "compression_ratio": 0.86
}
```

### 3. Large Text with Chunking

#### Request Example
```json
{
  "text": "[Very long text exceeding 120,000 characters that would be automatically split into chunks]",
  "format": "paragraph"
}
```

#### Response Example
```json
{
  "success": true,
  "summary": "This is a comprehensive summary combining insights from multiple chunks of the original text, maintaining coherence while capturing all key points from the lengthy document.",
  "title": "Comprehensive Analysis of Large Document",
  "error": null,
  "format": "paragraph",
  "chunks_processed": 4,
  "original_length": 150000,
  "summary_length": 2500,
  "estimated_tokens": 37500,
  "compression_ratio": 0.02
}
```

---

## Error Responses

### Empty Text Error
```json
{
  "success": false,
  "summary": null,
  "title": null,
  "error": "Text cannot be empty",
  "format": "paragraph",
  "chunks_processed": 0,
  "original_length": 0,
  "summary_length": 0,
  "estimated_tokens": null,
  "compression_ratio": null
}
```

### API Error
```json
{
  "success": false,
  "summary": null,
  "title": null,
  "error": "Error during summarization: API rate limit exceeded",
  "format": "paragraph",
  "chunks_processed": 0,
  "original_length": 1200,
  "summary_length": 0,
  "estimated_tokens": null,
  "compression_ratio": null
}
```

---

## cURL Examples

### Basic Paragraph Summary (Medium Length)
```bash
curl -X POST "http://localhost:8000/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your text to summarize here...",
    "format": "paragraph",
    "length": "medium"
  }'
```

### Short Bullet Points Summary
```bash
curl -X POST "http://localhost:8000/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your text to summarize here...",
    "format": "bullet_points",
    "length": "small"
  }'
```

### Detailed Paragraph Summary
```bash
curl -X POST "http://localhost:8000/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your text to summarize here...",
    "format": "paragraph",
    "length": "large"
  }'
```

---

## HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success - Summary generated successfully |
| 400 | Bad Request - Invalid input parameters |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error - Server processing error |

---

## Rate Limits and Constraints

- **Token Limit:** Approximately 30,000 tokens per request
- **Auto-chunking:** Large texts are automatically split into manageable chunks
- **Character Limit:** No hard limit due to automatic chunking
- **Response Time:** Varies based on text length (typically 2-30 seconds)

---

## Best Practices

1. **Text Length:** For optimal performance, keep individual requests under 120,000 characters
2. **Format Selection:** 
   - Use "paragraph" for narrative summaries (returns string)
   - Use "bullet_points" for structured overviews (returns array of strings)
3. **Response Structure:** Check `success` field and handle different summary types
4. **Title Usage:** The `title` field provides a concise heading for the summary
5. **Error Handling:** Always check the `success` field before processing the summary
6. **Retry Logic:** Implement exponential backoff for API rate limit errors

---

## Interactive Documentation

When your FastAPI server is running, you can access:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

These provide interactive documentation where you can test the API directly in your browser.
