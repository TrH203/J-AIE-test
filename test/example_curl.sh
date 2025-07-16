# Test api Access into 0.0.0.0:8000/docs
# Create knowledge
curl -X POST http://0.0.0.0:8000/knowledge/update \
    -H "Content-Type: application/json" \
    -d '[{"text": "HTH is Hoang Trong Hien, he is an AI Engineer in Viet Name"}]'

#Create
curl -X POST http://0.0.0.0:8000/knowledge/update \
    -H "Content-Type: application/json" \
    -d '[{"text": "HTH is Hieuthuhai, he is a rapper and singer in Viet Nam"}]'

#Create
curl -X POST http://0.0.0.0:8000/knowledge/update \
    -H "Content-Type: application/json" \
    -d '[{"text": "G-Dragon is a rapper and singer in Korea"}]'

#Create
curl -X POST http://0.0.0.0:8000/knowledge/update \
    -H "Content-Type: application/json" \
    -d '[{"id": "doc1", "text": "AI is Apple Inteligent"}]'

# Update
curl -X POST http://0.0.0.0:8000/knowledge/update \
    -H "Content-Type: application/json" \
    -d '[{"id": "doc1", "text": "AI is Artificial Inteligient"}]'

#Get all knowledge
curl -X GET http://0.0.0.0:8000/knowledge

#Get knowledge by id
curl -X GET http://0.0.0.0:8000/knowledge/doc1

#Delete knowledge by id
curl -X DELETE http://0.0.0.0:8000/knowledge/doc1

# Chat without reasoning
curl -X POST http://0.0.0.0:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"query": "What is the name of singer and rapper in Viet Nam"}'

# Chat without reasoning
curl -X POST http://0.0.0.0:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"query": "What is the name of singer and rapper in Viet Nam", "enable_reasoning": true}'

#Get all action logs
curl -X GET http://0.0.0.0:8000/logs/

#Get all audit logs
curl -X GET http://0.0.0.0:8000/audit/