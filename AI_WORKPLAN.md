# AI Workplan theo giai đoạn

Tài liệu này tách riêng các công việc AI cần làm cho sản phẩm Startup / Market Intelligence Assistant, bám theo PRODUCT_PLAN, ARCHITECTURE, ROADMAP và DATA_SOURCES.

## 1) Mục tiêu của AI trong hệ thống

AI không phải để copy tin, mà để tạo lớp intelligence trên dữ liệu signals:
- Tóm tắt nhanh thông tin quan trọng.
- Trích xuất thực thể/cấu trúc phục vụ search và filter.
- Trả lời câu hỏi có grounding và nguồn tham chiếu.
- Tạo digest/alert/personalization.

## 2) Nguyên tắc bắt buộc

- Chỉ dùng dữ liệu hợp lệ theo policy nguồn (metadata + excerpt + source link).
- Không republish full article.
- Không bypass paywall/login/anti-bot.
- Mọi output AI quan trọng phải audit được bằng model_name + prompt_version + timestamp.
- Chat/search phải grounded trên dữ liệu đã ingest.

## 3) Công việc AI theo giai đoạn

## Giai đoạn A — Enrichment nền (đang có baseline)

Mục tiêu:
- Mỗi signal có lớp mô tả AI cơ bản.

Công việc AI:
1. Sinh summary_one_line.
2. Sinh summary_bullets.
3. Sinh why_it_matters.
4. Gắn topic/event_type/tags/importance_score/confidence_score.
5. Lưu model_name + prompt_version.

Input:
- title, sub_title, description, category, source_url, published_at.

Output:
- signal_ai_enrichments cho mỗi signal.

Trạng thái hiện tại:
- Đã có baseline rule-based.

Cần nâng cấp tiếp:
- Chuyển từ rule-based sang LLM-based async jobs.

## Giai đoạn B — Enrichment v1 bằng LLM (ưu tiên cao)

Mục tiêu:
- Chất lượng summary và extraction tốt hơn, ổn định hơn.

Công việc AI:
1. Thiết kế prompt template cho từng source type.
2. Yêu cầu model trả structured JSON (schema cố định).
3. Validate JSON output (reject/retry nếu sai schema).
4. Chuẩn hóa confidence_score và importance_score.
5. Fallback khi model lỗi (giữ baseline hoặc queue retry).

Input:
- raw payload đã normalize + metadata source.

Output:
- enrichment_status (done/failed), error_message, retries.

Done khi:
- >= 95% bản ghi mới có enrichment_status=done.
- Tỉ lệ lỗi format JSON < 2%.

## Giai đoạn C — Retrieval/Search AI (ưu tiên cao)

Mục tiêu:
- Tìm kiếm thông minh vượt keyword search.

Công việc AI:
1. Tạo embedding_text cho signal.
2. Sinh embeddings và lưu vector index.
3. Thêm semantic retrieval.
4. Kết hợp keyword + semantic retrieval.
5. Rerank kết quả theo relevance + recency + importance.

Input:
- signals + signal_ai_enrichments.

Output:
- Danh sách signal liên quan có score.

Done khi:
- Search query mơ hồ vẫn trả đúng ngữ cảnh.
- Latency p95 trong ngưỡng mục tiêu.

## Giai đoạn D — Chat RAG (ưu tiên cao)

Mục tiêu:
- Trợ lý hỏi đáp grounded trên signals.

Công việc AI:
1. Query understanding (intent + scope).
2. Retrieval top-k signals.
3. Build context ngắn gọn có nguồn.
4. Generate answer có citation/source reference.
5. Guardrail chống hallucination (không đủ context thì nói rõ).
6. Fallback: “không đủ dữ liệu” thay vì bịa.

Input:
- user question + retrieval context.

Output:
- answer + sources + meta.

Done khi:
- Tỉ lệ câu trả lời có nguồn phù hợp >= mục tiêu.
- Giảm hallucination rõ rệt qua bộ test chuẩn.

## Giai đoạn E — Digest / Alert / Personalization

Mục tiêu:
- Tăng giá trị dùng hằng ngày và retention.

Công việc AI:
1. Chọn top signals theo importance + recency + preference.
2. Sinh daily digest theo user/team.
3. Tạo alert theo watchlist (company/topic/event_type).
4. Cá nhân hóa feed theo lịch sử tương tác.

Input:
- signals, enrichments, user_preferences, watchlists.

Output:
- digest content, alert events, personalized ranking.

Done khi:
- Digest có tỷ lệ mở/click đạt mục tiêu.
- Alert đúng ngữ cảnh và ít nhiễu.

## Giai đoạn F — AI Eval & Cost Control

Mục tiêu:
- Vận hành AI bền vững (chất lượng + chi phí).

Công việc AI:
1. Lập bộ benchmark câu hỏi thật cho search/chat.
2. Đo groundedness, relevance, factuality, coverage.
3. Theo dõi token usage và cost theo ngày.
4. Theo dõi latency theo pipeline step.
5. A/B test prompt/version/model.

Output:
- Dashboard chất lượng AI + chi phí + latency.

Done khi:
- Có vòng lặp cải tiến định kỳ theo metric.

## 4) Mapping nhanh với roadmap hiện tại

- Tuần 5: Giai đoạn A/B (AI enrichment).
- Tuần 6: Giai đoạn C (retrieval/search).
- Tuần 7: Giai đoạn D (chat RAG).
- Tuần 8: Giai đoạn E (digest/alert).
- Tuần 10: Giai đoạn F (AI eval/cost).

## 5) Việc AI không làm

- Không ingest nguồn trái policy ở DATA_SOURCES.
- Không xuất full article thay cho source gốc.
- Không trả lời “khẳng định chắc chắn” khi thiếu context dữ liệu.

## 6) Checklist sprint gần nhất (đề xuất)

Sprint 1:
- Chuẩn hóa prompt + JSON schema cho enrichment.
- Tạo worker async enrichment + retry queue.
- Log model_name/prompt_version/error_message đầy đủ.

Sprint 2:
- Tạo embeddings + semantic retrieval + rerank cơ bản.
- Thêm API search có hybrid mode.

Sprint 3:
- Chat RAG v1 có source citations + fallback.
- Bộ test chat groundedness bản đầu.

## 7) Kanban vận hành hằng ngày (Now / Next / Later)

### Now (làm ngay)

- Hoàn thiện enrichment async worker (queue + retry + dead-letter).
- Khóa JSON schema output cho summary/topic/event_type/tags.
- Thêm bộ kiểm tra chất lượng enrichment tự động (format + null-rate).
- Bật logging đầy đủ model_name, prompt_version, token usage, latency.

### Next (làm kế tiếp)

- Tạo pipeline embeddings cho signal mới và backfill dữ liệu cũ.
- Triển khai hybrid search (keyword + semantic) và rerank cơ bản.
- Thiết kế API search có debug metadata (retrieval_score, rerank_score).
- Dựng Chat RAG v1 có source citations + fallback khi context yếu.

### Later (làm sau)

- Tạo digest cá nhân hóa theo user preferences + watchlist.
- Tạo alert theo event_type/topic/company với ngưỡng chống nhiễu.
- Dựng dashboard AI eval (groundedness, relevance, hallucination).
- Tối ưu cost bằng prompt routing, model tiering, caching.

## 8) Định nghĩa trạng thái Kanban

- Todo: chưa bắt đầu.
- In Progress: đang làm, có owner rõ ràng.
- Review: đã xong kỹ thuật, chờ review chất lượng.
- Done: đạt tiêu chí done và đã theo dõi ổn định trên production-like data.
