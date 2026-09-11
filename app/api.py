from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash

from app.database import db
from app.models import User

api_bp=Blueprint("api",__name__)

@api_bp.route("/test")          
def test():
    return jsonify({"message":"api working"})

@api_bp.route("/login",methods=["POST"])
def login():
    data=request.get_json()
    username=data.get("username")
    password=data.get("password")
    user=User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'message':'user does not exist'})
    else:
        if check_password_hash(user.password_hash,password ):
            token=create_access_token(identity=str(user.id))
            print(f'token: {token}')
            return jsonify({'message':'Login successful','token':token,'role':user.role})
        else:
            return jsonify({'message':'Invalid password '})

@api_bp.route("/sign-up",methods=["POST"])
def sign_up():
    try:
        data=request.get_json()
        username=data.get("username")
        password=data.get("password_hash")
        existing_user=User.query.filter_by(username=username).first()
        if existing_user :
            return jsonify({'message':'User already exist'})
        hasshed_password=generate_password_hash(password, method="pbkdf2:sha256")
        new_user=User(username=username,password_hash=hasshed_password,role="staff")
        db.session.add(new_user)
        db.session.commit()
        print(f"New user created with ID: {new_user.id}") 

        return jsonify({'message':'Registration Successful'})
    except Exception as e:  # noqa: BLE001
        db.session.rollback()
        print(f"Registration error: {e}") 
        return jsonify({'message':'Registration Failed'})
        
