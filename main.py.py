import os
import requests
import time
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- LOAD SECRETS ---
ASTRIA_API_KEY = os.environ.get("ASTRIA_API_KEY")

# --- ENDPOINT 1: TRAIN A NEW MODEL (The $97 Event) ---
@app.route('/tune_model', methods=['POST'])
def train_model():
    data = request.json
    # Bubble will send a list of image URLs
    image_urls = data.get('image_urls', [])

    if not image_urls:
        return jsonify({"error": "No images provided"}), 400

    print(f"Received training request with {len(image_urls)} images.")

    url = "https://api.astria.ai/tunes"
    headers = {"Authorization": f"Bearer {ASTRIA_API_KEY}"}

    # The V2 Luxury Recipe (Flux)
    payload = {
        "tune[title]": "Customer Luxury Model (Flux)",
        "tune[name]": "woman",
        "tune[branch]": "flux1",
        "tune[token]": "ohwx",
        "tune[model_type]": "lora",
        "tune[image_urls]": image_urls # Astria downloads these for us
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code in [200, 201]:
            return jsonify(response.json())
        else:
            return jsonify({"error": response.text}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- ENDPOINT 2: GENERATE THE PACK (The Delivery) ---
@app.route('/generate', methods=['POST'])
def generate_photos():
    data = request.json
    model_id = data.get('model_id')

    # Customization from Bubble
    hair_style = data.get('hair_style', "styled hair") 
    outfit_note = data.get('outfit_note', "") 

    if not model_id:
        return jsonify({"error": "Missing Model ID"}), 400

    print(f"Generating Pack for Model {model_id} | Hair: {hair_style}")

    url = f"https://api.astria.ai/tunes/{model_id}/prompts"
    headers = {
        "Authorization": f"Bearer {ASTRIA_API_KEY}",
        "Content-Type": "application/json"
    }

    # --- THE LUXURY THEMES ---
    # Helper to build the prompt string
    def make_prompt(desc):
        hair_text = f"with {hair_style}" if hair_style else ""
        outfit_text = f"wearing {outfit_note}" if outfit_note else ""
        return f"ohwx woman {hair_text}, {desc} {outfit_text}"

    themes = [
        {
            "name": "THE EXECUTIVE",
            "desc": "medium shot, sharp tailored blazer. Standing in a modern glass office, arms crossed, confident expression. Soft professional studio lighting, grey background. 8k, authentic skin texture."
        },
        {
            "name": "THE VOGUE COVER",
            "desc": "close up portrait, high-fashion editorial style. Wearing a silk blouse. Golden hour sunlight hitting face, cinematic bokeh, lens flare, luxury penthouse background. 85mm lens, f/1.8. Dreamy, expensive."
        },
        {
            "name": "THE LIFESTYLE",
            "desc": "sitting in a high-end coffee shop, laughing candidly, looking away from camera. Wearing a cashmere sweater. Natural window light, blurry city street visible. Lifestyle photography, bright and airy."
        },
        {
            "name": "THE GALA",
            "desc": "red carpet event photography, direct flash style. Diamond earrings. Dark luxury background with bokeh lights. Paparazzi aesthetic, glamorous, high contrast."
        }
    ]

    sent_count = 0
    for theme in themes:
        final_prompt = make_prompt(theme['desc'])

        payload = {
            "prompt": {
                "text": final_prompt,
                "num_images": 2,
                "super_resolution": True,
                "face_correct": False,
                "aspect_ratio": "3:4",
                "cfg_scale": 3.0
            }
        }
        try:
            requests.post(url, headers=headers, json=payload)
            sent_count += 1
            time.sleep(0.5)
        except:
            pass

    return jsonify({"status": "success", "message": f"Started {sent_count} jobs"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)