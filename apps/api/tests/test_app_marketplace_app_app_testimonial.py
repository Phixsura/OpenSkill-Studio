from app.services.app_marketplace_app_app_testimonial import build_testimonials

def test_testimonials():
    data = [
        {"quote": "Amazing platform!", "author": "Alice Smith", "role": "CTO", "company": "Acme", "rating": 5},
        {"quote": "Great SDK!", "author": "Bob Jones", "role": "Dev", "rating": 4},
    ]
    r = build_testimonials(testimonials=data)
    assert r["total"] == 2
    assert r["avg_rating"] == 4.5
    assert r["testimonials"][0]["avatar_initials"] == "AS"

def test_xss():
    r = build_testimonials(testimonials=[{"quote": "<script>xss</script>", "author": "X"}])
    assert "<script>" not in r["testimonials"][0]["quote"]
