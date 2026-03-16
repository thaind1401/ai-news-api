# AI Learning Apply Plan (Stage 2 -> Stage 6)

Last updated: 2026-03-16

Mục tiêu: học đúng thứ tự để apply trực tiếp vào AI Signals API, tránh học lan man.

---

## 1) Tổng quan lộ trình

| Stage | Năng lực chính | Áp dụng vào app này | Kết quả đầu ra |
| --- | --- | --- | --- |
| 2 | LLM Fundamentals + Prompt Engineering | Nâng AI enrichment từ rule-based -> LLM structured output | Enrichment chất lượng cao, ổn định format |
| 3 | RAG Systems + Vector Database | Embeddings + retrieval + hybrid search | Search thông minh, chuẩn bị context cho chat |
| 4 | AI Agents + Tool Use | Agent orchestration gọi tools nội bộ | Chat/assistant biết dùng data + tool thay vì trả lời chung |
| 5 | AI System Architecture | Thiết kế runtime AI production-like | Kiến trúc rõ trách nhiệm, scale và vận hành tốt |
| 6 | Deployment + Automation + Integration | CI/CD, jobs, monitoring, automation | Pipeline chạy bền, có đo lường và cảnh báo |

---

## 2) Stage 2 — LLM Fundamentals + Prompt Engineering

### Learn
- Prompt patterns: system/user/context separation.
- Structured output (JSON schema), validation, retry strategy.
- Hallucination guardrails và fallback khi model lỗi.

### Apply vào repo
- Thay enrichment baseline ở [app/services/ingestion_service.py](app/services/ingestion_service.py) bằng pipeline LLM có schema.
- Tách prompt templates trong [app/ai/prompts/](app/ai/prompts/).
- Tạo enricher implementation trong [app/ai/enrichers/](app/ai/enrichers/).

### Deliverables
- `summary_one_line`, `summary_bullets`, `why_it_matters` từ LLM.
- Validate JSON output trước khi ghi DB.
- Có fallback sang baseline khi LLM fail.

### Done criteria
- >= 95% record mới có `enrichment_status=done`.
- Tỉ lệ lỗi schema < 2%.
- Có log `model_name`, `prompt_version`, `error_message`.

### Checklist Stage 2

- [ ] Hiểu rõ token/context window và ảnh hưởng lên cost + quality.
- [ ] Viết prompt theo cấu trúc `role + objective + constraints + output format`.
- [ ] Có bộ few-shot examples cho enrichment output.
- [ ] Định nghĩa JSON schema cho output enrichment.
- [ ] Có validate output (schema/type/required fields).
- [ ] Có retry policy khi output sai format.
- [ ] Có fallback (rule-based hoặc queue retry) khi model fail.
- [ ] Log đầy đủ `model_name`, `prompt_version`, `error_message`, `latency`.
- [ ] Có test dataset nhỏ để chấm quality enrichment.
- [ ] Có tiêu chí pass/fail rõ ràng trước khi bật rộng.

---

## 3) Stage 3 — RAG Systems + Vector Database

### Learn
- Embedding fundamentals, chunking strategy, top-k retrieval.
- Vector index basics (`pgvector` hoặc tương đương).
- Hybrid retrieval: keyword + semantic + rerank.

### Apply vào repo
- Dùng bảng `signal_embeddings` trong [app/database/models.py](app/database/models.py).
- Tạo indexing jobs trong [app/ai/embeddings/](app/ai/embeddings/).
- Implement retrieval service trong [app/ai/retrieval/](app/ai/retrieval/).
- Nâng Search API ở [app/api/routers/search.py](app/api/routers/search.py) từ placeholder -> thật.

### Deliverables
- Pipeline tạo embedding cho signal mới + backfill cũ.
- `GET /api/v1/search` trả kết quả hybrid có score.

### Done criteria
- Query mơ hồ vẫn ra kết quả đúng ngữ cảnh.
- Latency search p95 trong ngưỡng chấp nhận.
- Có debug metadata (`keyword_score`, `semantic_score`, `rerank_score`).

### Checklist Stage 3

- [ ] Chuẩn hóa `embedding_text` cho signal (title + summary + metadata).
- [ ] Chọn embedding model và ghi version rõ ràng.
- [ ] Tạo job sinh embedding cho signal mới.
- [ ] Có cơ chế backfill embeddings cho dữ liệu cũ.
- [ ] Thiết kế index/vector store phù hợp (ưu tiên `pgvector`).
- [ ] Implement semantic retrieval top-k.
- [ ] Implement hybrid search (keyword + semantic).
- [ ] Implement rerank lớp cuối.
- [ ] Trả debug scores trong search response.
- [ ] Đo latency/search quality và tune top-k.

---

## 4) Stage 4 — AI Agents + Tool Use

### Learn
- Agent loop: plan -> act -> observe -> refine.
- Tool calling patterns và safety boundaries.
- Multi-tool orchestration (search/reingest/re-enrich/inspect).

### Apply vào repo
- Xây agent service trong [app/ai/chat/](app/ai/chat/).
- Dùng tools nội bộ qua APIs:
  - [app/api/routers/search.py](app/api/routers/search.py)
  - [app/api/routers/internal_jobs.py](app/api/routers/internal_jobs.py)
- Nâng chat endpoint ở [app/api/routers/chat.py](app/api/routers/chat.py) từ echo -> grounded assistant.

