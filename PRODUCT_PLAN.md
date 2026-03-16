# Product Plan: Startup / Market Intelligence Assistant

Tài liệu này mô tả định hướng sản phẩm theo hướng Startup / Market Intelligence Assistant, tách riêng với roadmap kỹ thuật để dễ theo dõi.

## 1. Định vị sản phẩm

Sản phẩm không nên được định vị là một ứng dụng đọc tin tức tổng hợp.

Sản phẩm nên được định vị là:

> Trợ lý AI giúp theo dõi tín hiệu startup và thị trường, tóm tắt thông tin quan trọng, giải thích tác động và hỗ trợ hỏi đáp trên dữ liệu đã thu thập.

Giá trị cốt lõi không nằm ở việc hiển thị lại bài báo, mà nằm ở:
- phát hiện tín hiệu quan trọng
- tổng hợp thông tin từ nhiều nguồn
- tóm tắt ngắn gọn
- chuẩn hóa dữ liệu thành insight
- hỗ trợ search và chat theo ngữ cảnh

## 2. Người dùng mục tiêu

### Nhóm ưu tiên giai đoạn đầu

- Founder
- Product Manager
- Startup operator
- Growth lead
- Analyst theo dõi thị trường

### Pain points chính

- Quá nhiều nguồn thông tin, khó theo dõi hằng ngày
- Khó biết tin nào thật sự quan trọng
- Tốn thời gian đọc nhiều nguồn nhưng vẫn bỏ lỡ tín hiệu đáng chú ý
- Khó tổng hợp bức tranh chung của startup, đối thủ và thị trường

## 3. Bài toán sản phẩm cần giải quyết

Sản phẩm cần trả lời được các câu hỏi như:

- Hôm nay có startup nào vừa gọi vốn?
- Công ty nào vừa ra mắt tính năng mới?
- Đối thủ đang có động thái gì đáng chú ý?
- Tuần này thị trường AI / fintech / SaaS có gì nổi bật?
- Có tín hiệu nào quan trọng mà founder hoặc PM nên biết không?

## 4. Đề xuất giá trị cốt lõi

### Thay vì làm

- app đọc tin tức
- nơi copy nội dung bài báo
- news feed thông thường

### Nên làm

- AI market intelligence assistant
- signal feed thay vì article feed
- công cụ theo dõi startup, sản phẩm, funding, competitor moves
- trợ lý tóm tắt, search, chat và digest trên dữ liệu thị trường

## 5. Phạm vi dữ liệu nên dùng ở giai đoạn đầu

### Nguồn ưu tiên

- company blog
- official newsroom
- press release
- Product Hunt
- GitHub releases
- changelog
- docs update pages
- RSS chính thức
- public startup announcement pages
- accelerator / incubator announcement pages

### Nguồn nên hạn chế hoặc tránh ở giai đoạn đầu

- báo paywall
- nguồn yêu cầu đăng nhập
- nền tảng có ToS chặt với scraping
- mạng xã hội khó kiểm soát quyền sử dụng
- nguồn dễ phát sinh tranh chấp bản quyền

## 6. Nguyên tắc dữ liệu và bản quyền

Để giảm rủi ro pháp lý và bản quyền, sản phẩm nên tuân thủ các nguyên tắc sau:

1. Không lưu full article nếu không có quyền rõ ràng.
2. Không hiển thị lại toàn bộ bài viết gốc từ publisher.
3. Chỉ lưu metadata + excerpt ngắn + AI summary + source link.
4. Luôn gắn attribution và đường dẫn về nguồn.
5. Không dùng ảnh nếu chưa rõ quyền sử dụng.
6. Ưu tiên dùng nguồn public chính thức hoặc RSS/API chính thức.
7. Không bypass paywall, login hoặc anti-bot.

## 7. Mô hình dữ liệu sản phẩm

Sản phẩm nên đi theo hướng `signal/event`, không nên đi theo hướng `article mirror`.

### Một signal nên có

- source_name
- source_url
- title
- published_at
- raw_excerpt
- company_name
- event_type
- topic
- tags
- ai_summary
- why_it_matters
- confidence_score

### Event types nên chuẩn hóa sớm

- funding
- product_launch
- hiring
- partnership
- acquisition
- market_move
- regulation
- competitor_update

## 8. Tính năng sản phẩm nên làm

### Core features cho MVP

