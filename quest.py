# quest.py

class Quest:
    """Represents a single quest with objectives."""
    def __init__(self, name, description, objectives):
        self.name = name
        self.description = description
        self.objectives = {obj: False for obj in objectives} # Objective: is_complete
        self.is_complete = False

    def complete_objective(self, objective_name):
        """Marks an objective as complete."""
        if objective_name in self.objectives:
            self.objectives[objective_name] = True
            self.check_completion()

    def check_completion(self):
        """Checks if all objectives are complete."""
        if all(self.objectives.values()):
            self.is_complete = True

class QuestLog:
    """Manages all active and completed quests for the player."""
    def __init__(self):
        self.active_quests = {}
        self.completed_quests = {}

    def add_quest(self, quest):
        """Adds a new quest to the active list."""
        if quest.name not in self.active_quests and quest.name not in self.completed_quests:
            self.active_quests[quest.name] = quest
            return f"New Quest: {quest.name}"
        return None

    def complete_quest(self, quest_name):
        """Moves a quest from active to completed."""
        if quest_name in self.active_quests:
            quest = self.active_quests.pop(quest_name)
            quest.is_complete = True
            self.completed_quests[quest_name] = quest
            return f"Quest Complete: {quest_name}"
        return None
