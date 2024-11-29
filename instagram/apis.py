from pathlib import Path
from instaloader import Instaloader, Post, Profile, TwoFactorAuthRequiredException
from fastapi import HTTPException
import instaloader
import requests
from fastapi import HTTPException, Depends, Request
from fastapi.responses import FileResponse
from constants import INSTAGRAM_CLIENT_ID, INSTAGRAM_CLIENT_SECRET, INSTAGRAM_REDIRECT_URI, INSTAGRAM_ACCESS_TOKEN_HEADER


instaloader_obj = instaloader.Instaloader()

INSTAGRAM_CLIENT_ID = INSTAGRAM_CLIENT_ID
INSTAGRAM_CLIENT_SECRET = INSTAGRAM_CLIENT_SECRET
INSTAGRAM_REDIRECT_URI = INSTAGRAM_REDIRECT_URI
# INSTAGRAM_API_VERSION = "v21.0"  # Adjust based on the API version you're using
INSTAGRAM_ACCESS_TOKEN_HEADER = INSTAGRAM_ACCESS_TOKEN_HEADER


def get_authorization_url():
    authorization_url = f"https://api.instagram.com/oauth/authorize?client_id=3610376912555728&redirect_uri={INSTAGRAM_REDIRECT_URI}&scope=user_profile,user_media&response_type=code"
    return {
        "authorization_url": authorization_url
    }

def instagram_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return {"error": "Authorization failed"}
    return {"message": "Authorization successful", "code": code}

def generate_access_token(code: str):
    try:
        CLIENT_ID = "3610376912555728"
        CLIENT_SECRET = "30905d708e2d8f753b8d53146ceabc4a"
        REDIRECT_URI = "https://instaapis-125d3323b5e6.herokuapp.com/api/v1/instagram/callback/"
        TOKEN_URL = "https://api.instagram.com/oauth/access_token"

        payload = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI,
            "code": code
        }

        response = requests.post(TOKEN_URL, data=payload)

        print("Response Status:", response.status_code)
        print("Response Content:", response.text)

        if response.status_code == 200:
            access_token = response.json().get("access_token")
            return {"access_token": access_token}
        else:
            return {"error": response.json()}

    except Exception as e:
        print("Exception Occurred:", str(e))
        return {"error": "Server encountered an error"}


def get_user_info(access_token: str = Depends(INSTAGRAM_ACCESS_TOKEN_HEADER)):
    response = requests.get(
        f"https://graph.instagram.com/me?fields=id,username,profile_picture_url&access_token={access_token}")
    user_info = response.json()

    if not user_info:
        raise HTTPException(status_code=400, detail="Failed to obtain user instagram details")

    return user_info


def get_instagram_followers_following(user_id: int, access_token: str = Depends(INSTAGRAM_ACCESS_TOKEN_HEADER)):
    followers_response = requests.get(
        f"https://graph.instagram.com/{user_id}/followers",
        params={"access_token": access_token, "fields": "id,username,profile_picture_url"}
    )
    following_response = requests.get(
        f"https://graph.instagram.com/{user_id}/following",
        params={"access_token": access_token, "fields": "id,username,profile_picture_url"}
    )

    if followers_response.status_code != 200 or following_response.status_code != 200:
        raise HTTPException(status_code=followers_response.status_code, detail=followers_response.json())

    followers = followers_response.json().get("data", [])
    following = following_response.json().get("data", [])
    return {"followers": followers, "following": following}



async def download_media(user_id: str, media_type: str, access_token: str):
    # Validate media type
    media_type = media_type.lower()
    if media_type not in ["reel", "stories", "photos", "posts"]:
        raise HTTPException(
            status_code=400, detail="Invalid media type. Use 'reel', 'stories', 'photos', or 'posts'."
        )
    
    # Adjust media_type for filtering
    target_type = "IMAGE" if media_type in ["photos", "posts"] else "VIDEO"

    # Base Instagram Graph API endpoint
    url = f"https://graph.instagram.com/v21.0/{user_id}/media"
    
    # Request parameters
    params = {
        "access_token": access_token,
        "fields": "id,media_type,media_url,thumbnail_url,permalink,timestamp"
    }

    # Make the request
    response = requests.get(url, params=params)
    print(response)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())

    # Parse the response
    media_data = response.json()
    media_items = media_data.get("data", [])

    # Filter media by type
    filtered_media = [
        item for item in media_items
        if item.get("media_type", "").upper() == target_type
    ]
    print(filtered_media)

    return filtered_media


