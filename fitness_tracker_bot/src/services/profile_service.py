from database import Repository


async def save_user_profile(repo: Repository, user_id: int, data: dict) -> None:
    repo.profiles.create_user_profile(
        user_id,
        data.get('age', 0),
        data.get('gender', 'Unknown'),
        data.get('height', 0),
        data.get('weight', 0),
        data.get('health_params'),
    )

async def update_user_profile(repo: Repository, user_id: int, data: dict):
    repo.profiles.update_user_profile(
        user_id=user_id,
        age=data.get('age'),
        gender=data.get('gender'),
        height=data.get('height'),
        weight=data.get('weight'),
        health_params=data.get('health_params'),
    )
