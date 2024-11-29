from fastapi import APIRouter
from instagram.apis import *

router = APIRouter(prefix="/api/v1", tags=['instagram'])

router.add_api_route(
    '/instagram/get_instagram_auth_url', get_authorization_url
)

# router.add_api_route(
#     '/instagram/callback/', instagram_callback
# )

router.add_api_route(
    '/generator_access_token/', generate_access_token
)

# router.add_api_route(
#     '/instagram/user/info', get_user_info
# )

router.add_api_route(
    '/instagram/user/relationships/', get_instagram_followers_following
)


router.add_api_route(
    '/instagram/media/download', download_media
)

router.add_api_route(
    '/instagram/media/download/public', download_public_media
)

router.add_api_route(
    '/instagram/public/follower/count/', get_public_follower_count
)

router.add_api_route(
    '/instagram/download_media/', download_private_media #get_download_private_media download_private_media
)


