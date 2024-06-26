from typing import Any, Dict

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import relationship, selectinload

from .database import Base


class Likes(Base):
    """
    Likes association table.
    """

    __tablename__ = "likes"

    users = Column(Integer, ForeignKey("users.id"), primary_key=True)
    tweets = Column(Integer, ForeignKey("tweets.id"), primary_key=True)


class Follows(Base):
    """
    Follows association table.
    """

    __tablename__ = "follows"

    followers_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    following_id = Column(Integer, ForeignKey("users.id"), primary_key=True)


class Users(Base, AsyncAttrs):
    """
    Users table.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    api_key = Column(String, nullable=False, unique=True)
    followers = relationship(
        "Users",
        secondary=Follows.__table__,
        primaryjoin=id == Follows.__table__.c.following_id,
        secondaryjoin=id == Follows.__table__.c.followers_id,
        back_populates="following",
        lazy="selectin",
    )
    following = relationship(
        "Users",
        secondary=Follows.__table__,
        primaryjoin=id == Follows.__table__.c.followers_id,
        secondaryjoin=id == Follows.__table__.c.following_id,
        back_populates="followers",
        lazy="selectin",
    )
    tweets = relationship("Tweets", back_populates="author", lazy="selectin")

    @classmethod
    async def get_id_by_api_key(cls, session: AsyncSession, api_key: str) -> Any | None:
        """
        Returns id of user with given api key.
        :param session: Database session.
        :type session: AsyncSession
        :param api_key: Api authorisation key.
        :type api_key: str
        :return: User id
        :rtype: Result
        """
        res = await session.execute(select(cls.id).filter(cls.api_key == api_key))
        return res.scalar_one_or_none()

    @classmethod
    async def get_user_by_api_key(
        cls, session: AsyncSession, api_key: str
    ) -> Any | None:
        """
        Returns user with given api key.
        :param session: Database session.
        :type session: AsyncSession
        :param api_key: Api authorisation key.
        :type api_key: str
        :return: User data
        :rtype: Result
        """
        res = await session.execute(
            select(cls)
            .filter(cls.api_key == api_key)
            .options(selectinload(cls.followers), selectinload(cls.following))
        )
        return res.unique().scalar_one_or_none()

    @classmethod
    async def get_user_by_id(cls, session: AsyncSession, id: int) -> Any | None:
        """
        Returns user with given id.
        :param session: Database session.
        :type session: AsyncSession
        :param id: User id.
        :type id: int
        :return: User data
        :rtype: Result
        """
        res = await session.execute(
            select(cls)
            .filter(cls.id == id)
            .options(selectinload(cls.followers), selectinload(cls.following))
        )
        return res.unique().scalar_one_or_none()

    def to_json(self) -> Dict[str, Any]:
        """
        Converts user data to json dict.
        :return: Json dict with user data.
        :rtype: Dict
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Tweets(Base):
    """
    Tweets table.
    """

    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True, nullable=False)
    content = Column(String, nullable=False)
    # media_ids = Column(ARRAY(Integer))
    media = relationship("Media", cascade="all, delete", lazy="selectin")
    attachments = association_proxy("media", "filename")
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    author = relationship("Users", back_populates="tweets", lazy="selectin")
    likes = relationship("Users", secondary=Likes.__table__, lazy="selectin")

    @classmethod
    async def get_tweet_by_id(cls, session: AsyncSession, id: int) -> Any | None:
        """
        Returns tweet with given id.
        :param session: Database session.
        :type session: AsyncSession
        :param id: Tweet id.
        :type id: int
        :return: Tweet data
        :rtype: Result
        """
        res = await session.execute(select(cls).filter(cls.id == id))
        return res.unique().scalar_one_or_none()

    @classmethod
    async def get_new_id(cls, session: AsyncSession) -> int:
        """
        Returns id going after last existing.
        :param session: Database session.
        :type session: AsyncSession
        :return: New id.
        :rtype: int
        """
        res = await session.execute(select(cls).order_by(cls.id.desc()))
        last = res.scalars().first()
        print(last)
        if not last:
            return 1
        return int(last.id + 1)


class Media(Base):
    """
    Media table.
    """

    __tablename__ = "media"

    id = Column(Integer, primary_key=True, nullable=False)
    filename = Column(String, nullable=False)
    tweet_id = Column(Integer, ForeignKey("tweets.id", ondelete="CASCADE"))

    @classmethod
    async def get_media_by_id(cls, session: AsyncSession, id: int) -> Any | None:
        """
        Returns media with given id.
        :param session: Database session.
        :type session: AsyncSession
        :param id: Media id.
        :type id: int
        :return: Media data
        :rtype: Result
        """
        res = await session.execute(select(cls).filter(cls.id == id))
        return res.unique().scalar_one_or_none()
