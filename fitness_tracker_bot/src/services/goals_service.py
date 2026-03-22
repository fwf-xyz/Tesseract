from database import Repository


async def save_goal(repo: Repository, user_id: int, data: dict) -> None:
    repo.goals.save_goal(
        user_id,
        data.get('goal', 'Unknown'),
        data.get('deadline', None),

    )
