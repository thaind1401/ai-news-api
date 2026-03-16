# Startup / Market Intelligence Assistant Roadmap

Tài liệu này dùng để theo dõi backlog, tiến độ và thứ tự triển khai cho sản phẩm Startup / Market Intelligence Assistant.

Roadmap này đã được đồng bộ theo hướng sản phẩm mới:
- không còn đi theo hướng app đọc tin tức tổng hợp
- tập trung vào `signal/event`, `AI summary`, `search`, `chat`, `digest` và `market intelligence`
- bám sát [PRODUCT_PLAN.md](PRODUCT_PLAN.md) và [ARCHITECTURE.md](ARCHITECTURE.md)

## Mục tiêu sản phẩm

| Mục tiêu | Mô tả |
| --- | --- |
| Xây sản phẩm intelligence có thể dùng được | Có data pipeline, backend, AI và app phục vụ founder / PM / analyst |
| Học theo hướng AI Solution Engineer | Đi qua backend, ingestion, enrichment, retrieval, RAG, evaluation |
| Ra MVP sớm nhưng mở rộng được | Bắt đầu bằng monolith có kỷ luật, sau đó tách worker/service khi cần |

## Nguyên tắc triển khai

| Nguyên tắc | Ý nghĩa |
| --- | --- |
| Signal trước article | Xây dữ liệu theo `signal/event`, không theo `full article mirror` |
| Dữ liệu an toàn trước mở rộng nguồn | Ưu tiên nguồn public chính thức, giảm rủi ro bản quyền |
| AI chạy sau pipeline dữ liệu | Phải có normalize, dedup, metadata sạch trước khi enrich |
| Search và chat phải grounded | Mọi câu trả lời AI cần dựa trên signal đã lưu và có nguồn tham chiếu |
| Mỗi giai đoạn phải có deliverable thật | Không để roadmap chỉ dừng ở ý tưởng |

## Kanban Tổng Quan

### Now

Đây là các việc cần làm ngay để hoàn thiện nền tảng `market intelligence product`.

| Nhóm việc | Hạng mục | Kết quả mong đợi |
| --- | --- | --- |
| Product scope | Chốt persona, use case, value proposition | Sản phẩm có định vị rõ ràng |
| Data policy | Chốt nguồn dữ liệu an toàn và nguyên tắc ingest | Giảm rủi ro bản quyền / ToS |
| Data model | Thiết kế `sources`, `raw_items`, `signals`, `companies`, `topics` | Có schema đúng với hướng signal/event |
| Backend foundation | Health, signals API, search API, source registry | App/web gọi được API nền tảng |

### Next

Đây là phần tạo giá trị AI và intelligence cho sản phẩm.

| Nhóm việc | Hạng mục | Kết quả mong đợi |
| --- | --- | --- |
| AI enrichment | Summary, why it matters, tags, topic, event type, importance | Mỗi signal có lớp insight AI |
| Search thông minh | Keyword search + semantic retrieval + rerank | Tìm thông tin theo nhu cầu thực tế |
| Chat RAG | Hỏi đáp theo dữ liệu đã ingest | Có assistant thật sự, không trả lời chung chung |
| Digest | Daily brief theo signal quan trọng | Tạo thói quen quay lại hằng ngày |

### Later

Đây là phần nâng sản phẩm lên mức có retention và cá nhân hóa.

| Nhóm việc | Hạng mục | Kết quả mong đợi |
| --- | --- | --- |
| User system | Auth, profile, bookmark, history | Có user flow riêng cho từng người dùng |
| Personalization | Watchlist, feed cá nhân hóa, alert | Tăng giá trị sử dụng dài hạn |
| Productization | Dashboard, evaluation, cost tracking, demo polish | Sẵn sàng demo và mở rộng quy mô |

## Timeline 10 Tuần

Quy ước trạng thái:
- `DONE`: hoàn thành ở mức MVP hiện tại
- `IN_PROGRESS`: đã có phần nền, còn hạng mục chưa hoàn tất
- `TODO`: chưa bắt đầu

