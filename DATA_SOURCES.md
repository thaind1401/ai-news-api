# Data Sources: Startup / Market Intelligence Assistant

Tài liệu này dùng để chốt danh sách nguồn dữ liệu cho sản phẩm Startup / Market Intelligence Assistant.

Mục tiêu của tài liệu:
- xác định nguồn nào có thể dùng ngay cho MVP
- xác định nguồn nào cần review thêm trước khi bật
- xác định nguồn nào nên tránh trong giai đoạn đầu
- giảm rủi ro về bản quyền, Terms of Service và độ ổn định dữ liệu

Lưu ý: đây là tài liệu định hướng sản phẩm và kỹ thuật, không thay thế tư vấn pháp lý. Khi mở rộng quy mô hoặc thương mại hóa, vẫn nên review lại Terms of Service và chính sách dữ liệu của từng nguồn.

## 1. Nguyên tắc chọn nguồn dữ liệu

### 1.1. Nguyên tắc ưu tiên

Ưu tiên nguồn có đặc điểm sau:
- public, không cần đăng nhập
- là nguồn chính thức của công ty hoặc tổ chức
- có RSS hoặc API chính thức
- nội dung có cấu trúc rõ ràng, dễ parse
- có giá trị tạo ra signal về startup, sản phẩm, funding, thị trường

### 1.2. Thứ tự ưu tiên về cách ingest

1. API chính thức
2. RSS chính thức
3. Trang public HTML đơn giản, không có anti-bot phức tạp

### 1.3. Nguyên tắc lưu trữ dữ liệu

Với hầu hết nguồn dữ liệu, hệ thống chỉ nên lưu:
- source name
- source URL
- title
- published_at
- excerpt ngắn
- metadata chuẩn hóa
- AI summary
- tags / topic / event type / company

Không nên mặc định lưu:
- full article text nếu không có quyền rõ ràng
- ảnh gốc của publisher nếu chưa rõ quyền sử dụng
- dữ liệu yêu cầu login hoặc có paywall

## 2. Mức độ rủi ro nguồn dữ liệu

### Mức A: An toàn để bật ngay

Đặc điểm:
- nguồn chính thức
- public
- không cần login
- không có paywall
- có RSS/API hoặc HTML rõ ràng

### Mức B: Có thể dùng nhưng phải review trước

Đặc điểm:
- nguồn public nhưng Terms of Service cần đọc kỹ
- dữ liệu có giá trị nhưng có thể nhạy cảm về crawling/reuse
- có thể dùng nếu chỉ lấy metadata hoặc có cơ chế hạn chế rõ ràng

### Mức C: Tránh trong giai đoạn đầu

Đặc điểm:
- paywall
- yêu cầu login
- anti-bot mạnh
- rủi ro cao về bản quyền hoặc ToS
- dữ liệu cá nhân hoặc social data khó kiểm soát

## 3. Danh sách nguồn nên bật ngay cho MVP

Các nguồn dưới đây phù hợp để tạo market/product/company signals ở giai đoạn đầu.

