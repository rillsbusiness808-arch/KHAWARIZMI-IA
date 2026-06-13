const fs = require('fs');
const path = require('path');

const apiKey = process.env.GROQ_API_KEY || 'VOTRE_CLE_GROQ_ICI';

let content = fs.readFileSync(path.join(__dirname, 'js', 'gemini-api.js'), 'utf8');
content = content.replace(
  /API_KEY:\s*'[^']*'/,
  `API_KEY: '${apiKey}'`
);
fs.writeFileSync(path.join(__dirname, 'js', 'gemini-api.js'), content, 'utf8');
console.log('✅ API key injected. Length:', apiKey.length);
