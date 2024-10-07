from fastapi import APIRouter, Depends
from starlette.websockets import WebSocket
from app.database import get_db
from app.models.session import Session
from app.models.user import User

router = APIRouter()


@router.websocket("/ws/users")
async def search_users(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()

    try:
        while True:
            search_query = await websocket.receive_text()
            results = db.query(User).filter(User.username.ilike(f"%{search_query}%")).all()
            await websocket.send_json([{
                "id": user.id,
                "username": user.username,
                "filename": f"http://127.0.0.1:8000/{user.filename.replace('\\', '/')}" if user.filename else None
            } for user in results])
    except Exception as e:
        print(f"Error: {e}")
        await websocket.send_json({"error": "Произошла ошибка при выполнении поиска."})
    finally:
        await websocket.close()
