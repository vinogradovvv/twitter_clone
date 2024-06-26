from typing import List

from pydantic import BaseModel, ConfigDict, Field


class BaseUser(BaseModel):
    id: int
    name: str


class User(BaseUser):
    model_config = ConfigDict(from_attributes=True)

    followers: List[BaseUser]
    following: List[BaseUser]


class LikesUser(BaseModel):
    id: int = Field(serialization_alias="user_id")
    name: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    result: bool
    user: User


class ResultResponse(BaseModel):
    result: bool


class AddTweetResponse(ResultResponse):
    tweet_id: int


class AddMediaResponse(ResultResponse):
    media_id: int


class Media(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str


class Tweet(BaseModel):
    id: int
    content: str
    attachments: List[str]
    author: BaseUser
    likes: List[LikesUser]


class TweetsResponse(ResultResponse):
    model_config = ConfigDict(from_attributes=True)

    tweets: List[Tweet]


class FailResponse(BaseModel):
    result: bool
    error_type: str
    error_message: str
