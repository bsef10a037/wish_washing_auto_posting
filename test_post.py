import requests

FB_PAGE_ID = "1223826014146335"
IG_USER_ID = "17841439907503178"
FB_PAGE_ACCESS_TOKEN = "EAAhAraLZB3H0BSugNXs5wHPu5yulkfxURIYwpK0FzGib21u4ZCwbUXWLsor5JboWvgWB7nHM6VP6nAXadVevAtmpXPj4nnrVtuREEZCc4tCNTWiDUGLUQmnZBZCfiGbxIJfNyQSB4MQ0k9KqF6qGz5Kkd7qQ7To5tg8gZB8zSsvcbXWTlw9ENGZATSJ3ZAOCr6uAoX6Uvv78"

TEST_IMAGE_URL = "https://images.unsplash.com/photo-1520340356584-f9917d1eea6f?w=1080"
TEST_CAPTION = "Wish Washing - Doorstep Car Wash Test Post 🚗✨ #WishWashing #Lahore"

def test_facebook():
    url = f"https://graph.facebook.com/v26.0/{FB_PAGE_ID}/photos"
    payload = {
        'url': TEST_IMAGE_URL,
        'caption': TEST_CAPTION,
        'access_token': FB_PAGE_ACCESS_TOKEN
    }
    r = requests.post(url, data=payload)
    print("Facebook Result:", r.json())

def test_instagram():
    # Step A: Create container
    container_url = f"https://graph.facebook.com/v26.0/{IG_USER_ID}/media"
    payload = {
        'image_url': TEST_IMAGE_URL,
        'caption': TEST_CAPTION,
        'access_token': FB_PAGE_ACCESS_TOKEN
    }
    r = requests.post(container_url, data=payload)
    res = r.json()
    container_id = res.get('id')
    
    if not container_id:
        print("IG Container Failed:", res)
        return

    # Step B: Publish container
    publish_url = f"https://graph.facebook.com/v26.0/{IG_USER_ID}/media_publish"
    pub_payload = {
        'creation_id': container_id,
        'access_token': FB_PAGE_ACCESS_TOKEN
    }
    pub_r = requests.post(publish_url, data=pub_payload)
    print("Instagram Result:", pub_r.json())

if __name__ == "__main__":
    test_facebook()
    test_instagram()