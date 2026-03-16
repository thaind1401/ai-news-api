# Database Tables (AI Signals API)

Tài liệu này mô tả rõ các bảng hiện có trong database dựa trên định nghĩa tại `app/database/models.py`.

## 1) Tổng quan nhanh

| Table | Mục đích | PK | FK chính |
|---|---|---|---|
| `sources` | Danh mục nguồn dữ liệu crawl/ingest | `id` | - |
| `source_fetch_runs` | Log từng lần fetch theo nguồn | `id` | `source_id -> sources.id` |
| `raw_items` | Dữ liệu thô sau khi crawl | `id` | `source_id -> sources.id`, `fetch_run_id -> source_fetch_runs.id` |
| `companies` | Chuẩn hóa doanh nghiệp | `id` | - |
| `topics` | Chuẩn hóa chủ đề | `id` | - |
| `signals` | Bản ghi tín hiệu chính (public/internal) | `id` | `source_id`, `raw_item_id`, `company_id`, `primary_topic_id` |
| `signal_ai_enrichments` | Kết quả AI enrichment cho signal | `id` | `signal_id -> signals.id` |
| `signal_embeddings` | Vector embedding cho semantic search | `id` | `signal_id -> signals.id` |
| `users` | Người dùng hệ thống | `id` | - |
| `bookmarks` | Đánh dấu signal theo user | `id` | `user_id -> users.id`, `signal_id -> signals.id` |
| `user_preferences` | Preference cá nhân hóa | `id` | `user_id -> users.id` |
| `watchlists` | Theo dõi company/topic/event | `id` | `user_id -> users.id` |
| `digests` | Bản tổng hợp daily/weekly | `id` | `user_id -> users.id` |
| `chat_sessions` | Phiên chat | `id` | `user_id -> users.id` |
| `chat_messages` | Tin nhắn trong phiên chat | `id` | `session_id -> chat_sessions.id` |

---

## 2) Chi tiết từng bảng

## `sources`
- Mục đích: lưu metadata nguồn dữ liệu.
- Cột chính: `name` (unique), `source_type`, `base_url`, `ingest_method`, `risk_level`, `status`, `owner`.
- Cờ compliance: `terms_reviewed`, `robots_reviewed`, `auth_required`, `paywall`, `store_full_text`.
- Ràng buộc:
  - `risk_level IN ('A','B','C')`
  - `status IN ('active','paused','blocked')`

## `source_fetch_runs`
- Mục đích: theo dõi từng run fetch của một source.
- Cột chính: `source_id`, `status`, `started_at`, `finished_at`, `items_fetched`, `items_created`, `error_message`, `run_metadata`.
- Ràng buộc: `status IN ('running','success','failed')`.

## `raw_items`
- Mục đích: lưu dữ liệu thô trước bước chuẩn hóa/public.
- Cột chính: `source_id`, `source_url`, `title`, `published_at`, `raw_payload`, `parse_status`, `parse_error`, `fetched_at`.
- Ràng buộc:
  - Unique (`source_id`, `source_url`)
  - Unique (`source_id`, `external_id`)
  - `parse_status IN ('pending','parsed','failed')`

## `companies`
- Mục đích: từ điển doanh nghiệp chuẩn hóa để join/filter.
- Cột chính: `name`, `normalized_name` (unique), `website`, `domain`, `company_type`, `country_code`.

## `topics`
- Mục đích: từ điển chủ đề chuẩn hóa.
- Cột chính: `name` (unique), `slug` (unique), `description`.

## `signals`
- Mục đích: bảng nghiệp vụ trung tâm cho API signals.
- Cột chính:
  - Nguồn: `source_id`, `raw_item_id`, `source_url`
  - Nội dung: `title`, `raw_excerpt`, `author_name`, `image_url`, `published_at`, `crawl_time`
  - Phân loại: `company_id`, `primary_topic_id`, `event_type`
  - Quản trị: `dedup_key`, `signal_status`, `visibility`
- Ràng buộc:
  - Unique `dedup_key`
  - `event_type IN ('funding','product_launch','hiring','partnership','acquisition','market_move','regulation','competitor_update')`
  - `signal_status IN ('active','hidden','rejected')`
  - `visibility IN ('public','internal')`
- Ghi chú pipeline hiện tại: signal được tạo ở `hidden/internal`, sau AI enrichment sẽ chuyển `active/public`.

## `signal_ai_enrichments`
- Mục đích: lưu output AI cho mỗi signal (1-1).
- Cột chính: `signal_id` (unique), `summary_one_line`, `summary_bullets`, `why_it_matters`, `tags`, `importance_score`, `confidence_score`, `company_name_extracted`, `topic_extracted`, `event_type_extracted`, `model_name`, `prompt_version`, `enrichment_status`, `error_message`.
- Ràng buộc:
  - `importance_score` trong [1..5] (hoặc null)
  - `enrichment_status IN ('pending','done','failed')`

## `signal_embeddings`
- Mục đích: phục vụ semantic retrieval/search.
- Cột chính: `signal_id` (unique), `embedding_text`, `embedding_model`, `embedding` (JSON vector).

## `users`
- Mục đích: người dùng hệ thống.
- Cột chính: `email` (unique), `password_hash`, `role`, `status`.
- Ràng buộc:
  - `role IN ('user','admin')`
  - `status IN ('active','disabled')`

## `bookmarks`
- Mục đích: user lưu signal quan tâm.
- Cột chính: `user_id`, `signal_id`, `created_at`.
- Ràng buộc: Unique (`user_id`, `signal_id`).

## `user_preferences`
- Mục đích: cấu hình cá nhân hóa.
- Cột chính: `user_id` (unique), `preferred_topics`, `preferred_event_types`, `preferred_companies`, `digest_enabled`, `updated_at`.

## `watchlists`
- Mục đích: danh sách theo dõi theo loại đối tượng.
- Cột chính: `user_id`, `watch_type`, `watch_value`, `created_at`.
- Ràng buộc:
  - Unique (`user_id`, `watch_type`, `watch_value`)
  - `watch_type IN ('company','topic','event_type')`

## `digests`
- Mục đích: bản tổng hợp gửi theo chu kỳ.
- Cột chính: `user_id`, `digest_date`, `digest_type`, `title`, `content`.
- Ràng buộc: `digest_type IN ('daily','weekly')`.

## `chat_sessions`
- Mục đích: phiên hội thoại giữa user và assistant.
- Cột chính: `user_id`, `title`, `created_at`, `updated_at`.

## `chat_messages`
- Mục đích: lịch sử message trong từng session.
- Cột chính: `session_id`, `role`, `content`, `sources`, `model_name`, `created_at`.
- Ràng buộc: `role IN ('user','assistant','system')`.

---

## 3) Quan hệ chính (ngắn gọn)

- `sources (1) -> (N) source_fetch_runs`
- `sources (1) -> (N) raw_items`
- `sources (1) -> (N) signals`
- `raw_items (1) -> (1) signals` (qua `signals.raw_item_id` unique)
- `signals (1) -> (1) signal_ai_enrichments`
- `signals (1) -> (1) signal_embeddings`
- `companies (1) -> (N) signals`
- `topics (1) -> (N) signals`
- `users (1) -> (N) bookmarks/watchlists/digests/chat_sessions`
- `chat_sessions (1) -> (N) chat_messages`
