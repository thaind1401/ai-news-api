# AI Signals API

Backend FastAPI cho hướng sản phẩm Startup / Market Intelligence theo mô hình `signal/event`.

## Cấu trúc chính

```text
app/
  main.py
  crawlers/
    crawler.py
    news_crawler.py
  database/
    db.py
    init_db.py
    models.py
  models/
    common.py
    chat.py
    signal.py
  routers/
    chat.py
    signals.py
  services/
    chat_service.py
    ingestion_service.py
    signal_service.py
```

## Yêu cầu môi trường

- Python 3.11+
- PostgreSQL
- Biến môi trường DB (tùy chọn):
  - `DATABASE_URL`
  - hoặc `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`

## Chạy nhanh

```bash
make venv
make install
make init-db
make run
```

Lệnh hữu ích:

```bash
make help
make status
make smoke
make stop
make restart
```

## Luồng dữ liệu hiện tại

1. `run_crawler()` chạy khi startup và mỗi 3 phút.
2. Crawl link mới từ VnExpress.
3. Parse nội dung và ghi vào schema v2:
   - `sources`
   - `raw_items`
   - `signals`
   - `signal_ai_enrichments`
4. Dedupe baseline:
   - theo `source_url`
   - theo `title similarity`
   - theo `company + event_type` (heuristic)

## API

### Health

```bash
curl http://localhost:8000/health
```

### Signals list

```bash
curl "http://localhost:8000/api/v1/signals?page=1&size=10"
```

Filters hỗ trợ:
- `q`
- `source`
- `company`
- `topic`
- `event_type`
- `from`
- `to`
- `sort` (`newest|oldest`)

### Signal detail

```bash
curl http://localhost:8000/api/v1/signals/1
```

### Trending signals

```bash
curl "http://localhost:8000/api/v1/signals/trending?limit=10&within_hours=24"
```

### Topics

```bash
curl http://localhost:8000/api/v1/topics
```

### Companies

```bash
curl http://localhost:8000/api/v1/companies
```

### Chat (stub)

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"hello"}'
```

## Ghi chú

- Dự án vận hành theo hướng signals-first.
- API runtime hiện tại chỉ phục vụ schema v2.
