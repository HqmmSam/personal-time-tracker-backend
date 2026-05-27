from sqlalchemy.orm import Session

from app.models.user_settings import UserSettings
from app.schemas.stats import SettingsUpdate


class SettingsService:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create(self, user_id: int) -> UserSettings:
        s = self.db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
        if not s:
            s = UserSettings(user_id=user_id)
            self.db.add(s)
            self.db.commit()
            self.db.refresh(s)
        return s

    def update(self, user_id: int, payload: SettingsUpdate) -> UserSettings:
        s = self.get_or_create(user_id)
        data = payload.model_dump(exclude_unset=True)
        for k, v in data.items():
            setattr(s, k, v)
        self.db.commit()
        self.db.refresh(s)
        return s
