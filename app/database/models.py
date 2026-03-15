from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database.db import Base
import datetime

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    sub_title = Column(Text)
    image = Column(String(1000))
    author = Column(String(255))
    category = Column(String(100))
    content = Column(Text)
    published_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
