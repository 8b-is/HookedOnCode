#!/bin/bash
curl -s -X POST http://172.30.50.42:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nousresearch/hermes-4-70b",
    "messages": [{"role": "user", "content": "Just say OK"}],
    "max_tokens": 5,
    "temperature": 0
  }'