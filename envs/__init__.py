''' Register new environments
'''
from ai_game.envs.env import Env
from ai_game.envs.vec_env import VecEnv
from ai_game.envs.registration import register, make



register(
    env_id='uno',
    entry_point='ai_game.envs.uno:UnoEnv',
)

