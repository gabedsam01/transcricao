#!/bin/bash
set -e

mkdir -p output-tests
API_URL="http://localhost:8000"

echo "Checking API Health..."
curl -s $API_URL/health | jq .

echo ""
echo "Testing SHORT VIDEO..."
yt-dlp -f "bestaudio" -x --audio-format mp3 -o "output-tests/short.mp3" "https://youtube.com/shorts/GPLg0FZQSmk"
curl -s -X POST -F "file=@output-tests/short.mp3" $API_URL/transcribe > output-tests/short_result.json
echo "Short video transcribed! Results at output-tests/short_result.json"
cat output-tests/short_result.json | jq '{text: .text[0:100], duration: .duration}'

echo ""
echo "Testing LONG VIDEO..."
yt-dlp -f "bestaudio" -x --audio-format mp3 -o "output-tests/long.mp3" "https://youtu.be/lT2Ze4LT6Ls"
curl -s -X POST -F "file=@output-tests/long.mp3" $API_URL/transcribe > output-tests/long_result.json
echo "Long video transcribed! Results at output-tests/long_result.json"
cat output-tests/long_result.json | jq '{text: .text[0:100], duration: .duration}'