| STT | Nguồn | Loại | Cách ingest ưu tiên | Giá trị chính | Mức rủi ro | Trạng thái |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Official company blogs | Company source | RSS / HTML | Product update, launch, hiring, positioning | A | Bật |
| 2 | Official company newsroom | Company source | RSS / HTML | Press release, partnership, funding announcement | A | Bật |
| 3 | Official changelog pages | Product source | HTML / RSS | Product releases, feature launches | A | Bật |
| 4 | Official GitHub Releases | Developer source | GitHub API / RSS / HTML | Release signals, product shipping cadence | A | Bật |
| 5 | Product Hunt public launches | Product discovery | HTML / RSS nếu có | Product launch, startup launch signals | A | Bật |
| 6 | OpenAI Blog / News | Official AI source | RSS / HTML | Model launch, API update, pricing, roadmap signal | A | Bật |
| 7 | Anthropic News | Official AI source | HTML / RSS | Model updates, partnership, enterprise signal | A | Bật |
| 8 | Google AI Blog | Official AI source | RSS / HTML | AI research-to-product signals | A | Bật |
| 9 | Hugging Face Blog | Official AI source | RSS / HTML | Open-source AI ecosystem signals | A | Bật |
| 10 | AWS What's New | Official product source | RSS / HTML | Cloud product updates, enterprise market signal | A | Bật |
| 11 | Cloudflare Blog / Changelog | Official product source | RSS / HTML | Infrastructure and market signals | A | Bật |
| 12 | Stripe Blog / Newsroom | Official company source | RSS / HTML | Fintech and product movement signals | A | Bật |
| 13 | Vercel Changelog / Blog | Official company source | RSS / HTML | Devtool and product launch signals | A | Bật |
| 14 | Supabase Blog / Changelog | Official company source | RSS / HTML | Startup + product evolution signals | A | Bật |
| 15 | Linear Changelog | Official product source | HTML | Product shipping signals | A | Bật |
| 16 | Notion What's New | Official product source | HTML | Product launch and positioning signals | A | Bật |
| 17 | Figma Blog / Releases | Official company source | HTML / RSS | Design/product market signal | A | Bật |
| 18 | Y Combinator Blog / Announcements | Ecosystem source | HTML / RSS | Startup ecosystem signals | A | Bật |
| 19 | Techstars News / Blog | Ecosystem source | HTML / RSS | Accelerator ecosystem signals | A | Bật |
| 20 | 500 Global Blog / Announcements | Ecosystem source | HTML / RSS | Startup and funding ecosystem signals | A | Bật |
| 21 | Official startup announcement pages | Company source | HTML / RSS | Funding, hiring, launch, partnership | A | Bật |
| 22 | Official docs update pages | Documentation source | HTML / RSS | API/product changes with high signal value | A | Bật |

## 4. Nguồn có thể dùng nhưng cần review trước khi bật

Các nguồn này có thể rất giá trị, nhưng không nên ingest hàng loạt ngay khi chưa review kỹ.

| STT | Nguồn | Vì sao giá trị | Rủi ro / lưu ý | Mức rủi ro | Trạng thái |
| --- | --- | --- | --- | --- | --- |
| 1 | Crunchbase public pages | Funding, startup profile, company events | Terms of Service cần review kỹ; không nên scrape bừa | B | Review trước |
| 2 | Tech in Asia | Tin startup châu Á có giá trị | Cần đọc kỹ điều khoản sử dụng và cách reuse nội dung | B | Review trước |
| 3 | TechCrunch | Nhiều signal startup/funding | Rủi ro bản quyền nếu republish nội dung | B | Review trước |
| 4 | VentureBeat | Tốt cho AI/startup/product | Cần giới hạn dùng ở metadata + source link | B | Review trước |
| 5 | Hacker News | Tốt cho discovery và tín hiệu cộng đồng | Dữ liệu công khai nhưng cần kiểm soát reuse và chất lượng tín hiệu | B | Review trước |
| 6 | Reddit communities | Có tín hiệu sớm từ cộng đồng | Chất lượng nhiễu cao, ToS và moderation phức tạp | B | Review trước |
| 7 | App Store release notes | Tốt cho product intelligence | Cần review cách thu thập hợp lệ và mức reuse dữ liệu | B | Review trước |
| 8 | Google Play release notes | Tốt cho tracking product updates | Cần review nguồn và chính sách lấy dữ liệu | B | Review trước |
| 9 | Public investor blogs | Có market insights tốt | Phải phân biệt insight blog với nội dung cần license | B | Review trước |
| 10 | Startup database public profile pages | Hữu ích cho company mapping | Dễ vướng ToS nếu crawl khối lượng lớn | B | Review trước |

Nguyên tắc nếu dùng nhóm này:
- chỉ lưu metadata hoặc excerpt ngắn
- luôn dẫn link gốc
- không republish full content
- đọc ToS trước khi bật ingestion thường xuyên

## 5. Nguồn nên tránh trong giai đoạn đầu

| STT | Nguồn | Lý do tránh | Mức rủi ro |
| --- | --- | --- | --- |
| 1 | Website có paywall | Rủi ro cao về bản quyền và ToS | C |
| 2 | Nguồn yêu cầu login | Rủi ro cao, khó vận hành hợp lệ | C |
| 3 | LinkedIn scraping | ToS nhạy cảm, dữ liệu khó kiểm soát | C |
| 4 | X / Twitter scraping trái điều khoản | ToS và ổn định dữ liệu không phù hợp giai đoạn đầu | C |
| 5 | Newsletter private email content | Không phù hợp để ingest tự động nếu chưa rõ quyền | C |
| 6 | Nội dung social cá nhân | Có yếu tố dữ liệu cá nhân và quyền riêng tư | C |
| 7 | Ảnh và media của publisher | Rủi ro cao nếu reuse mà không có quyền | C |
| 8 | Nguồn anti-bot mạnh | Chi phí vận hành cao, dễ vi phạm ToS | C |

