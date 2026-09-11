import time
from collections import deque, Counter

class ActionStabilizer:
    """
    Temporal smoothing, majority voting, and scene transition debounce/cooldown.
    Ensures computer vision predictions do not jitter or thrash music/effects.
    """

    def __init__(self, window_size=4, min_agreement_ratio=0.55, cooldown_seconds=1.2):
        self.window_size = window_size
        self.min_agreement_ratio = min_agreement_ratio
        self.cooldown_seconds = cooldown_seconds

        self.window = deque(maxlen=window_size)
        self.current_action = "INITIALIZING"
        self.last_action_change_time = 0.0
        self.last_evaluated_time = time.time()
        self.transition_count = 0

    def update(self, raw_action, confidence=1.0):
        now = time.time()
        self.last_evaluated_time = now
        self.window.append(raw_action)

        counts = Counter(self.window)
        dominant_action, dominant_count = counts.most_common(1)[0]
        agreement_ratio = dominant_count / len(self.window)

        scene_changed = False
        time_since_last_change = now - self.last_action_change_time
        in_cooldown = time_since_last_change < self.cooldown_seconds
        cooldown_remaining = max(0.0, self.cooldown_seconds - time_since_last_change)

        # Initial transition immediately accepts the first action (ENTRY)
        if self.current_action == "INITIALIZING":
            self.current_action = raw_action
            self.last_action_change_time = now
            self.transition_count += 1
            scene_changed = True
        elif dominant_action != self.current_action:
            # Intentional gestures and boundary events bypass cooldown for crisp response
            instant_actions = ("EXIT", "ENTRY", "RAISING_HAND", "BOTH_HANDS_UP", "DRINKING_WATER", "HANDS_ON_HEAD")
            can_transition = (not in_cooldown) or (dominant_action in instant_actions)
            if agreement_ratio >= self.min_agreement_ratio and can_transition:
                self.current_action = dominant_action
                self.last_action_change_time = now
                self.transition_count += 1
                scene_changed = True

        return self.current_action, scene_changed, {
            "raw_action": raw_action,
            "stabilized_action": self.current_action,
            "agreement_ratio": round(agreement_ratio, 2),
            "in_cooldown": in_cooldown,
            "cooldown_remaining": round(cooldown_remaining, 1),
            "window_size": len(self.window),
            "transition_count": self.transition_count
        }

    def reset(self):
        self.window.clear()
        self.current_action = "INITIALIZING"
        self.last_action_change_time = 0.0
        self.transition_count = 0
