from src.monitoring import update_feedback


def save_positive_feedback(interaction_id: int) -> None:
    update_feedback(interaction_id=interaction_id, feedback="positive")


def save_negative_feedback(interaction_id: int) -> None:
    update_feedback(interaction_id=interaction_id, feedback="negative")