from flask_login import UserMixin


class UserLogin(UserMixin):
    """Special class for getting data about a specific user"""

    def from_db(self, user_id, db):
        self.__user = db.get_user(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user['id'])

    def get_name(self):
        return str(self.__user['name'])

    def get_email(self):
        return str(self.__user['email'])
