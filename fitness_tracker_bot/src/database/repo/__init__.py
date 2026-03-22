from .workout_repository import WorkoutRepository
from .user_repository import UserRepository
from .profile_repository import ProfileRepository
from .goal_repository import GoalRepository


class Repository:
    def __init__(self, conn):
        self.conn = conn
        self.users = UserRepository(conn)
        self.workouts = WorkoutRepository(conn)
        self.profiles = ProfileRepository(conn)
        self.goals = GoalRepository(conn)