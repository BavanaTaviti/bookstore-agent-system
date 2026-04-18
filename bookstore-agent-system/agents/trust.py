def calculate_trust(reputation, avg_rating=0):
    """
    reputation → from seller
    avg_rating → from users (1–5 scale)
    """

    # Convert rating (1–5) → (0–1)
    rating_score = avg_rating / 5 if avg_rating else 0.5

    # Combine both
    trust = (reputation + rating_score) / 2

    # Normalize into levels
    if trust > 0.8:
        return round(trust, 2)
    elif trust > 0.6:
        return round(trust, 2)
    else:
        return round(trust, 2)