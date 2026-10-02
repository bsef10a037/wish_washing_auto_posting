import os
import random
import requests
from openai import OpenAI

# Environment Variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
IG_USER_ID = os.getenv("IG_USER_ID")
FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")

client = OpenAI(api_key=OPENAI_API_KEY)

# 1. Topic Matrix for Dynamic Daily Content
TOPICS = [
    {
        "theme": "Doorstep Convenience",
        "angle": "Focus on how Wish Washing saves time by cleaning cars right at the customer's doorstep in Sahiwal while they work or relax."
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
        "angle": "Encourage booking a wash before Friday prayers or weekend family trips in Sahiwal."
    }
]

def generate_post_content():
    selected_topic = random.choice(TOPICS)
    
    # Generate Caption in Roman Urdu + English
    text_prompt = f"""
    You are the social media manager for 'Wish Washing', a mobile doorstep car wash service operating in Sahiwal, Pakistan.
    
    Topic: {selected_topic['theme']}
    Angle: {selected_topic['angle']}
    
    Write an engaging social media post in Roman Urdu mixed with simple English.
    Structure:
    1. Attention-grabbing hook line
    2. 2-3 short sentences on the benefit of doorstep car wash
    3. Call to Action (CTA) with WhatsApp booking line: +92-300-0000000
    4. 5 targeted hashtags (e.g. #WishWashing #DoorstepCarWash #Sahiwal #CarCareSahiwal #CleanCar)
    
    Do NOT use markdown headers or bold headings.
    """
    
    print("Generating post text via OpenAI...")
    text_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": text_prompt}],
        max_tokens=300
    )
    caption = text_response.choices[0].message.content.strip()

    # Generate Visual via DALL-E 3
    image_prompt = (
        f"A photorealistic, crisp morning light shot of a professional mobile car wash service in Pakistan. "
        f"A shiny modern clean sedan parked in a residential driveway in Sahiwal. "
        f"A detailing technician using a high-pressure foam sprayer with rich snow foam, water droplets reflecting sunlight, "
        f"4k resolution, clean aesthetic, highly detailed."
    )
    
    print("Generating image via DALL-E 3...")
    img_response = client.images.generate(
        model="dall-e-3",
        prompt=image_prompt,
        size="1024x1024",
        quality="standard",
        n=1
    )
    image_url = img_response.data[0].url

    return caption, image_url

def post_to_facebook(caption, image_url):
    url = f"https://graph.facebook.com/v26.0/{FB_PAGE_ID}/photos"
    payload = {
        'url': image_url,
        'caption': caption,
        'access_token': FB_PAGE_ACCESS_TOKEN
    }
    response = requests.post(url, data=payload)
    response.raise_for_status()
    print("Facebook Posted Successfully:", response.json())

def post_to_instagram(caption, image_url):
    # Step 1: Create Container
    container_url = f"https://graph.facebook.com/v26.0/{IG_USER_ID}/media"
    payload = {
        'image_url': image_url,
        'caption': caption,
        'access_token': FB_PAGE_ACCESS_TOKEN
    }
    r = requests.post(container_url, data=payload)
    r.raise_for_status()
    container_id = r.json().get('id')

    # Step 2: Publish Container
    publish_url = f"https://graph.facebook.com/v26.0/{IG_USER_ID}/media_publish"
    pub_payload = {
        'creation_id': container_id,
        'access_token': FB_PAGE_ACCESS_TOKEN
    }
    pub_r = requests.post(publish_url, data=pub_payload)
    pub_r.raise_for_status()
    print("Instagram Posted Successfully:", pub_r.json())

if __name__ == "__main__":
    try:
        caption, image_url = generate_post_content()
        print("\n--- Generated Caption ---")
        print(caption)
        print("-------------------------\n")
        
        post_to_facebook(caption, image_url)
        post_to_instagram(caption, image_url)
        print("Daily automated posting completed successfully!")
    except Exception as e:
        print(f"Error during execution: {e}")