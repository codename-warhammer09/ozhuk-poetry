from src.ozhuk_poetry.tutor import PoetryTutor
import os

def test_tutor_progression():
    profile_file = "test_user.json"
    if os.path.exists(profile_file):
        os.remove(profile_file)
        
    tutor = PoetryTutor(profile_path=profile_file)
    
    print(f"Initial Stage: {tutor.get_current_stage().name} (ID: {tutor.profile.current_stage_id})")
    
    # Test milestone completion
    milestone = tutor.get_current_milestone()
    print(f"Current Milestone: {milestone.name}")
    
    tutor.mark_milestone_complete(milestone.id)
    print(f"Marked {milestone.id} complete.")
    
    # Complete all milestones in Stage 1
    stage1 = tutor.curriculum[1]
    for m in stage1.milestones:
        tutor.mark_milestone_complete(m.id)
        
    print(f"Stage after completing all S1 milestones: {tutor.get_current_stage().name} (ID: {tutor.profile.current_stage_id})")
    
    # Test portfolio
    tutor.add_portfolio_poem("s2_m1", "My Great Poem", "Good rhythm.")
    print(f"Total poems written: {tutor.profile.total_poems_written}")
    
    # Clean up
    os.remove(profile_file)

if __name__ == "__main__":
    test_tutor_progression()
