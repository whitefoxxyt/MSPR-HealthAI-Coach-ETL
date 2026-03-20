from pipelines.diet_recommendations import PIPELINE as diet_recommendations
from pipelines.exercisedb import PIPELINE as exercisedb
from pipelines.gym_tracking import PIPELINE as gym_tracking
from pipelines.nutrition import PIPELINE as nutrition

PIPELINES = [exercisedb, nutrition, gym_tracking, diet_recommendations]
