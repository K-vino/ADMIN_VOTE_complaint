require('dotenv').config();
const axios = require('axios');

async function analyzeVotePattern(votePayload) {
  const geminiPrompt = `
You are a fraud detection AI. Analyze this voting record JSON and assign a fraud probability score (0 to 1).
{
  "voter_id": "${votePayload.voter_id}",
  "location": "${votePayload.location}",
  "timestamp": "${votePayload.timestamp}",
  "device_id": "${votePayload.device_id}",
  "biometric_status": "${votePayload.biometric_status}"
}
Respond with just the score.
`;

  const response = await axios.post(
    'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=' + process.env.GEMINI_API_KEY,
    {
      contents: [{ parts: [{ text: geminiPrompt }] }]
    }
  );

  const aiReply = response.data.candidates?.[0]?.content?.parts?.[0]?.text || '0.1';
  return parseFloat(aiReply);
}

// Example use
(async () => {
  const votePayload = {
    voter_id: 'V12345',
    location: 'Station-11',
    timestamp: new Date().toISOString(),
    device_id: 'device789',
    biometric_status: 'valid'
  };

  const score = await analyzeVotePattern(votePayload);
  console.log('AI Risk Score:', score);

  if (score > 0.6) {
    console.warn('🚨 Possible Vote Fraud Detected!');
    // Trigger admin alert system here
  }
})();
