# AI Signals API

Backend FastAPI cho hướng sản phẩm Startup / Market Intelligence theo mô hình `signal/event`.

## Cấu trúc thư mục (đã chuẩn hóa)

```text
app/
  main.py
  api/
    routers/
      health.py
      signals.py
      search.py
      chat.py
      users.py
      digests.py
      internal_jobs.py
  core/
    config.py
    logging.py
    security.py
  ingestion/
    scheduler.py
    sources/
      registry.py
      sources.json
    parsers/
      news_parser.py
    workers/
      types.py
      rss_worker.py
      homepage_worker.py
      source_discovery.py
      source_worker.py
      pipeline.py
  normalization/
    normalizer.py
    dedupe.py
  ai/
    prompts/
    enrichers/
    embeddings/
    retrieval/
    chat/
  schemas/
    signal.py
    search.py
    chat.py
    digest.py
  services/
    signal_service.py
    search_service.py
    chat_service.py
    digest_service.py
    ingestion_service.py
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
make reingest
make re-enrich
```

## Luồng dữ liệu hiện tại

1. `run_crawler()` chạy khi startup và theo lịch scheduler.
2. Crawl link mới từ các nguồn đang `enabled` trong `app/ingestion/sources/sources.json`.
3. Mỗi source trong mỗi run đều ghi log vào `source_fetch_runs` (status, số link, số item tạo, lỗi).
4. Parse nội dung và ghi **phase 1** vào schema v2:
   - `sources`
   - `raw_items`
     - `signals` (trạng thái chờ AI: `hidden/internal`)
5. Chạy **phase 2 AI enrichment**:
     - queue `pending`: enrich signal mới
     - queue `failed`: retry enrichment lỗi theo job riêng
     - tạo/cập nhật `signal_ai_enrichments`
     - publish signal sang `active/public`
6. Dedupe baseline:
   - theo `source_url`
   - theo `title similarity`
   - theo `company + event_type` (heuristic)

## Chuẩn hóa source workers

Phần ingestion source đã tách theo đúng cấu trúc worker:

- `source fetcher/discovery`: `app/ingestion/workers/source_discovery.py`
- `source parser`: `app/ingestion/parsers/news_parser.py`
- `source worker`: `app/ingestion/workers/source_worker.py`
- `scheduler`: `app/main.py` (job crawl + retry enrichment)
- `crawl logger`: `source_fetch_runs` + metadata theo từng source run

## Cấu hình nguồn crawl

File cấu hình: `app/ingestion/sources/sources.json`

- `enabled: true/false` để bật/tắt nguồn.
- `discovery.type` hỗ trợ:
  - `homepage_css`: lấy link bằng CSS selector từ trang chủ.
  - `rss`: lấy link từ RSS/Atom feed.
- `detail_parser` hỗ trợ:
  - `vnexpress`: parser tối ưu cho VnExpress.
  - `generic_meta`: parser generic cho đa số site dùng meta tags.

Ví dụ bật một nguồn:

```json
{
  "name": "openai_blog",
  "enabled": true,
  "source_type": "official_blog",
  "base_url": "https://openai.com",
  "ingest_method": "rss",
  "detail_parser": "generic_meta",
  "discovery": {
    "type": "rss",
    "url": "https://openai.com/blog/rss.xml"
  }
}
```

Tuỳ chọn đổi đường dẫn file config bằng biến môi trường:

```bash
export SOURCES_CONFIG_PATH=/path/to/your/sources.json
```

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

### Internal: re-ingest thủ công

Thiết lập key:

```bash
export INTERNAL_API_KEY="your-secret-key"
```

Hoặc đặt trong file `.env` ở root project:

```dotenv
INTERNAL_API_KEY=your-secret-key
```

Bạn có thể tạo nhanh từ file mẫu:

```bash
cp .env.example .env
```

```bash
curl -X POST http://localhost:8000/api/internal/reingest \
  -H "X-Internal-Key: $INTERNAL_API_KEY"
```

### Internal: re-enrich thủ công

```bash
curl -X POST "http://localhost:8000/api/internal/re-enrich?pending_limit=500&failed_retry_limit=500" \
  -H "X-Internal-Key: $INTERNAL_API_KEY"
```

## Ghi chú

- Dự án vận hành theo hướng signals-first.
- API runtime hiện tại chỉ phục vụ schema v2.
