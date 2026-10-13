import os
import random
import requests
import time
import urllib.parse
from dotenv import load_dotenv
from google import genai

load_dotenv()

# Environment Variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
IG_USER_ID = os.getenv("IG_USER_ID")
FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")

# Initialize Gemini Client (Requires google-genai package)
client = genai.Client(api_key=GEMINI_API_KEY)

TOPICS = [
    {
        "theme": "Doorstep Convenience",
        "angle": "Focus on how Wish Washing saves time by cleaning cars right at the customer's doorstep in Lahore while they work or relax."
    },
    {
        "theme": "Paint & Clear Coat Protection",
        "angle": "Highlight how daily dust and mud buildup damages car paint and how regular foam washing protects the shine."
    },
    {
        "theme": "Interior Hygiene & Comfort",
        "angle": "Focus on removing dust, germs, and AC vent debris to keep the interior fresh for family commutes."
    },
    {
        "theme": "Water Conservation & Efficiency",
        "angle": "Explain the benefit of high-pressure eco-friendly foam cleaning over wasteful bucket washing."
    },
    {
        "theme": "Weekend Readiness",
        "angle": "Encourage booking a wash before Friday prayers or weekend family trips in Lahore."
    }
]

def generate_post_content():
    selected_topic = random.choice(TOPICS)
    
    text_prompt = f"""
    You are the social media manager for 'Wish Washing', a mobile doorstep car wash service operating in Lahore, Pakistan.
    
    Topic: {selected_topic['theme']}
    Angle: {selected_topic['angle']}
    
    Write an engaging social media post in Roman Urdu mixed with simple English.
    Structure:
    1. Attention-grabbing hook line
    2. 2-3 short sentences on the benefit of doorstep car wash
    3. Call to Action (CTA) with WhatsApp booking line: +92-371-7011639
    4. 5 targeted hashtags (e.g. #WishWashing #DoorstepCarWash #Lahore #CarCareLahore #CleanCar)
    
    Do NOT use markdown headers or bold headings. Keep it natural and persuasive.
    """
    
    print("Generating caption via Google Gemini Free API...")
    max_attempts = 6
    for attempt in range(1, max_attempts + 1):
        try:
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=text_prompt,
            )
            caption = response.text.strip()
            break
        except Exception as e:
            if attempt == max_attempts:
                raise
            wait_seconds = min(15 * (2 ** (attempt - 1)), 120)
            print(f"Gemini request failed (attempt {attempt}/{max_attempts}): {e}")
            print(f"Retrying in {wait_seconds}s...")
            time.sleep(wait_seconds)

    # Generate Image URL via Pollinations.ai (100% Free, Keyless)
    car_colors = ["white", "jet black", "silver", "midnight blue", "maroon", "graphite grey"]
    car_models = ["sedan", "SUV", "hatchback", "crossover", "pickup truck"]
    scenes = [
        "in a residential driveway in Lahore, Pakistan",
        "parked outside a house on a quiet Lahore street",
        "in an apartment building's parking area in Lahore",
        "on a paved driveway in a Lahore suburb"
    ]
    lighting = [
        "bright morning sunlight", "soft golden hour light", "crisp midday sun",
        "warm late afternoon light"
    ]

    raw_prompt = (
        f"Photorealistic DSLR photo of a {random.choice(car_colors)} {random.choice(car_models)} "
        f"{random.choice(scenes)}, a mobile car wash detailer in uniform actively washing it "
        f"with a high pressure foam cannon, thick rich white foam covering the body and wheels, "
        f"visible water droplets and foam texture, {random.choice(lighting)}, shallow depth of field, "
        f"shot on 50mm lens, realistic skin and fabric textures, natural shadows, 4k detail, no text, no watermark"
    )
    encoded_prompt = urllib.parse.quote(raw_prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&seed={random.randint(1, 99999)}"
    
    print("Generated Free Image URL:", image_url)
    return caption, image_url

def fetch_image_bytes(image_url, max_attempts=5, delay_seconds=5):
    for attempt in range(1, max_attempts + 1):
        try:
            r = requests.get(image_url, timeout=60)
            content_type = r.headers.get('content-type', '')
            if r.ok and content_type.startswith('image/') and len(r.content) > 1000:
                return r.content
            print(f"Image not ready yet (attempt {attempt}/{max_attempts}, status={r.status_code}, content-type={content_type})...")
        except requests.RequestException as e:
            print(f"Image fetch failed (attempt {attempt}/{max_attempts}): {e}")
        time.sleep(delay_seconds)
    raise RuntimeError(f"Could not fetch a valid image from {image_url} after {max_attempts} attempts")

def post_to_facebook(caption, image_bytes):
    url = f"https://graph.facebook.com/v26.0/{FB_PAGE_ID}/photos"
    payload = {
        'caption': caption,
        'access_token': FB_PAGE_ACCESS_TOKEN
    }
    files = {
        'source': ('image.jpg', image_bytes)
    }
    response = requests.post(url, data=payload, files=files)
    if not response.ok:
        print("Facebook post failed:", response.json())
    response.raise_for_status()
    print("Facebook Posted Successfully:", response.json())

def wait_for_container_ready(container_id, max_attempts=10, delay_seconds=3):
    status_url = f"https://graph.facebook.com/v26.0/{container_id}"
    for attempt in range(1, max_attempts + 1):
        status_r = requests.get(status_url, params={
            'fields': 'status_code',
            'access_token': FB_PAGE_ACCESS_TOKEN
        })
        status_r.raise_for_status()
        status_code = status_r.json().get('status_code')

        if status_code == 'FINISHED':
            return
        if status_code == 'ERROR':
            raise RuntimeError(f"Instagram media container failed to process: {status_r.json()}")

        print(f"Instagram container not ready yet (status={status_code}), attempt {attempt}/{max_attempts}...")
        time.sleep(delay_seconds)

    raise RuntimeError(f"Instagram media container {container_id} did not finish processing in time")

def post_to_instagram(caption, image_url):
    container_url = f"https://graph.facebook.com/v26.0/{IG_USER_ID}/media"
    payload = {
        'image_url': image_url,
        'caption': caption,
        'access_token': FB_PAGE_ACCESS_TOKEN
    }
    r = requests.post(container_url, data=payload)
    r.raise_for_status()
    container_id = r.json().get('id')

    wait_for_container_ready(container_id)

    publish_url = f"https://graph.facebook.com/v26.0/{IG_USER_ID}/media_publish"
    pub_payload = {
        'creation_id': container_id,
        'access_token': FB_PAGE_ACCESS_TOKEN
    }
    pub_r = requests.post(publish_url, data=pub_payload)
    if not pub_r.ok:
        print("Instagram publish failed:", pub_r.json())
    pub_r.raise_for_status()
    print("Instagram Posted Successfully:", pub_r.json())

if __name__ == "__main__":
    try:
        caption, image_url = generate_post_content()
        print("\n--- Generated Caption ---")
        print(caption)
        print("-------------------------\n")

        print("Waiting for Pollinations image to be ready...")
        image_bytes = fetch_image_bytes(image_url)

        post_to_facebook(caption, image_bytes)
        post_to_instagram(caption, image_url)
        print("Daily automated posting completed successfully!")
    except Exception as e:
        print(f"Error during execution: {e}")
        raise e