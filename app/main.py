import logging
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from app.crawlers.crawler import run_crawler
from app.routers import news, articles, chat

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(timezone="Asia/Ho_Chi_Minh")

@asynccontextmanager
async def lifespan(_: FastAPI):
    await run_crawler()  # chạy 1 lần ngay lúc start
    scheduler.add_job(
        run_crawler,
        "interval",
        minutes=3,
        id="vnexpress_crawler",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    scheduler.start()
    try:
        yield
    finally:
        scheduler.shutdown(wait=False)

app = FastAPI(lifespan=lifespan)
app.include_router(news.router)
app.include_router(articles.router)
app.include_router(chat.router)