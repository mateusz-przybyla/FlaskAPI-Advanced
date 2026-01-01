from api.tasks.email_tasks import send_user_registration_email

def test_send_user_registration_email_calls_mailgun_and_renders_template(mocker):
    mock_render = mocker.patch("api.tasks.email_tasks.render_template", return_value="<html>")
    mock_mailgun = mocker.patch("api.tasks.email_tasks.send_mailgun_message")

    send_user_registration_email("test@example.com", "test_user")

    # checking template rendering    
    mock_render.assert_called_once_with(
        "email/registration.html", 
        username="test_user")
    # checking mailgun call
    mock_mailgun.assert_called_once_with(
        to="test@example.com",
        subject="Successfully signed up",
        body="Hi test_user, you have successfully signed up for our service!",
        html="<html>"
    )