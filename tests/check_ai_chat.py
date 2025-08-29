import sys
from pathlib import Path
import os
import json

# Add the src directory to the path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(Path(__file__).parent.parent))

import tempfile
from src.core.ai_chat import AIChat

# Check if settings file exists in results directory
settings_path = Path(__file__).parent.parent / "результаты" / "ai_chat_settings.json"
if settings_path.exists():
    print("Settings file exists in results directory")
    with open(settings_path, 'r') as f:
        settings = json.load(f)
        print("Current settings:", settings)

with tempfile.TemporaryDirectory() as d:
    f = os.path.join(d, 'test.json')
    settings_file = os.path.join(d, 'ai_chat_settings.json')
    
    # Create empty settings file to prevent loading from results directory
    with open(settings_file, 'w') as sf:
        json.dump({
            'enable_openrouter': False, 
            'enable_local_ai': False, 
            'enable_external_ai': False
        }, sf)
    
    ai = AIChat({
        'chat_history_file': f, 
        'enable_openrouter': False, 
        'enable_local_ai': False, 
        'enable_external_ai': False
    })
    print('OpenRouter:', ai.enable_openrouter)
    print('Local AI:', ai.enable_local_ai)
    print('External AI:', ai.enable_external_ai)
    r = ai.get_response('Привет')
    print('Response:', r)