from api.models import UserModel

def test_user_model_fiels():
    user = UserModel(username="test", email="a@b.com", password="secret")
    assert user.username == "test"
    assert user.email == "a@b.com"
    assert user.password == "secret"