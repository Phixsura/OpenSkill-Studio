"""Rating input — star rating input configuration."""


def build_rating_input(*, current_value: int = 0, max_stars: int = 5,
                         allow_half: bool = False, labels: dict | None = None) -> dict:
    default_labels = {1: "Poor", 2: "Fair", 3: "Good", 4: "Very Good", 5: "Excellent"}
    star_labels = labels or default_labels
    stars = []
    for i in range(1, max_stars + 1):
        stars.append({
            "value": i,
            "filled": i <= current_value,
            "label": star_labels.get(i, ""),
        })
    return {
        "stars": stars,
        "current_value": current_value,
        "max_stars": max_stars,
        "allow_half": allow_half,
        "display": "★" * current_value + "☆" * (max_stars - current_value),
        "label": star_labels.get(current_value, ""),
    }
