from database import Repository
from datetime import datetime


async def save_user_profile(repo: Repository, user_id: int, data: dict) -> None:
    repo.profiles.create_user_profile(
        user_id,
        data.get('age', 0),
        data.get('gender', 'Unknown'),
        data.get('height', 0),
        data.get('weight', 0),
        data.get('health_params'),
    )
