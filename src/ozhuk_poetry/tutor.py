import json
import os
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class Milestone(BaseModel):
    id: str
    name: str
    completed: bool = False
    portfolio_count: int = 0
    portfolio_poems: List[Dict[str, Any]] = [] # List of {poem: str, critique: str}

class Stage(BaseModel):
    id: int
    name: str
    milestones: List[Milestone]

class UserProfile(BaseModel):
    username: str = "Poet"
    current_stage_id: int = 1
    completed_milestones: List[str] = []
    total_poems_written: int = 0

class PoetryTutor:
    """
    Manages the 3-stage curriculum, user progress, and Socratic loops.
    """
    def __init__(self, profile_path: str = "user_profile.json"):
        self.profile_path = profile_path
        self.profile = self._load_profile()
        self.curriculum = self._init_curriculum()

    def _init_curriculum(self) -> Dict[int, Stage]:
        """Defines the 3-stage Ozhuk path."""
        return {
            1: Stage(id=1, name="The Foundations", milestones=[
                Milestone(id="s1_m1", name="Rhythm & Rhyme"),
                Milestone(id="s1_m2", name="Sensory Imagery (Stone 1)"),
                Milestone(id="s1_m3", name="Basic Poetic Flow"),
            ]),
            2: Stage(id=2, name="The Architect's Tools", milestones=[
                Milestone(id="s2_m1", name="Formal Structures (Sonnets/Haikus)"),
                Milestone(id="s2_m2", name="Literary Devices (Stone 2)"),
                Milestone(id="s2_m3", name="Structural Cohesion"),
            ]),
            3: Stage(id=3, name="The Master's Breath", milestones=[
                Milestone(id="s3_m1", name="Complex Scansion (Stone 3)"),
                Milestone(id="s3_m2", name="Synthesis & Theme"),
                Milestone(id="s3_m3", name="Original Composition Mastery"),
            ]),
        }

    def _load_profile(self) -> UserProfile:
        if os.path.exists(self.profile_path):
            try:
                with open(self.profile_path, "r") as f:
                    data = json.load(f)
                    return UserProfile(**data)
            except Exception:
                return UserProfile()
        return UserProfile()

    def save_profile(self):
        with open(self.profile_path, "w") as f:
            f.write(self.profile.model_dump_json(indent=4))

    def get_current_stage(self) -> Stage:
        return self.curriculum[self.profile.current_stage_id]

    def get_current_milestone(self) -> Optional[Milestone]:
        stage = self.get_current_stage()
        for m in stage.milestones:
            if m.id not in self.profile.completed_milestones:
                return m
        return None

    def mark_milestone_complete(self, milestone_id: str):
        if milestone_id not in self.profile.completed_milestones:
            self.profile.completed_milestones.append(milestone_id)

            # Check if stage is complete to advance
            stage = self.get_current_stage()
            if all(m.id in self.profile.completed_milestones for m in stage.milestones):
                if self.profile.current_stage_id < 3:
                    self.profile.current_stage_id += 1

            self.save_profile()

    def add_portfolio_poem(self, milestone_id: str, poem: str, critique: str):
        """Adds a poem to the specific milestone portfolio."""
        stage = self.get_current_stage()
        for m in stage.milestones:
            if m.id == milestone_id:
                m.portfolio_poems.append({"poem": poem, "critique": critique})
                m.portfolio_count += 1
                break
        self.profile.total_poems_written += 1
        self.save_profile()
