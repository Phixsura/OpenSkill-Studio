from app.services.app_marketplace_app_app_social_proof import build_social_proof

def test_social_proof():
    testimonials = [
        {"quote": "Amazing platform!", "author": "Alice", "role": "CTO", "company": "Acme"},
    ]
    logos = [{"name": "Google", "url": "https://google.com"}]
    r = build_social_proof(testimonials=testimonials, logos=logos)
    assert r["testimonial_count"] == 1
    assert r["testimonials"][0]["quote"] == "Amazing platform!"
    assert len(r["logos"]) == 1
    assert "developers" in r["stats"]
