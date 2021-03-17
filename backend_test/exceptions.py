from pprint import pformat


class SlackMessageException(Exception):

    def __init__(self, response_object, message=None):
        self.status_code = response_object.status_code
        self.requested_params = {
            'slack_web_hook': response_object.request.url,
            'headers': response_object.request.headers,
            'payload': response_object.request.body,
        }
        self.message = message or self.default_exception_message
        super().__init__(self.message)

    @property
    def default_exception_message(self):
        return pformat(
            f"Slack message was not sent successfully [{self.status_code}]"
            f" received, requested params: {self.requested_params}"
        )
