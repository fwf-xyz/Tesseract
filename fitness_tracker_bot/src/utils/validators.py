from utils import AgeConstants, HeightConstants, WorkoutConstants, WeightConstants


def validate_age(text: str) -> bool:
    return text.isdigit() and AgeConstants.MIN <= int(text) <= AgeConstants.MAX

def validate_height(text: str) -> bool:
    return text.isdigit() and HeightConstants.MIN <= int(text) <= HeightConstants.MAX

def validate_weight(text: str) -> bool:
    return text.isdigit() and WeightConstants.MIN <= int(text) <= WeightConstants.MAX

def validate_duration(text: str) -> bool:
    return text.isdigit() and WorkoutConstants.MIN_DURATION <= int(text) <= WorkoutConstants.MAX_DURATION

def validate_intensity(text: str) -> bool:
    return text.isdigit() and WorkoutConstants.MIN_INTENSITY <= int(text) <= WorkoutConstants.MAX_INTENSITY 
