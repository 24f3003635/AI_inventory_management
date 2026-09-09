from werkzeug.security import generate_password_hash

from app.database import db
from app.models import User


def create_default_admin():
    try:
        admin_username = "admin@gmail.com"
        admin_password = "admin_123"

        admin_user = User.query.filter_by(username=admin_username).first()

        if not admin_user:
            hashed_password = generate_password_hash(admin_password, method="pbkdf2:sha256")
            
            new_admin = User(username=admin_username, password_hash=hashed_password, role="admin")
            db.session.add(new_admin)
            db.session.commit()
            print(f"Default admin user '{admin_username}' created.")
        else:
            print(f"Admin user '{admin_username}' already exists.")
    except Exception as e:  # noqa: BLE001
        print(f"Error creating admin user: {e}")
        print(f"Error type: {type(e)}")
