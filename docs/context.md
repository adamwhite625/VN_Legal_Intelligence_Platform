# Tổng quan Dự án: VN Legal Intelligence Platform

## Giới thiệu
VN Legal Intelligence Platform là một hệ thống tra cứu và tư vấn thông tin pháp luật Việt Nam cấp độ chuyên nghiệp (production-grade). Hệ thống ứng dụng kỹ thuật **Retrieval-Augmented Generation (RAG)** để cung cấp các câu trả lời chính xác, có căn cứ và trích dẫn cụ thể từ kho dữ liệu văn bản pháp quy.

## Các thành phần chính
1. **Backend (FastAPI)**: Cung cấp API mạnh mẽ, xử lý logic RAG và quản lý người dùng.
2. **Frontend (React/TypeScript)**: Giao diện hiện đại, dễ sử dụng, tích hợp bộ công cụ Dashboard cho Admin.
3. **Cơ sở dữ liệu**:
   - **Qdrant (Vector DB)**: Lưu trữ các bản nhúng (embeddings) của luật để tìm kiếm ngữ nghĩa.
   - **MySQL**: Lưu trữ thông tin người dùng, lịch sử chat, Bookmark và dữ liệu quản trị.
   - **Redis**: Dùng để quản lý cache và session, tăng tốc độ phản hồi.

## Kiến trúc RAG Agentic
Hệ thống sử dụng **LangGraph** để xây dựng một quy trình suy luận đa bước (7-node pipeline):
- **Contextualize**: Chuyển đổi câu hỏi của người dùng dựa trên ngữ cảnh lịch sử chat.
- **Router**: Phân loại ý định người dùng để quyết định chiến lược tìm kiếm.
- **Retriever**: Thực hiện tìm kiếm vector trên Qdrant.
- **Checker**: Kiểm tra mức độ liên quan và đầy đủ của thông tin đã lấy được.
- **Writer**: Tổng hợp câu trả lời cuối cùng với các trích dẫn luật cụ thể.
- **Clarifier**: Yêu cầu người dùng cung cấp thêm thông tin nếu câu hỏi mơ hồ.
- **Fallback**: Xử lý các trường hợp không tìm thấy thông tin hoặc có lỗi hệ thống.

## Công nghệ sử dụng (Tech Stack)
- **AI/LLM**: GPT-4o-mini, LangChain, LangGraph.
- **Backend**: Python 3.11+, FastAPI, SQLAlchemy.
- **Frontend**: React 19, Vite, TailwindCSS, Lucide Icons.
- **MLOps**: Docker, GitHub Actions, Jenkins, GCP Cloud Run.

## Mục tiêu của tài liệu triển khai
Hướng dẫn này giúp đưa dự án từ môi trường phát triển local lên hạ tầng đám mây chuyên nghiệp của Google Cloud, đảm bảo tính ổn định, bảo mật và khả năng mở rộng theo tiêu chuẩn MLOps.
