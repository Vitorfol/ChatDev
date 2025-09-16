'''
Configuration and presets for difficulties.
DIFFICULTY_PRESETS maps difficulty name -> suggested bomb fraction and first_click_safe flag.
'''
DIFFICULTY_PRESETS = {
    "Easy": {
        "suggest_fraction": 0.10,   # suggested fraction of bombs if user hasn't specified
        "first_click_safe": True,
    },
    "Medium": {
        "suggest_fraction": 0.15,
        "first_click_safe": True,
    },
    "Hard": {
        "suggest_fraction": 0.25,
        "first_click_safe": False,
    }
}