| Tuần | Giai đoạn | Trọng tâm | Deliverable chính | Trạng thái |
| --- | --- | --- | --- | --- |
| 1 | Product & Data Policy | Chốt phạm vi sản phẩm và chính sách dữ liệu | Persona, use case, source policy, event taxonomy | DONE |
| 2 | Data Foundation | Thiết kế schema signal/event và ingestion foundation | Sources, raw_items, signals, health, scheduler | DONE |
| 3 | Ingestion | Kết nối nguồn an toàn, normalize, dedup | 5-10 nguồn ingest ổn định | IN_PROGRESS |
| 4 | Backend APIs | Signals API, companies, topics, search, trending | API dùng được cho app/web | IN_PROGRESS |
| 5 | AI Enrichment | Summary, event type, topic, tags, importance | Signal có AI insight | IN_PROGRESS |
| 6 | Retrieval | Embeddings, semantic search, rerank | Search thông minh khả dụng | TODO |
| 7 | Chat RAG | Q&A grounded trên signal | Chat có nguồn tham chiếu | TODO |
| 8 | Digest & Alert | Daily digest, watchlist, alert logic | Daily Brief khả dụng | TODO |
| 9 | User & Personalization | Auth, bookmark, preferences, personalized feed | User flow hoàn chỉnh bản đầu | TODO |
| 10 | Productization | Evaluation, cost, polish, demo | MVP end-to-end hoàn chỉnh | TODO |

## Roadmap Chi Tiết Theo Tuần

## Tuần 1: Chốt phạm vi sản phẩm và chính sách dữ liệu

Mục tiêu: Khóa hướng sản phẩm và nguyên tắc dữ liệu để không build sai từ đầu.

| Hạng mục | Loại | Trạng thái |
| --- | --- | --- |
| Chốt 1 user persona chính | Product | [x] |
| Chốt 3 pain points chính | Product | [x] |
| Viết 1 câu định vị sản phẩm | Product | [x] |
| Xác định 5 câu hỏi mẫu người dùng sẽ hỏi | Product | [x] |
| Lập danh sách 20-30 nguồn dữ liệu tiềm năng | Data | [x] |
| Phân loại nguồn theo `an toàn / cần cẩn thận / tránh` | Data Policy | [x] |
| Viết nguyên tắc ingest dữ liệu | Data Policy | [x] |
| Chuẩn hóa taxonomy `event_type` bản đầu | Product / Data | [x] |

Deliverable:
- Persona rõ ràng
- Value proposition rõ ràng
- Source policy rõ ràng
- Event type taxonomy bản đầu

## Tuần 2: Thiết kế schema signal/event và hạ tầng dữ liệu nền

Mục tiêu: Hoàn thiện hệ thống theo mô hình `signal/event`.

| Hạng mục | Loại | Trạng thái |
| --- | --- | --- |
| Thiết kế bảng `sources` | Backend / DB | [x] |
| Thiết kế bảng `raw_items` | Backend / DB | [x] |
| Thiết kế bảng `signals` | Backend / DB | [x] |
| Thiết kế bảng `companies` | Backend / DB | [x] |
| Thiết kế bảng `topics` | Backend / DB | [x] |
| Thiết kế bảng `signal_ai_enrichments` | Backend / DB | [x] |
| Tạo script khởi tạo schema mới | Backend / DB | [x] |
| Thêm source registry | Backend | [x] (mức schema trong bảng `sources`) |
| Thêm `GET /health` | Backend | [x] |
| Thêm logging nền cho ingestion pipeline | Vận hành | [x] |

Deliverable:
- Schema signal/event hoàn chỉnh bản đầu
- Health endpoint
- Cấu trúc DB sẵn sàng cho ingestion mới

## Tuần 3: Xây ingestion cho nguồn an toàn, normalize và dedup

Mục tiêu: Có pipeline ingest dữ liệu ổn định từ nguồn rủi ro thấp.

