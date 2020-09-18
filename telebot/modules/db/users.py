from typing import Optional

from mongoengine import StringField, DynamicDocument, IntField


# create models for this module


class User(DynamicDocument):
    id = IntField(primary_key=True)  # ID of the user
    username = StringField()  # username of the user

    def __str__(self):
        return f"<User {self.username} : {self.id}>"

    def __repr__(self):
        return f"<User {self.username} : {self.id}>"


# create helper functions to be used to interact with the model


def add_user(user_id: int, username: str):
    """
    Add/Update a user in the database
    :param user_id: ID of the user we want to add
    :param username: username of the user we want to add
    :return:
    """
    User(id=user_id, username=username).save()


def get_user(username: str) -> Optional[int]:
    """
    get the user ID of a user
    :param username: username of the user who's ID we want to fetch
    :return: ID of the user
    """
    user = User.objects(username=username).first()
    if user:
        return user.id
    else:
        return None
