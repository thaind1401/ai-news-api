run:
	/usr/local/bin/python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

stop:
	pkill -f "uvicorn app.main:app" || true
