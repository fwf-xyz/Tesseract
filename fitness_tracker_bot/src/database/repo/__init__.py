from .workout_repository import WorkoutRepository
from .user_repository import UserRepository


class Repository:
    def __init__(self, conn):
        self.users = UserRepository(conn)
        self.workouts = WorkoutRepository(conn)