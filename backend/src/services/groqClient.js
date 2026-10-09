const OpenAI = require('openai');

const groqApiKey = process.env.GROQ_API_KEY;

const groq = new OpenAI({
  apiKey: groqApiKey || 'sk-placeholder',
  baseURL: 'https://api.groq.com/openai/v1'
});

async function generateWithGroq(systemPrompt, userMessage, context, options = {}) {
  if (!groqApiKey) {
    console.error('Groq API key not set');
    return null;
  }
  try {
    const messages = [{ role: 'system', content: systemPrompt }];
    if (context) {
      messages.push({
        role: 'system',
        content: `Here is relevant legal information from the Nepal law knowledge base to help answer:\n\n${context}`
      });
    }
    messages.push({ role: 'user', content: userMessage });
    const completion = await groq.chat.completions.create({
      model: options.model || 'openai/gpt-oss-120b',
      messages,
      temperature: options.temperature ?? 0.3,
      max_tokens: options.maxTokens || 2048,
      // gpt-oss-* are reasoning models; cap reasoning so it doesn't consume the
      // whole max_tokens budget and truncate/empty the visible answer.
      reasoning_effort: options.reasoningEffort || 'low',
      top_p: options.topP ?? 0.9
    });
    return completion.choices[0]?.message?.content || '';
  } catch (error) {
    console.error('Groq API error:', error.message);
    return null;
  }
}

module.exports = { generateWithGroq, groq, groqApiKey };
