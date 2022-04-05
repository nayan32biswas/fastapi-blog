from fastapi import HTTPException, status
from firebase_admin import auth
import requests


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

        return simplified_token
    except Exception as e:
        print("Error While Decoding FireJWT:", str(e))
        return None


def create_user(email, password):
    user = auth.create_user(email=email, password=password)
    return user


API_KEY = "AIzaSyC-JjPNxTM3IEXwVponhpgKjv3S2Xgf8Lw"


def create_user_token_from_id(uid):
    """This is a another way to get firebase token"""
    token = auth.create_custom_token(uid)
    print(token)

    req = requests.post(
        f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyCustomToken?key={API_KEY}",
        {"token": token},
    )
    data = req.json()
    return {
        "token": data.get("idToken"),
        "refresh_token": data.get("refreshToken"),
    }


def get_or_create_firebase_token(email, password):
    data = {
        "email": email,
        "password": password,
    }

    req = requests.post(
        f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={API_KEY}",
        json={
            **data,
            # "returnSecureToken": True,
        },
    )
    req_body = req.json()
    if req.status_code == 200:
        data = req_body
        # print(data)
        return {
            "token": data.get("idToken"),
            "refresh_token": data.get("refreshToken"),
        }
    if (
        req.status_code == 400
        and req_body.get("error", {}).get("message") == "EMAIL_NOT_FOUND"
    ):
        user = create_user(email, password)
        uid = user.uid
        # Or you can re verify credentials by calling get_or_create_firebase_token()
        return create_user_token_from_id(uid)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
    )
