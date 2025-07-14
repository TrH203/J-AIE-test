curl -X POST http://localhost:8000/knowledge/update \
    -H "Content-Type: application/json" \
    -d '[{"id": "doc1", "text": "AI is cool"}]'

curl http://localhost:8000/knowledge

curl -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"query": "Tell me about AI"}'

curl http://localhost:8000/audit/some_chat_id
