"""
Servicio de autenticación: registro, login y sesión activa.
"""
import bcrypt
from sqlalchemy.exc import IntegrityError
from src.models import User, get_session

# Sesión en memoria (reemplazable por JWT en producción)
_current_user: User | None = None


def get_current_user() -> User | None:
    return _current_user


def set_current_user(user: User | None):
    global _current_user
    _current_user = user


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def register_user(name: str, email: str, password: str, phone: str = "", position: str = "Cualquiera") -> tuple[bool, str]:
    """
    Registra un nuevo usuario.
    Retorna (éxito: bool, mensaje: str).
    """
    if not name or not email or not password:
        return False, "field_required"
    if "@" not in email:
        return False, "invalid_email"
    if len(password) < 6:
        return False, "password_min"

    session = get_session()
    try:
        user = User(
            name=name.strip(),
            email=email.strip().lower(),
            password_hash=hash_password(password),
            phone=phone.strip(),
            position=position,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        set_current_user(user)
        return True, "register_success"
    except IntegrityError:
        session.rollback()
        return False, "email_taken"
    finally:
        session.close()


def login_user(email: str, password: str) -> tuple[bool, str]:
    """
    Autentica al usuario.
    Retorna (éxito: bool, mensaje: str).
    """
    session = get_session()
    try:
        user = session.query(User).filter_by(email=email.strip().lower()).first()
        if not user or not verify_password(password, user.password_hash):
            return False, "login_error"
        # Detach del session para uso fuera de la sesión
        session.expunge(user)
        set_current_user(user)
        return True, "welcome"
    finally:
        session.close()


def logout_user():
    set_current_user(None)
