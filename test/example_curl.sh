# Test api Access into 0.0.0.0:8000/docs

# Chat without reasoning
curl -X POST http://0.0.0.0:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"query": "Tell me about AI"}'

# Chat without reasoning
curl -X POST http://0.0.0.0:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"query": "Tell me about AI", "enable_reasoning": true}'