1. Signal feed
2. Signal detail
3. AI summary
4. Topic / event type / company extraction
5. Search
6. Trending / notable signals
7. Chat hỏi đáp trên kho dữ liệu
8. Daily digest

### Tính năng giai đoạn sau

1. Bookmark
2. Watchlist theo company / topic
3. Personalized feed
4. Alert theo event type
5. Team sharing / report export

## 9. Trải nghiệm người dùng mong muốn

Người dùng mở app và ngay lập tức thấy:

- tín hiệu nào quan trọng hôm nay
- công ty nào vừa có động thái mới
- điều đó ảnh hưởng gì đến họ
- có thể search hoặc hỏi AI ngay

Mỗi signal card nên có:

- tiêu đề
- company
- event type
- topic
- AI summary
- why it matters
- source link

## 10. Luồng sản phẩm đề xuất

### Luồng backend / data

1. Thu thập dữ liệu từ nguồn public phù hợp
2. Parse và chuẩn hóa dữ liệu
3. Deduplicate
4. Trích xuất signal / event / company / topic
5. Sinh AI summary
6. Lưu vào database
7. Expose qua API
8. Hỗ trợ search, chat, digest

### Luồng người dùng

1. Mở feed
2. Đọc summary nhanh
3. Xem signal detail
4. Search theo công ty / chủ đề / sự kiện
5. Hỏi AI
6. Theo dõi digest hoặc alert hằng ngày

## 11. Kế hoạch từng bước để triển khai

### Bước 1: Chốt bài toán sản phẩm

Output cần có:
- 1 user persona chính
- 3 pain points chính
- 1 câu định vị sản phẩm
- 5 câu hỏi mẫu người dùng hay hỏi

### Bước 2: Chốt danh sách nguồn dữ liệu an toàn

Output cần có:
- danh sách 20-30 nguồn
- phân loại nguồn theo mức độ rủi ro
- nguyên tắc ingest dữ liệu

### Bước 3: Thiết kế schema kiểu signal/event

Output cần có:
- thiết kế bảng dữ liệu chính
- chuẩn event types
- field cho AI enrichment

### Bước 4: Xây ingestion pipeline

Output cần có:
- crawler/puller nhiều nguồn
- normalize dữ liệu
- dedup
- logging + retry

### Bước 5: Xây backend API

Output cần có:
- list signals
- signal detail
- categories/topics
- search
- trending

### Bước 6: Thêm AI enrichment

Output cần có:
- summary_one_line
- summary_bullets
- why_it_matters
- topic / event type / company extraction

### Bước 7: Dựng UI MVP

Output cần có:
- feed
- detail
- search
- company page
- daily digest

### Bước 8: Thêm search thông minh và chat RAG

Output cần có:
- keyword search
- semantic retrieval
- chat có grounding và source reference

### Bước 9: Thêm digest và alert

Output cần có:
- daily digest
- watchlist
- alert theo topic / company / event type

### Bước 10: Đo lường và tối ưu

Output cần có:
- đo latency
- đo AI cost
- đo chất lượng AI output
- tối ưu prompt / retrieval / UX

## 12. KPI nên đo

- số signal ingest mỗi ngày
- tỉ lệ parse thành công
- thời gian từ ingest đến khi có AI summary
- latency API
- latency chat
- cost AI theo ngày
- số lượt search
- số lượt chat
- số người dùng xem digest
- số click sang source gốc

## 13. MVP đề xuất

MVP đầu tiên nên bao gồm:

1. 5-10 nguồn dữ liệu an toàn
2. signal feed
3. AI summary
4. event type + topic + company extraction
5. search
6. chat RAG
7. daily digest

Không nên cố làm ngay từ đầu:

- social crawling phức tạp
- enterprise workflow lớn
- recommendation nặng ML
- full user system quá sâu
- đa nền tảng quá sớm

## 14. Kết luận định hướng

Hướng Startup / Market Intelligence là khả thi nếu được xây như một lớp intelligence trên dữ liệu công khai, thay vì như một công cụ sao chép tin tức.

Điểm mạnh của hướng này:
- giá trị sản phẩm rõ hơn news app thông thường
- phù hợp để học AI systems
- dễ phát triển thành search, chat, digest, alert
- phù hợp với mục tiêu trở thành AI Solution Engineer

Điểm cần kỷ luật ngay từ đầu:
- kiểm soát nguồn dữ liệu
- kiểm soát rủi ro bản quyền
- tập trung vào metadata, summary và insight
- không đi theo hướng republish full content