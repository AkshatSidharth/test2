require('dotenv').config();
const express = require('express');
const cors = require('cors');
const OpenAI = require('openai');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

/**
 * POST /api/extract
 *
 * Body:
 * {
 *   "context": "string — the text/data to analyze",
 *   "fields": ["field1", "field2", ...],   // optional: specific keys to extract
 *   "instructions": "string"               // optional: extra instructions for OpenAI
 * }
 *
 * Response:
 * {
 *   "success": true,
 *   "data": { ... extracted key-value pairs ... }
 * }
 */
app.post('/api/extract', async (req, res) => {
  const { context, fields, instructions } = req.body;

  if (!context || typeof context !== 'string' || context.trim() === '') {
    return res.status(400).json({
      success: false,
      error: 'Missing or empty "context" field in request body.',
    });
  }

  const fieldSection = fields && fields.length > 0
    ? `Extract the following specific fields: ${fields.map(f => `"${f}"`).join(', ')}.`
    : 'Extract all relevant key-value pairs from the context.';

  const extraInstructions = instructions
    ? `\nAdditional instructions: ${instructions}`
    : '';

  const systemPrompt = `You are a data extraction assistant. Given a piece of context, you extract structured information and return it as a JSON object.
Always respond with ONLY a valid JSON object — no markdown, no explanation, no code blocks.
${fieldSection}${extraInstructions}
If a requested field is not found in the context, set its value to null.`;

  try {
    const completion = await openai.chat.completions.create({
      model: process.env.OPENAI_MODEL || 'gpt-4o-mini',
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: context },
      ],
      temperature: 0,
      response_format: { type: 'json_object' },
    });

    const raw = completion.choices[0].message.content;
    let data;
    try {
      data = JSON.parse(raw);
    } catch {
      return res.status(500).json({
        success: false,
        error: 'OpenAI returned non-JSON output.',
        raw,
      });
    }

    return res.json({ success: true, data });
  } catch (err) {
    const status = err.status ?? 500;
    return res.status(status).json({
      success: false,
      error: err.message ?? 'OpenAI request failed.',
    });
  }
});

/**
 * POST /api/chat
 *
 * General-purpose chat completion endpoint.
 *
 * Body:
 * {
 *   "messages": [{ "role": "user"|"assistant"|"system", "content": "string" }],
 *   "context": "string"   // optional: injected as system context
 * }
 *
 * Response:
 * {
 *   "success": true,
 *   "reply": "string"
 * }
 */
app.post('/api/chat', async (req, res) => {
  const { messages, context } = req.body;

  if (!messages || !Array.isArray(messages) || messages.length === 0) {
    return res.status(400).json({
      success: false,
      error: 'Missing or empty "messages" array in request body.',
    });
  }

  const systemMessages = context
    ? [{ role: 'system', content: `Context:\n${context}` }]
    : [];

  try {
    const completion = await openai.chat.completions.create({
      model: process.env.OPENAI_MODEL || 'gpt-4o-mini',
      messages: [...systemMessages, ...messages],
      temperature: 0.7,
    });

    const reply = completion.choices[0].message.content;
    return res.json({ success: true, reply });
  } catch (err) {
    const status = err.status ?? 500;
    return res.status(status).json({
      success: false,
      error: err.message ?? 'OpenAI request failed.',
    });
  }
});

app.get('/health', (_req, res) => {
  res.json({ status: 'ok', model: process.env.OPENAI_MODEL || 'gpt-4o-mini' });
});

app.listen(PORT, () => {
  console.log(`OpenAI API server running on http://localhost:${PORT}`);
});
