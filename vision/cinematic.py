import random

CINEMATIC_MODES = {
    "ENTRY": {
        "id": "ENTRY",
        "action": "ENTRY",
        "genre": "GRAND ENTRANCE",
        "bgm_pool": ["entry.mp3", "hero.mp3"],
        "captions": [
            "A wild main character appeared!",
            "Who invited bro to the movie?",
            "Enter the protagonist. Act natural.",
            "Main character aura: 1000%.",
            "Look who finally decided to show up."
        ],
        "drama_meter": 95,
        "vfx_class": "vfx-entry",
        "meme": "dramatic.png"
    },
    "BOTH_HANDS_UP": {
        "id": "BOTH_HANDS_UP",
        "action": "BOTH HANDS UP",
        "genre": "WORLD CHAMPION VICTORY",
        "bgm_pool": ["track_victory.mp3", "hero.mp3"],
        "captions": [
            "HE'S THE CHAMPION OF THE WORLD!",
            "Rocky training montage unlocked.",
            "Victory achieved. Zero effort required.",
            "Cue the stadium fireworks!"
        ],
        "drama_meter": 98,
        "vfx_class": "vfx-entry",
        "meme": "dramatic.png"
    },
    "RAISING_HAND": {
        "id": "RAISING_HAND",
        "action": "RAISING HAND",
        "genre": "SPIDER-MAN SUSPENSE",
        "bgm_pool": ["raising_hand.mp3", "suspense.mp3"],
        "captions": [
            "Bro thinks he has web-shooters.",
            "Spider-Man stretch activated.",
            "Who gave bro superpowers?",
            "With great posture comes great responsibility."
        ],
        "drama_meter": 92,
        "vfx_class": "vfx-suspense",
        "meme": "suspicious.png"
    },
    "HANDS_ON_HEAD": {
        "id": "HANDS_ON_HEAD",
        "action": "HANDS ON HEAD",
        "genre": "EXISTENTIAL SHOCK",
        "bgm_pool": ["track_shock.mp3", "suspense.mp3"],
        "captions": [
            "MIND = COMPLETELY BLOWN.",
            "Bro just remembered he left the stove on.",
            "Plot twist of the century!",
            "Existential crisis caught in 4K."
        ],
        "drama_meter": 96,
        "vfx_class": "vfx-suspense",
        "meme": "suspicious.png"
    },
    "THINKING": {
        "id": "THINKING",
        "action": "THINKING",
        "genre": "DETECTIVE NOIR",
        "bgm_pool": ["track_thinking.mp3", "suspense.mp3"],
        "captions": [
            "The Thinker has entered the chat.",
            "Solving the world's problems right here.",
            "Brain cells operating at 110% capacity.",
            "Plotting his next cinematic mastermind move."
        ],
        "drama_meter": 90,
        "vfx_class": "vfx-suspense",
        "meme": "suspicious.png"
    },
    "DRINKING_WATER": {
        "id": "DRINKING_WATER",
        "action": "DRINKING WATER",
        "genre": "SLOW-MOTION ROMANCE",
        "bgm_pool": ["drinking_water.mp3", "romance.mp3"],
        "captions": [
            "Taking a sip like he's in a cologne commercial.",
            "Hydrated and unnecessarily dramatic.",
            "Is that water or liquid destiny?",
            "10/10 sip technique. Oscar incoming."
        ],
        "drama_meter": 89,
        "vfx_class": "vfx-romance",
        "meme": "emotional.png"
    },
    "HAND_ON_HEART": {
        "id": "HAND_ON_HEART",
        "action": "HAND ON HEART",
        "genre": "DRAMATIC ALLEGIANCE",
        "bgm_pool": ["track_heart.mp3", "romance.mp3"],
        "captions": [
            "An emotional allegiance to the cinematic arts.",
            "Feel the sheer, unbridled sincerity.",
            "Pledging loyalty to the snack cabinet.",
            "Deeply touched by his own existence."
        ],
        "drama_meter": 91,
        "vfx_class": "vfx-romance",
        "meme": "emotional.png"
    },
    "STANDING_UP": {
        "id": "STANDING_UP",
        "action": "STANDING UP",
        "genre": "HERO ASCENSION",
        "bgm_pool": ["track_stand.mp3", "action.mp3"],
        "captions": [
            "HE HAS RISEN.",
            "Standing up like a superhero in the third act.",
            "Power levels exceeding maximum.",
            "The movie budget just doubled."
        ],
        "drama_meter": 93,
        "vfx_class": "vfx-sitting",
        "meme": "dramatic.png"
    },
    "SITTING_DOWN": {
        "id": "SITTING_DOWN",
        "action": "SITTING DOWN",
        "genre": "MAIN CHARACTER ENERGY",
        "bgm_pool": ["sitting_down.mp3", "hero.mp3"],
        "captions": [
            "Bro sat down like a mafia boss.",
            "Chair secured. Zero regrets.",
            "He sat. The budget tripled.",
            "Sitting down like it's his full-time job."
        ],
        "drama_meter": 94,
        "vfx_class": "vfx-sitting",
        "meme": "dramatic.png"
    },
    "EXIT": {
        "id": "EXIT",
        "action": "EXIT",
        "genre": "TRAGIC FAREWELL",
        "bgm_pool": ["exit.mp3", "tragedy.mp3"],
        "captions": [
            "And bro just dipped.",
            "Gone. Reduced to atoms.",
            "Budget ran out. Main character left.",
            "Bro exited stage left without warning."
        ],
        "drama_meter": 99,
        "vfx_class": "vfx-exit",
        "meme": "emotional.png"
    }
}

def get_cinematic_scene(action_name):
    """Maps an action to its cinematic package with random shuffled music & comical caption."""
    mode_data = CINEMATIC_MODES.get(action_name, CINEMATIC_MODES["SITTING_DOWN"]).copy()
    mode_data["caption"] = random.choice(mode_data["captions"])
    mode_data["bgm"] = random.choice(mode_data.get("bgm_pool", ["entry.mp3"]))
    return mode_data
