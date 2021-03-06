import json

from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_raw_jwt
from flask_restful import reqparse, Resource
from werkzeug.security import safe_str_cmp

from config.common import BLACKLIST_TOKEN, app
from model.users import UserModel

_user_parser = reqparse.RequestParser()
_user_parser.add_argument('username', type=str, required=True)
_user_parser.add_argument('password', type=str, required=True)


class UserRegister(Resource):
    def post(self):
        params = _user_parser.parse_args()
        user = UserModel.find_by_username(params['username'])
        if user:
            return {"msg": f"{user.username} already exists"}, 400
        user_model = UserModel(**params)
        try:
            user_model.save()
        except:
            return {"msg": f"{params['username']} save fails"}, 400
        data = {
            'id': user_model.id,
            'username': user_model.username,
            'room_private': user_model.room_private,
        }
        return data, 200


class UserLogin(Resource):
    def post(self):
        params = _user_parser.parse_args()
        user = UserModel.find_by_username(params['username'])
        if user and safe_str_cmp(user.password, params['password']):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)
            data = {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'id': user.id,
                'username': user.username,
                'room_private': user.room_private,
            }
            return data, 200
        return {"msg": f"{params['username']} with password {params['password']} login fails"}, 400


class UserLogout(Resource):

    @jwt_required
    def post(self):
        token = get_raw_jwt()['jti']
        BLACKLIST_TOKEN.add(token)
        return {'msg': 'logout ok'}, 200
