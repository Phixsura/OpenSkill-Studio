from app.services.app_oauth_pkce import generate_code_verifier, compute_code_challenge, verify_pkce

def test_generate_length():
    v = generate_code_verifier()
    assert 43 <= len(v) <= 128

def test_challenge_deterministic():
    v = "test_verifier_string"
    assert compute_code_challenge(v) == compute_code_challenge(v)

def test_challenge_different_for_different_verifiers():
    assert compute_code_challenge("a") != compute_code_challenge("b")

def test_verify_correct():
    v = generate_code_verifier()
    c = compute_code_challenge(v)
    assert verify_pkce(v, c) is True

def test_verify_wrong():
    v = generate_code_verifier()
    c = compute_code_challenge(v)
    assert verify_pkce("wrong_verifier", c) is False

def test_unique_verifiers():
    verifiers = {generate_code_verifier() for _ in range(50)}
    assert len(verifiers) == 50

def test_challenge_is_base64url():
    v = generate_code_verifier()
    c = compute_code_challenge(v)
    assert all(ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_" for ch in c)
