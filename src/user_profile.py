import json
import os
from datetime import datetime

class UserProfileManager:
    def __init__(self, filepath="profiles.json"):
        self.filepath = filepath
        self.profiles = self._load_all()

    def _load_all(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, "r") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}
        return {}

    def load_user(self, username):
        if username not in self.profiles:
            # Inicjalizacja nowego użytkownika
            self.profiles[username] = {
                "total_reps": 0, 
                "perfect_reps": 0,
                "history": []
            }
            self.save()
        # Migracja starszych profili (kompatybilność wsteczna)
        if "history" not in self.profiles[username]:
            self.profiles[username]["history"] = []
            self.save()
            
        return self.profiles[username]

    def get_user(self, username):
        return self.profiles.get(username, {"total_reps": 0, "perfect_reps": 0, "history": []})

    def update_user(self, username, total_added, perfect_added):
        if username in self.profiles:
            self.profiles[username]["total_reps"] += total_added
            self.profiles[username]["perfect_reps"] += perfect_added
            self.save()

    def save_session(self, username, session_total, session_perfect):
        """Zapisuje podsumowanie sesji treningowej po jej zakończeniu"""
        if username in self.profiles and session_total > 0:
            today = datetime.now().strftime("%Y-%m-%d %H:%M")
            self.profiles[username]["history"].append({
                "date": today,
                "reps": session_total,
                "perfect_reps": session_perfect
            })
            self.save()

    def save(self):
        with open(self.filepath, "w") as f:
            json.dump(self.profiles, f, indent=4)
