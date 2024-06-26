from fastapi import status
from starlette.exceptions import HTTPException


class TwitterException(HTTPException):
    """Custom exception"""

    # status_code = None

    def __init__(self):
        self.result = False
        self.status_code = None
        self.error_type = None
        self.error_message = None


class TwitterNoFileException(TwitterException):
    def __init__(self):
        super().__init__()
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.error_type = "Missed file."
        self.error_message = "File is required."


class TwitterWrongApiKeyException(TwitterException):
    def __init__(self):
        super().__init__()
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.error_type = "Unauthorized user."
        self.error_message = "Unauthorized user."


class TwitterNoUserException(TwitterException):
    def __init__(self):
        super().__init__()
        self.status_code = status.HTTP_404_NOT_FOUND
        self.error_type = "User not found."
        self.error_message = "There is no such user in the database."


class TwitterNoMediaException(TwitterException):
    def __init__(self):
        super().__init__()
        self.status_code = status.HTTP_404_NOT_FOUND
        self.error_type = "Media not found."
        self.error_message = "There is no such media in the database."


class TwitterNoTweetException(TwitterException):
    def __init__(self):
        super().__init__()
        self.status_code = status.HTTP_404_NOT_FOUND
        self.error_type = "Tweet not found."
        self.error_message = "There is no such tweet in the database."


class TwitterOwnerException(TwitterException):
    def __init__(self):
        super().__init__()
        self.status_code = status.HTTP_405_METHOD_NOT_ALLOWED
        self.error_type = "Tweet owner error."
        self.error_message = "The tweet you are trying to delete is not yours."


class TwitterAlreadyLikedException(TwitterException):
    def __init__(self):
        super().__init__()
        self.status_code = status.HTTP_405_METHOD_NOT_ALLOWED
        self.error_type = "Tweet like error."
        self.error_message = "You are already liked this tweet."


class TwitterDidNotLikeException(TwitterException):
    def __init__(self):
        super().__init__()
        self.status_code = status.HTTP_405_METHOD_NOT_ALLOWED
        self.error_type = "Tweet like error."
        self.error_message = "You did not liked this tweet yet."


class TwitterAlreadyFollowingException(TwitterException):
    def __init__(self):
        super().__init__()
        self.status_code = status.HTTP_405_METHOD_NOT_ALLOWED
        self.error_type = "Following error."
        self.error_message = "You are already following this user."


class TwitterDoNotFollowingException(TwitterException):
    def __init__(self):
        super().__init__()
        self.status_code = status.HTTP_405_METHOD_NOT_ALLOWED
        self.error_type = "Following error."
        self.error_message = "You are not following this user."
