from mongoengine import connect, Document, StringField

from .config import DB_URL

try:
    connect_to_db = connect(host=DB_URL)
    print(f"\n\nConnected to DB: {connect_to_db}")
except Exception as e:
    print(f"\n\nDB Connection Error: {e}")


class User(Document):
    name = StringField()


user = User(name="Demo Name")
print("User obj:", user)
# user.save()
# print("user.id:", user.id)

# print(User.objects.all())

# print("users")
