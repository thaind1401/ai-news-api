from fastapi import APIRouter

router = APIRouter()

@router.get("/articles")
def get_articles():
    return {
        "data": [
        {
            "id": 1,
            "title": "AI Revolutionizes Healthcare",
            "content": "Artificial Intelligence is transforming the healthcare industry by improving diagnostics and patient care."
        },
        {
            "id": 2,
            "title": "AI in Finance: A Game Changer",
            "content": "Financial institutions are leveraging AI to enhance fraud detection and optimize trading strategies."
        },
        {
            "id": 3,
            "title": "AI and the Future of Work",
            "content": "AI is reshaping the job market, creating new opportunities while also posing challenges for workers."       
        },
    ]}