| Hạng mục | Loại | Trạng thái |
| --- | --- | --- |
| Kết nối 5-10 nguồn public an toàn | Ingestion | [ ] (đã có 1 nguồn: VnExpress) |
| Viết parser theo từng nguồn | Ingestion | [x] (baseline cho 1 nguồn) |
| Chuẩn hóa dữ liệu về signal format | Normalization | [x] |
| Lưu raw payload để debug | Backend / DB | [x] |
| Dedupe theo URL | Normalization | [x] (baseline theo `source_url`) |
| Dedupe theo title similarity | Normalization | [x] (baseline) |
| Dedupe theo company + event type | Normalization | [x] (baseline heuristic) |
| Thêm retry và crawl failure logging | Vận hành | [x] |

Deliverable:
- Ingest ổn định từ nhóm nguồn đầu tiên
- Signal được chuẩn hóa và giảm trùng lặp

## Tuần 4: Hoàn thiện Signal APIs cho app/web

Mục tiêu: Có backend API chuẩn cho signal feed, detail và search.

| Hạng mục | Loại | Trạng thái |
| --- | --- | --- |
| Thêm `GET /api/v1/signals` | Backend | [x] |
| Thêm `GET /api/v1/signals/{id}` | Backend | [x] |
| Thêm `GET /api/v1/companies` | Backend | [x] |
| Thêm `GET /api/v1/topics` | Backend | [x] |
| Thêm `GET /api/v1/search` | Backend | [ ] |
| Thêm `GET /api/v1/trending` | Backend | [ ] (đã có `/api/v1/signals/trending`) |
| Thêm filter theo `company` | Backend | [x] |
| Thêm filter theo `topic` | Backend | [x] |
| Thêm filter theo `event_type` | Backend | [x] |
| Thêm filter theo `source` | Backend | [x] |
| Thêm filter theo `date range` | Backend | [x] |
| Hoàn thiện docs API | Tài liệu | [x] (README baseline) |

Deliverable:
- App/web có thể dựng feed signal và detail bằng API thật

## Tuần 5: AI enrichment v1

Mục tiêu: Thêm lớp insight AI vào từng signal.

| Hạng mục | Loại | Trạng thái |
| --- | --- | --- |
| Sinh `summary_one_line` | AI | [x] (baseline rule-based) |
| Sinh `summary_bullets` | AI | [x] (baseline rule-based) |
| Sinh `why_it_matters` | AI | [x] (baseline rule-based) |
| Trích xuất `company_name` | AI | [ ] |
| Gắn `topic` | AI | [x] (mapping từ category) |
| Gắn `event_type` | AI | [x] (baseline `market_move`) |
| Sinh `tags` | AI | [x] (baseline từ category) |
| Tính `importance_score` | AI | [x] (baseline mặc định) |
| Tạo async enrichment jobs | AI Pipeline | [ ] |
| Lưu `model_name` và `prompt_version` để audit | AI / DB | [x] |

Deliverable:
- Mỗi signal mới có AI summary và metadata enrichment

## Tuần 6: Search thông minh và retrieval

Mục tiêu: Từ keyword search chuyển sang retrieval phục vụ AI assistant.

| Hạng mục | Loại | Trạng thái |
| --- | --- | --- |
| Tạo embeddings cho signal | AI | [ ] |
| Lưu vector index | AI / DB | [ ] |
| Thêm semantic retrieval | AI Retrieval | [ ] |
| Kết hợp keyword + semantic search | Backend / AI | [ ] |
| Thêm rerank logic | AI Retrieval | [ ] |
| Tối ưu search response cho app/web | Backend | [ ] |

Deliverable:
- Search hoạt động ở cả mức keyword và semantic

## Tuần 7: Chat RAG trên signal store

Mục tiêu: Biến sản phẩm thành market intelligence assistant thật sự.

| Hạng mục | Loại | Trạng thái |
| --- | --- | --- |
| Thêm `POST /api/v1/chat` | Backend | [ ] |
| Thiết kế request/response chat | Backend | [ ] |
| Retrieve signal liên quan | AI Retrieval | [ ] |
| Build grounded context | AI | [ ] |
| Generate answer có source reference | AI | [ ] |
| Lưu chat session và chat messages | Backend / DB | [ ] |
| Thêm fallback khi context yếu | AI | [ ] |

Deliverable:
- Chat trả lời được dựa trên signal đã ingest và có nguồn tham chiếu

