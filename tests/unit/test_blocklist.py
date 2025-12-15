from api.services import blocklist

def test_add_and_check_blocklist():
    jti = "test_jti"

    blocklist.add_jti_to_blocklist(jti, exp=60)

    assert blocklist.is_jti_blocked(jti) is True

def test_adding_same_jti_twice_is_safe():
    jti = "abc123"

    blocklist.add_jti_to_blocklist(jti, exp=60)
    blocklist.add_jti_to_blocklist(jti, exp=60)

    assert blocklist.is_jti_blocked(jti) is True

def test_is_jti_blocked_returns_false():
    assert blocklist.is_jti_blocked("non_existing_jti") is False