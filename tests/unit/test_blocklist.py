from api.services import blocklist

def test_add_and_check_blocklist(mocker):
    mock_redis = mocker.patch("api.services.blocklist.redis_client")
    jti = "test_jti"
    exp = 60

    blocklist.add_jti_to_blocklist(jti, exp)

    mock_redis.setex.assert_called_once_with(f"blocklist:{jti}", exp, "true")

def test_is_jti_blocked_true(mocker):
    mock_redis = mocker.patch("api.services.blocklist.redis_client")
    mock_redis.exists.return_value = 1
    assert blocklist.is_jti_blocked("abc123") is True

def test_is_jti_blocked_false(mocker):
    mock_redis = mocker.patch("api.services.blocklist.redis_client")
    mock_redis.exists.return_value = 0
    assert blocklist.is_jti_blocked("abc123") is False