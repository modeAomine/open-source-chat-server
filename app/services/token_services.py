import uuid
from datetime import timedelta, datetime
from jose import jwt, JWTError
from app.config import settings
from app.database import get_db
from app.models.session import Session


def create_access_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta

    to_encode.update({
        "exp": expire,
        "jti": str(uuid.uuid4())
    })

    access_token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return access_token


def create_refresh_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta

    to_encode.update({
        "exp": expire,
        "jti": str(uuid.uuid4())
    })

    refresh_token = jwt.encode(to_encode, settings.REFRESH_SECRET_KEY, algorithm=settings.ALGORITHM)
    return refresh_token


def verify_access_token(token: str) -> dict:
    """
    Верификация JWT access токена. Декодирует токен и проверяет срок действия.
    """
    try:
        # Декодируем токен с использованием секретного ключа
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        return payload
    except JWTError:
        return None


def refresh_user_token(refresh_token: str):
    """
    Использует refresh_token для генерации новой пары токенов.
    """
    try:
        payload = jwt.decode(refresh_token, settings.REFRESH_SECRET_KEY, algorithms=settings.ALGORITHM)

        new_access_token = create_access_token(
            data={"sub": payload.get("sub")},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        new_refresh_token = create_refresh_token(
            data={"sub": payload.get("sub")},
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    except JWTError:
        return None


def revoke_tokens(db: get_db, user_id: int):
    """
    Удаляет все сессии пользователя, аннулируя все активные токены.
    """
    db.query(Session).filter_by(user_id=user_id).delete()
    db.commit()

# def create_refresh_token(data: dict, expires_delta: timedelta, matrix: np.ndarray) -> str:
#     to_encode = data.copy()
#     expire = datetime.utcnow() + expires_delta
#     to_encode.update({"exp": expire})
#
#     encoded_data, salt = encode_data(to_encode, matrix, complex_matrix=True)
#     print("Encoded data shape:", encoded_data.shape)  # Отладка
#
#     encoded_str = ','.join(map(str, encoded_data.flatten()))
#     salt_str = ','.join(map(str, salt.flatten()))
#
#     refresh_token = jwt.encode({"data": encoded_str, "salt": salt_str}, settings.REFRESH_SECRET_KEY, algorithm="HS256")
#     return refresh_token
#
#
# def create_access_token(data: dict, expires_delta: timedelta, matrix: np.ndarray) -> str:
#     to_encode = data.copy()
#     expire = datetime.utcnow() + expires_delta
#     to_encode.update({"exp": expire})
#
#     encoded_data, salt = encode_data(to_encode, matrix, complex_matrix=True)
#     print("Encoded data shape:", encoded_data.shape)  # Отладка
#
#     encoded_str = ','.join(map(str, encoded_data.flatten()))
#     salt_str = ','.join(map(str, salt.flatten()))
#
#     access_token = jwt.encode({"data": encoded_str, "salt": salt_str}, settings.SECRET_KEY, algorithm="HS256")
#     return access_token
#
#
# def decrypt_data(encoded_data: np.ndarray, matrix: np.ndarray) -> np.ndarray:
#     """
#     Расшифровка данных с использованием унитарной матрицы.
#     """
#     print("Unitary matrix shape:", matrix.shape)
#     print("Encoded data shape:", encoded_data.shape)
#
#     # Проверка и исправление размера encoded_data
#     if encoded_data.shape[0] != matrix.shape[1]:
#         encoded_data = encoded_data[:matrix.shape[1]]
#
#     decoded_data = np.dot(np.conj(matrix.T), encoded_data)
#     return decoded_data
#
#
# def decrypt_token(token: str, matrix: np.ndarray, keys: list) -> dict:
#     try:
#         decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
#
#         encoded_data = np.array([complex(x) for x in decoded_token["data"].split(',')])
#         salt = np.array([complex(x) for x in decoded_token["salt"].split(',')]) if decoded_token.get("salt") else np.array([])
#
#         print("Encoded data shape before decryption:", encoded_data.shape)  # Отладка
#         decoded_data = decrypt_data(encoded_data, matrix)
#         print("Decoded data shape after decryption:", decoded_data.shape)  # Отладка
#
#         combined_data = np.concatenate((decoded_data, salt))
#
#         original_data = combined_data[:len(keys)]
#
#         # Преобразование комплексных чисел в строки
#         original_data_str = {key: str(value) for key, value in zip(keys, original_data)}
#
#         return original_data_str
#     except jwt.JWTError:
#         return None