## Tuần 8: Digest, watchlist và alert logic

Mục tiêu: Tạo giá trị sử dụng hằng ngày thay vì chỉ feed + chat.

| Hạng mục | Loại | Trạng thái |
| --- | --- | --- |
| Thêm `GET /api/v1/digest/today` | Backend | [ ] |
| Tạo job sinh daily digest | AI / Backend | [ ] |
| Chọn top signals theo importance + recency | AI / Backend | [ ] |
| Thiết kế watchlist theo `company / topic / event_type` | Product / Backend | [ ] |
| Thiết kế alert logic bản đầu | Product / Backend | [ ] |
| Tối ưu output digest cho app/web | App / Backend | [ ] |

Deliverable:
- Có Daily Brief bản đầu và watchlist logic cơ bản

## Tuần 9: User system và personalization

Mục tiêu: Bắt đầu tạo retention bằng trải nghiệm cá nhân hóa.

| Hạng mục | Loại | Trạng thái |
| --- | --- | --- |
| Thêm auth bằng JWT | Backend | [ ] |
| Thêm profile người dùng | Backend | [ ] |
| Thêm bookmarks | Backend | [ ] |
| Thêm preferences | Backend | [ ] |
| Thêm reading / interaction history | Backend | [ ] |
| Personalized feed theo `topic / company / event_type` | AI / Backend | [ ] |
| App hóa các màn hình bookmark / preference | App | [ ] |

Deliverable:
- User flow hoàn chỉnh bản đầu với bookmark và personalized feed

## Tuần 10: Productization, evaluation và demo

Mục tiêu: Chốt MVP hoàn chỉnh và đo được chất lượng hệ thống.

| Hạng mục | Loại | Trạng thái |
| --- | --- | --- |
| Theo dõi ingestion success rate | Vận hành | [ ] |
| Theo dõi enrichment success rate | Vận hành | [ ] |
| Theo dõi search/chat latency | Vận hành | [ ] |
| Theo dõi token usage và AI cost | Vận hành | [ ] |
| Tạo bộ test câu hỏi mẫu cho chat | AI Eval | [ ] |
| Đánh giá groundedness và hallucination | AI Eval | [ ] |
| Polish UX cho feed, detail, search, chat, digest | App | [ ] |
| Chuẩn bị staging/demo script | Product / Dev | [ ] |

Deliverable:
- MVP end-to-end hoàn chỉnh, có thể demo và đo được chất lượng

## KPI Cần Theo Dõi

| KPI | Mục đích | Trạng thái |
| --- | --- | --- |
| Số signal ingest mỗi ngày | Đo độ phủ dữ liệu | [ ] |
| Tỉ lệ parse thành công | Đo chất lượng ingestion | [ ] |
| Tỉ lệ dedup | Đo chất lượng normalize | [ ] |
| Thời gian từ ingest đến enrichment | Đo hiệu suất AI pipeline | [ ] |
| Latency API signals/search/chat | Đo trải nghiệm người dùng | [ ] |
| Cost AI theo ngày | Kiểm soát chi phí | [ ] |
| Tỉ lệ chat có source phù hợp | Đo chất lượng RAG | [ ] |
| Số lượt dùng digest | Đo giá trị sử dụng hằng ngày | [ ] |
| Số bookmark / watchlist | Đo mức độ quan tâm và retention | [ ] |

## Ưu Tiên MVP Nếu Cần Đi Nhanh

| Thứ tự | Hạng mục |
| --- | --- |
| 1 | Source policy + schema signal/event |
| 2 | Ingestion + normalize + dedup |
| 3 | Signal APIs |
| 4 | AI summary + event/topic extraction |
| 5 | Search + chat RAG |
| 6 | Daily digest |

## Ghi Chú

- [PRODUCT_PLAN.md](PRODUCT_PLAN.md) giữ vai trò định hướng chiến lược sản phẩm.
- [ARCHITECTURE.md](ARCHITECTURE.md) giữ vai trò thiết kế hệ thống tổng thể.
- [ROADMAP.md](ROADMAP.md) giữ vai trò backlog triển khai theo thứ tự build thực tế.