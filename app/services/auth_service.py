from app.models.user import User

from app.core.security import verify_password
def authenticate_user ( db, email, password):
    existing_user = db.query(User).filter(User.email ==email).first()
    if not existing_user:
        return None
    is_pass_true = verify_password(password,existing_user.hashed_pass)
    if not is_pass_true:
        return None
    return existing_user