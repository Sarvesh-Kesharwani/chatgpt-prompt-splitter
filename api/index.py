from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
import random
import redis
import string

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Set up Redis client
upstash_redis_url = os.environ.get('UPSTASH_REDIS_URL')
redis_client = redis.from_url(upstash_redis_url)

@app.route("/", methods=["GET", "POST"])
def index():
    prompt = ""
    split_length = ""
    file_data = []
    
    redis_client.incr("visit_counter")
    visit_count = int(redis_client.get("visit_counter"))

    if request.method == "POST":
        prompt = request.form["prompt"]
        split_length = int(request.form["split_length"])

        file_data = split_prompt(prompt, split_length)
        
    hash_value = generate_random_hash(8)
    
    return render_template("index.html", prompt=prompt, split_length=split_length, file_data=file_data, hash=hash_value, visit_count=visit_count)
            
def split_prompt(text, split_length):
    if split_length <= 0:
        raise ValueError("Max length must be greater than 0.")

    num_parts = -(-len(text) // split_length)
    file_data = []

    for i in range(num_parts):
        start = i * split_length
        end = min((i + 1) * split_length, len(text))
        content = text[start:end]
        file_data.append({
            'name': f'split_{str(i + 1).zfill(3)}_of_{str(num_parts).zfill(3)}.txt',
            'content': content
        })

    return file_data

def generate_random_hash(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 3000)))
