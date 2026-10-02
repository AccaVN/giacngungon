# Website Giấc Ngủ Ngon – giacngungon.org

Website tĩnh (HTML/CSS/JS thuần), lấy cảm hứng bố cục từ SleepFoundation.org.
Không cần PHP, không cần database, không cần WordPress → nhanh, an toàn, host miễn phí.

## Cấu trúc gói

```
content/*.md     ← 45 bài viết (Markdown) – sửa/thêm bài ở đây
content/images/  ← ảnh bài viết (tên file khai báo ở dòng `image:` của bài)
static/          ← CSS, JS, logo, ảnh chia sẻ
build.py         ← script sinh ra thư mục dist/ (website hoàn chỉnh) từ content/ + static/
requirements.txt ← thư viện Python cần cho build
```

Trang có sẵn: Trang chủ · 45 bài viết · 6 chuyên mục · Bài viết (lọc + tìm) · Máy tính giờ ngủ ·
Bài kiểm tra giấc ngủ · Bác sĩ · Liên hệ/đặt lịch · Chính sách biên tập · 404 · sitemap.xml · robots.txt.
Giữ nguyên đường dẫn 9 bài cũ (vd `/dau-hieu-mat-ngu/`, `/chung-ngu-ru/`, `/blog/`, `/lien-he/`) để không mất thứ hạng Google.

## TỰ ĐỘNG DEPLOY TỪ GITHUB (Cloudflare Pages)

Mỗi lần có commit mới lên nhánh `main`, Cloudflare tự build và cập nhật site.

1. Cloudflare → **Workers & Pages → Create → Pages → Connect to Git** → chọn repo `AccaVN/giacngungon`.
2. Cấu hình build:
   - Production branch: `main`
   - Framework preset: `None`
   - Build command: `pip install -r requirements.txt && python3 build.py`
   - Build output directory: `dist`
3. Save and Deploy → kiểm tra tại `<tên-project>.pages.dev`.
4. Chuyển tên miền: xóa `giacngungon.org` khỏi **Custom domains** của project cũ (Direct Upload), rồi thêm vào project mới.

## ĐĂNG THỦ CÔNG LÊN CLOUDFLARE PAGES (Direct Upload)

1. Tạo tài khoản tại https://dash.cloudflare.com (miễn phí).
2. Vào **Workers & Pages → Create → Pages → Upload assets** (Direct Upload).
3. Đặt tên project (vd `giacngungon`), kéo thả **nội dung thư mục `dist/`** (hoặc file zip của thư mục dist) → Deploy.
   Site chạy ngay tại `giacngungon.pages.dev` – kiểm tra trước.
4. Gắn tên miền: trong project → **Custom domains → Set up a custom domain** → nhập `giacngungon.org` (và `www.giacngungon.org`).
   - Cách dễ nhất: chuyển DNS của tên miền về Cloudflare (Add site → đổi 2 nameserver tại nơi mua tên miền). SSL tự động.
5. Sau khi chạy ổn: vào Google Search Console → gửi `https://giacngungon.org/sitemap.xml`.
6. Hủy gói hosting WordPress cũ khi đã chắc chắn (nhớ sao lưu trước).

Cập nhật về sau: build lại → vào project → **Create new deployment** → tải `dist/` lên lại.

## BẬT FORM ĐẶT LỊCH GỬI VỀ EMAIL (5 phút)

Mặc định form sẽ hướng dẫn người bệnh gọi/nhắn Zalo và tự sao chép nội dung.
Để form gửi thẳng về email phòng khám:
1. Vào https://web3forms.com → nhập email phòng khám → nhận **Access Key** qua email.
2. Mở `static/assets/js/config.js` (hoặc `dist/assets/js/config.js` nếu không build lại), dán key vào `WEB3FORMS_KEY: "..."`.
3. Upload lại.

## THÊM / SỬA BÀI VIẾT

Tạo file `content/ten-bai-khong-dau.md` (tên file = đường dẫn bài):

```
---
title: "Tiêu đề bài"
category: mat-ngu          # mat-ngu | roi-loan-giac-ngu | cai-thien-giac-ngu | khoa-hoc-giac-ngu | doi-tuong | suc-khoe-tam-than
description: "Mô tả 1–2 câu (hiện trên Google và thẻ bài)"
date: 2026-10-01
updated: 2026-10-01
featured: false            # true = hiện ở mục Bài viết nổi bật trang chủ
weight: 0                  # (tùy chọn) bài cùng ngày: số lớn hơn xếp trước
reviewed: false            # true = hiện dòng "Tham vấn y khoa: Bs. Nguyễn Thi Phú"
key:
  - "Ý chính 1"
sources:
  - "Nguồn tham khảo 1"
---

Nội dung Markdown: ## Tiêu đề mục, **đậm**, - gạch đầu dòng, bảng |a|b|, > lưu ý, [link](/slug-bai-khac/)
```

Build lại trên máy (cần Python 3) – nếu dùng GitHub + Cloudflare thì không cần, chỉ commit là xong:
```
pip install -r requirements.txt
python3 build.py
```

## LƯU Ý QUAN TRỌNG

- Các bài viết được biên soạn dựa trên hướng dẫn y khoa quốc tế (AASM, NIH, ACP, WHO…), **chưa được bác sĩ duyệt**.
  Nên nhờ Bs. Phú đọc lại; bài nào đã duyệt thì đổi `reviewed: true` → trang sẽ hiện "Tham vấn y khoa".
- Thông tin bác sĩ, số điện thoại, link Facebook sửa ở đầu file `build.py` (mục SITE).
- Chưa có địa chỉ phòng khám trên site – thêm vào `build.py` nếu muốn.