def download_public_media(username: str, media_type: str):
    profile = instaloader.Profile.from_username(instaloader_obj.context, username)
    print("----------------", profile)

    media_data = []

    # Convert media_type to lowercase and validate it
    media_type = media_type.lower()
    valid_media_types = ["reel", "photos", "posts"]
    if media_type not in valid_media_types:
        raise HTTPException(status_code=400, detail=f"Invalid media type. Use one of {valid_media_types}.")

    # Define mapping of media types to Instaloader typename
    media_type_map = {
        "reel": "GraphVideo",
        "posts": "GraphImage"
    }

    # Handle media retrieval based on media_type
    if media_type in media_type_map:
        post_type = media_type_map[media_type]
        media_data = [
            {
                'id': post.mediaid,
                'caption': post.caption if post.caption else '',
                'media_type': "video" if post.typename == 'GraphVideo' else "post",
                'media_url': post.video_url if post.typename == 'GraphVideo' else post.url,
                'timestamp': str(post.date)
            }
            for post in profile.get_posts() if post.typename == post_type
        ]
    elif media_type == "photos":
        media_data.append(
            {
                "profile_pic": profile.get_profile_pic_url()
            }
        )
    return {
        "media_data": media_data
    }


def get_public_follower_count(username: str):
    profile = instaloader.Profile.from_username(instaloader_obj.context, username)
    print("-----Profile Data ------", profile)
    return {
        "post_count": profile.mediacount,
        "followers_count": profile.followers,
        "following_count": profile.followees,
    }


def download_private_media(url: str, media_type: str):
    valid_media_types = ["reel", "photos", "posts"]
    media_type = media_type.lower()

    if media_type not in valid_media_types:
        raise HTTPException(status_code=400, detail=f"Invalid media type. Use one of {valid_media_types}.")

    instaloader_obj = Instaloader()

    # Login to Instagram with Two-Factor Authentication handling
    # try:
    #     instaloader_obj.login(username, password)
    # except TwoFactorAuthRequiredException as e:
    #     if not two_factor_code:
    #         raise HTTPException(status_code=401, detail="Two-factor authentication is required. Provide the code.")
    #     try:
    #         instaloader_obj.two_factor_login(two_factor_code)
    #     except Exception as e:
    #         raise HTTPException(status_code=401, detail=f"Two-factor authentication failed: {str(e)}")
    # except Exception as e:
    #     raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

    # Fetch the media URL
    try:
        if media_type in ["reel", "posts","photos"]:
            post_id = url.split('/')[4]
            post = Post.from_shortcode(instaloader_obj.context, post_id)
            post_url = post.url if post.typename == 'GraphImage' else post.video_url
        else:
            profile_username = url.split('/')[3].split("?")[0]
            profile = Profile.from_username(instaloader_obj.context, profile_username)
            post_url = profile.get_profile_pic_url()
            post_id = profile_username
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to fetch private data: {str(e)}")

    if not post_url:
        print("------------------POST URL ---------------------", post_url)
        raise HTTPException(status_code=404, detail="Media URL not found.")

    # Download the media
    try:
        response = requests.get(post_url, stream=True)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to download media.")

        file_extension = 'jpg' if media_type in ['photos', 'posts'] else 'mp4'
        file_name = f'{post_id}.{file_extension}'
        temp_folder = Path("temp_downloads")
        temp_folder.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
        download_path = temp_folder / file_name
        with open(download_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
    except Exception as e:
        print("exception as => ",e)
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    return FileResponse(
        path=download_path,
        media_type="application/octet-stream",
        filename=file_name
    )

def get_download_private_media(url: str, media_type: str, username: str, password: str, two_factor_code=None):
    try:
    # Call your function
        download_private_media(
            url=url,
            media_type=media_type,
            username=username,
            password=password
        )
    except HTTPException as e:
        if "Two-factor authentication is required" in str(e.detail):
            two_factor_code = input("Enter the 2FA code sent to your device: ")
            print(two_factor_code)
            download_private_media(
                url=url,
                media_type=media_type,
                username=username,
                password=password,
                two_factor_code=two_factor_code
            )
