from firebase_admin import auth
import requests
import json


def decode_firetoken(token):
    try:
        decoded_token = auth.verify_id_token(token)
        simplified_token = dict()
        simplified_token["uid"] = decoded_token["uid"]
        simplified_token["name"] = decoded_token.get("name", "")
        simplified_token["photo_link"] = decoded_token.get("picture", "")
        simplified_token["firebase_user_id"] = decoded_token.get("user_id")
        simplified_token["email"] = decoded_token.get("email", "")
        simplified_token["email_verification"] = decoded_token.get("email_verified")

        return 1, simplified_token
    except Exception as e:
        print("Error While Decoding FireJWT:", str(e))
        return 0, None


def create_user(email="example@example.com", password="exampelpass"):
    user = auth.create_user(email=email, password=password)
    return user


def create_user_token(uid):
    API_KEY = "AIzaSyC-JjPNxTM3IEXwVponhpgKjv3S2Xgf8Lw"

    token = auth.create_custom_token(uid)
    data = {"token": token, "returnSecureToken": True}

    url = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyCustomToken?key={API_KEY}"
    req = requests.post(url, data, {"Content-Type": "application/json"})
    data = json.loads(req.content.decode())

    return data.get("idToken")