### Deliverables
- Chat có thể truy xuất signal liên quan trước khi trả lời.
- Chat response kèm nguồn tham chiếu.

### Done criteria
- Câu trả lời luôn có source hoặc nói rõ thiếu context.
- Không còn trả lời kiểu chung chung khi có data nội bộ.

### Checklist Stage 4

- [ ] Xác định danh sách tools agent được phép gọi.
- [ ] Thiết kế policy an toàn cho từng tool (input/output guardrails).
- [ ] Implement loop `plan -> act -> observe -> refine`.
- [ ] Agent bắt buộc retrieval trước khi generate answer.
- [ ] Chat response luôn có sources/citations.
- [ ] Có fallback khi tool lỗi hoặc không có context.
- [ ] Log toàn bộ tool calls để debug.
- [ ] Giới hạn vòng lặp agent để tránh runaway.
- [ ] Có test cases cho tool misuse/prompt injection.
- [ ] Có tiêu chí quality cho grounded answers.

---

## 5) Stage 5 — AI System Architecture

### Learn
- Service boundaries: ingestion, enrichment, retrieval, API.
- Async jobs, retry queues, dead-letter strategy.
- Observability: logs, metrics, traces cho AI pipeline.

### Apply vào repo
- Chốt kiến trúc giữa:
  - ingestion workers: [app/ingestion/workers/](app/ingestion/workers/)
  - enrichment services: [app/services/ingestion_service.py](app/services/ingestion_service.py)
  - retrieval/chat modules: [app/ai/](app/ai/)
- Xác định rõ ownership mỗi lớp trong [ARCHITECTURE.md](ARCHITECTURE.md).

### Deliverables
- Architecture diagram + runbook vận hành ngắn.
- SLA/SLO cơ bản cho ingestion/enrichment/search/chat.

### Done criteria
- Mỗi luồng có retry/fallback rõ.
- Dễ mở rộng không phải refactor lớn cấu trúc thư mục.

### Checklist Stage 5

- [ ] Chốt boundary giữa ingestion/enrichment/retrieval/api.
- [ ] Chốt contract dữ liệu giữa các lớp.
- [ ] Có retry + dead-letter strategy cho jobs quan trọng.
- [ ] Có SLO/SLA cơ bản cho ingestion/search/chat.
- [ ] Có logging conventions thống nhất toàn hệ thống.
- [ ] Có metrics chuẩn (success rate, latency, error rate).
- [ ] Có runbook xử lý sự cố phổ biến.
- [ ] Có sơ đồ kiến trúc cập nhật trong docs.
- [ ] Có capacity plan cơ bản cho scale gần.
- [ ] Có review kiến trúc định kỳ.

---

## 6) Stage 6 — Deployment + Automation + Integration

### Learn
- CI/CD cho backend AI workloads.
- Job scheduling + automation + secret management.
- Monitoring cost/latency/error budget.

### Apply vào repo
- Chuẩn hóa deploy + config env từ [README.md](README.md).
- Tự động hóa job kiểm tra health/smoke/reingest/re-enrich.
- Bổ sung monitoring hooks cho enrichment/search/chat.

### Deliverables
- Pipeline deploy ổn định (dev/staging).
- Dashboard theo dõi health + cost + quality.

### Done criteria
- Có cảnh báo khi ingestion fail hoặc error rate tăng.
- Có số liệu usage/cost theo ngày.
- Có playbook xử lý incident cơ bản.

### Checklist Stage 6

- [ ] Chuẩn hóa `.env` và secrets management theo môi trường.
- [ ] Tạo pipeline CI cho test/lint/build cơ bản.
- [ ] Tạo pipeline CD cho deploy dev/staging.
- [ ] Tự động hóa scheduler/jobs và health checks.
- [ ] Có smoke tests sau deploy.
- [ ] Có alerting cho API down/job failures/high error rates.
- [ ] Có dashboard cost/latency/quality metrics.
- [ ] Có rollback procedure rõ ràng.
- [ ] Có backup/restore plan cho database.
- [ ] Có checklist release trước khi production.

---

## 7) Sequence thực thi đề xuất (bám repo hiện tại)

| Priority | Work item | Stage |
| --- | --- | --- |
| P1 | Implement Search API thật (keyword + filter) | 3 |
| P2 | Nâng enrichment sang LLM structured output + retry | 2 |
| P3 | Embeddings + retrieval + hybrid search | 3 |
| P4 | Chat grounded + source citations + tool use | 4 |
| P5 | Digest API tối thiểu + automation jobs | 6 |

---

## 8) Weekly check-in template

| Week | Focus | Done | Blocked | Next |
| --- | --- | --- | --- | --- |
| W1 | Stage 2 |  |  |  |
| W2 | Stage 2 -> 3 |  |  |  |
| W3 | Stage 3 |  |  |  |
| W4 | Stage 4 |  |  |  |
| W5 | Stage 5 |  |  |  |
| W6 | Stage 6 |  |  |  |

---

## 9) Rule học để apply hiệu quả

- Không học tách rời: học xong 1 concept phải map ngay vào 1 file/module thật trong repo.
- Mỗi stage phải có demo chạy được, không chỉ ghi chú lý thuyết.
- Ưu tiên “ship nhỏ nhưng hoàn chỉnh” theo thứ tự P1 -> P5.
