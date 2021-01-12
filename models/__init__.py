''' Register rule-based models or pre-trianed models
'''

from ai_game.models.registration import register, load
import subprocess
import sys
from packaging import version

reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
installed_packages = [r.decode().split('==')[0] for r in reqs.split()]


register(
    model_id = 'aigame-rule-v1',
    entry_point='ai_game.models.uno_rule_models:UNORuleModelV1')

