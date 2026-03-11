# from database import Repository
# from aiogram.fsm.context import FSMContext


# class WorkoutService:
#     def __init__(self, repo: Repository):
#         self.repo = repo

#     async def build_from_state(self, state: FSMContext, note: str | None) -> WorkoutData:
#         data = await state.get_data()
#         return WorkoutData(
#             type=data.get('type', 'Unknown'),
#             duration=data.get('duration', 0),
#             intensity=data.get('intensity', 'Normal'),
#             note=note,
#         )

#     async def save(self, user_id: int, workout: WorkoutData, state: FSMContext) -> None:
#         self.repo.save_workout(user_id, workout.type, workout.duration, workout.intensity, workout.note)
#         await state.clear()