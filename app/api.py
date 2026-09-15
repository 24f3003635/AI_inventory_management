from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import check_password_hash, generate_password_hash

from app.database import db
from app.models import OosEvent, User

api_bp=Blueprint("api",__name__)

@api_bp.route("/test")          
def test():
    return jsonify({"message":"api working"})

@api_bp.route("/login",methods=["POST","GET"])
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
        password=data.get("password")
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
        

@api_bp.route("/Out_of_stock",methods=['GET'])
@jwt_required()
def Out_of_stock():
    current_user=get_jwt_identity()
    user=User.query.filter_by(id=current_user).first()
    if not user or user.role not in ['admin' ,'manager']:
        return jsonify({'message':'unauthorized access'}) 

    rows=OosEvent.query.all()
    data=[{
        "id":row.id,
        "shelf_zone":row.shelf_zone,
        "sku_id":row.sku_id,
        "detected_at":row.detected_at,
        "resolved_at":row.resolved_at,
        "status":row.status,
        "Duration_secs":row.duration_secs
    } for row in rows]
    return jsonify(data)