## 6. Quy tắc sử dụng nội dung từ nguồn dữ liệu

### 6.1. Được phép lưu trong DB

- title
- source URL
- published_at
- source name
- excerpt ngắn
- signal metadata
- AI-generated summary
- topic / event type / company / tags

### 6.2. Không nên mặc định lưu hoặc hiển thị

- full article từ publisher
- hình ảnh gốc từ báo hoặc blog nếu chưa rõ quyền
- nội dung đã qua paywall
- nội dung cần đăng nhập

### 6.3. Quy tắc hiển thị trên app/web

Trên UI, mỗi signal nên hiển thị:
- title
- company
- event type
- topic
- AI summary
- why it matters
- source link

Không nên hiển thị:
- bản sao gần như nguyên văn bài gốc
- full article thay cho nguồn gốc

## 7. Source onboarding checklist

Mỗi nguồn mới phải đi qua checklist sau trước khi bật vào hệ thống:

| Hạng mục kiểm tra | Kết quả |
| --- | --- |
| Nguồn có public không? | [ ] |
| Có yêu cầu login không? | [ ] |
| Có paywall không? | [ ] |
| Có RSS hoặc API chính thức không? | [ ] |
| Robots.txt có dấu hiệu cấm crawl không? | [ ] |
| Terms of Service đã được review chưa? | [ ] |
| Có thể chỉ lưu metadata + excerpt ngắn + AI summary không? | [ ] |
| Có cần ảnh/media từ nguồn không? | [ ] |
| Giá trị signal có đủ cao để ingest định kỳ không? | [ ] |
| Đã gắn risk level và owner nội bộ chưa? | [ ] |

## 8. Source registry template

Mỗi nguồn nên được quản lý trong source registry nội bộ với cấu trúc như sau:

| Field | Ý nghĩa |
| --- | --- |
| source_name | Tên nguồn |
| source_type | company_blog / newsroom / changelog / ecosystem / aggregator |
| base_url | URL gốc |
| ingest_method | api / rss / html |
| risk_level | A / B / C |
| terms_reviewed | yes / no |
| robots_reviewed | yes / no |
| auth_required | yes / no |
| paywall | yes / no |
| store_full_text | yes / no |
| status | active / paused / blocked |
| owner | người phụ trách review |

### Mapping ingest method -> worker handler (đang áp dụng)

| ingest/discovery type | Worker handler | Ghi chú |
| --- | --- | --- |
| `rss` | `app/ingestion/workers/rss_worker.py` | Ưu tiên cho nguồn chính thức có feed |
| `homepage_css` | `app/ingestion/workers/homepage_worker.py` | Dùng khi chưa có RSS/API |
| discovery router | `app/ingestion/workers/source_discovery.py` | Route theo `discovery.type` trong source config |
| per-source orchestration | `app/ingestion/workers/source_worker.py` | Thực thi fetch + parse + ingest + fetch-run log |

## 9. Danh sách nguồn ưu tiên khởi động MVP

Nếu phải bắt đầu ngay với phạm vi nhỏ, nên bật theo thứ tự này:

1. Official company blogs của các công ty mục tiêu
2. Official newsroom
3. Official changelog pages
4. GitHub Releases của các sản phẩm / startup cần theo dõi
5. Product Hunt launches
6. OpenAI / Anthropic / Google AI / Hugging Face blogs
7. Vercel / Stripe / Supabase / Linear / Notion / Figma updates
8. YC / Techstars / 500 Global announcements

## 10. Kết luận

Danh sách nguồn dữ liệu an toàn cho giai đoạn MVP nên dựa trên nguyên tắc:
- official source trước
- metadata và signal trước full article
- RSS/API trước HTML crawl
- risk level rõ ràng trước khi bật ingestion

Nếu làm đúng theo tài liệu này, sản phẩm sẽ:
- giảm rủi ro về bản quyền và ToS
- có dữ liệu đủ tốt để xây signal feed, search, chat và digest
- dễ mở rộng theo hướng market intelligence thay vì news aggregation