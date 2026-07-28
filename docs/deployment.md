# Hướng dẫn Triển khai MLOps trên Google Cloud Platform

Tài liệu này hướng dẫn chi tiết cách thiết lập hạ tầng và triển khai dự án **VN Legal Intelligence Platform** lên GCP.

---

## Phase 1: Thiết lập Hạ tầng (Infrastructure Setup)

Giai đoạn này tập trung vào việc chuẩn bị "ngôi nhà" cho ứng dụng trên Cloud.

### 1. Chuẩn bị Tài khoản & Project
1. Truy cập [Google Cloud Console](https://console.cloud.google.com/).
2. Tạo một Project mới (ví dụ: `vn-legal-bot`).
3. Đảm bảo đã bật **Billing** cho dự án.

### 2. Kích hoạt APIs
Mở Terminal (Cloud Shell) và chạy lệnh sau để kích hoạt các dịch vụ cần thiết:
```bash
gcloud services enable \
    run.googleapis.com \
    containerregistry.googleapis.com \
    artifactregistry.googleapis.com \
    sqladmin.googleapis.com \
    secretmanager.googleapis.com \
    compute.googleapis.com
```

### 3. Cấu hình Cơ sở dữ liệu (Cloud SQL)
1. Vào **SQL** -> **Create Instance** -> Chọn **MySQL**.
2. Thiết lập ID instance (ví dụ: `law-db`) và mật khẩu root.
3. Chọn cấu hình phù hợp (Shared core/Small là đủ cho giai đoạn đầu).
4. Tạo database tên là `law_chatbot_db`.

### 4. Tạo Artifact Registry (Kho lưu trữ ảnh Docker)
1. Vào **Artifact Registry** -> **Create Repository**.
2. Name: `legal-repo`.
3. Format: `Docker`.
4. Region: `asia-southeast1`.

### 5. Thiết lập Service Account (Chìa khóa cho CI/CD)

Đây là bước quan trọng nhất để cấp quyền cho GitHub hoặc Jenkins thay mặt bạn thao tác trên GCP.

1.  **Tạo Service Account**: Vào **IAM & Admin** -> **Service Accounts** -> **Create Service Account**.
    - Tên: `github-actions-deployer`.
2.  **Gán quyền (Role)**: Cấp các Role sau để pipeline hoạt động:
    - `Cloud Run Admin` (Để triển khai Backend và Frontend lên Cloud Run).
    - `Artifact Registry Writer` (Để có quyền đẩy ảnh Docker vào kho lưu trữ).
    - `Secret Manager Accessor` (Để ứng dụng lấy được các Key nhạy cảm như OpenAI API Key).
    - `Storage Admin` (Hỗ trợ quá trình lưu trữ tạm khi build container).
3.  **Tạo và tải Key JSON**:
    - Sau khi tạo xong, trong danh sách Service Account, hãy click vào **Địa chỉ Email** của account bạn vừa tạo.
    - Chuyển sang thẻ **Keys** ở menu phía trên.
    - Cạnh nút **Add Key**, chọn **Create new key**.
    - Chọn định dạng **JSON** và nhấn **Create**.
    - File `.json` sẽ tự động tải về máy tính của bạn.
    - **CẢNH BÁO**: Tuyệt đối **KHÔNG** đưa file này vào thư mục code và **KHÔNG** đẩy lên GitHub. Nếu lộ file này, người khác có thể toàn quyền sử dụng project của bạn.
4.  **Cấu hình trên GitHub (Đưa Key lên Cloud)**:
    - Mở file JSON vừa tải bằng phần mềm đọc văn bản (Notepad, VS Code...).
    - **Sao chép toàn bộ nội dung** (nhấn Ctrl+A rồi Ctrl+C).
    - Truy cập Repository của bạn trên GitHub -> chọn tab **Settings**.
    - Phía cột bên trái, chọn **Secrets and variables** -> **Actions**.
    - Bấm nút xanh **New repository secret**.
    - Ô **Name**: Nhập chính xác `GCP_SA_KEY`.
    - Ô **Secret**: Dán toàn bộ nội dung bạn đã copy từ file JSON vào.
    - Bấm **Add secret** để hoàn tất.


---

## Phase 2: Triển khai & MLOps Pipeline

Giai đoạn này đưa mã nguồn vào quy trình tự động hóa và thiết lập các thành phần cần thiết để ứng dụng hoạt động trên Cloud.

### 1. Cấu hình Secret Manager (Quản lý biến môi trường bảo mật)

Thay vì dùng file `.env`, chúng ta sẽ cấu hình các biến môi trường này trong **Secret Manager**. 

1.  **Quan trọng**: Bật **Cloud SQL Admin API** để Cloud Run truy cập được DB.
2.  **Danh sách các Secret cần tạo**:

| Tên Secret | Giá trị mẫu / Hướng dẫn |
| :--- | :--- |
| **`OPENAI_API_KEY`** | Dán Key OpenAI của bạn. |
| **`DB_USER`** | `root` |
| **`DB_PASSWORD`** | `changeme` |
| **`DB_NAME`** | `law_chatbot_db` |
| **`DB_HOST`** | `/cloudsql/vn-legal-bot:asia-southeast1:law-db` (Dùng Connection Name) |
| **`QDRANT_HOST`** | `35.197.130.85` (IP máy ảo Qdrant bạn vừa tạo) |
| **`QDRANT_PORT`** | `6333` |
| **`SECRET_KEY`** | (Lấy từ file `.env` local của bạn) |
| **`ALGORITHM`** | `HS256` |

---

### 2. Triển khai Qdrant và Nạp Dữ liệu

#### Bước A: Hướng dẫn cài đặt Qdrant trên VM (Lưu để tham khảo)

Mục này lưu lại các bước bạn đã thực hiện để thiết lập Vector Database:

1.  **Tạo VM**: Vào **Compute Engine** -> **VM Instances** -> **Create Instance**.
    - Tên: `qdrant-vm-instance`.
    - Cấu hình: `e2-medium` (2 vCPU, 4GB RAM), OS: **Ubuntu 22.04 LTS**.
    - **Firewall**: Tích chọn **Allow HTTP** và **Allow HTTPS**.
    - **Networking**: Thêm tag `qdrant-server`.
2.  **Mở cổng Firewall tùy chỉnh**: 
    - Vào **VPC Network** -> **Firewall** -> **Create Firewall Rule**.
    - Tên: `allow-qdrant-ports`, Targets: `Specified target tags` (`qdrant-server`).
    - Source range: `0.0.0.0/0`, Protocols and ports: TCP `6333`, `6334`.
3.  **Lệnh cài đặt SSH**:
    ```bash
    # Cài Docker
    sudo apt-get update && sudo apt-get install -y docker.io
    sudo systemctl start docker

    # Tạo thư mục và chạy Qdrant
    mkdir qdrant_storage
    sudo docker run -d --name qdrant-server \
      -p 6333:6333 -p 6334:6334 \
      -v $(pwd)/qdrant_storage:/qdrant/storage:z \
      qdrant/qdrant
    ```
    *IP hiện tại máy ảo của bạn là: `35.197.130.85`.*

#### Bước B: Nạp dữ liệu từ máy Local lên Cloud Qdrant
Để "đẩy" kiến thức luật lên database trên Cloud, bạn thực hiện tại máy tính của mình:

1.  **Cập nhật `.env` local**: Sửa `QDRANT_HOST=35.197.130.85`.
2.  **Kích hoạt môi trường**: `conda activate legal_bot` (hoặc venv của bạn).
3.  **Chạy lệnh nạp**:
    ```bash
    python scripts/import_local.py
    ```
    *Dữ liệu sẽ được mã hóa và đẩy lên máy ảo GCP thông qua cổng 6333.*

---

### 3. Cấu hình GitHub Secrets (Dành cho CI/CD)

Vào Repo GitHub -> **Settings** -> **Secrets** -> **Actions**. Bạn cần các Secret để pipeline đẩy code lên GCP:

- **`GCP_SA_KEY`**: Nội dung JSON key của Service Account.
- **`GCP_PROJECT_ID`**: `vn-legal-bot`.
- **`OPENAI_API_KEY`**: Để chạy test evaluation.
- *(Các biến còn lại đã được cấu hình trong Secret Manager nên Cloud Run sẽ tự lấy).*

### 4. Kích hoạt Pipeline và Kiểm tra

1.  Push mã nguồn lên nhánh `main`.
2.  Theo dõi tại tab **Actions** trên GitHub. Pipeline sẽ tự động thực hiện:
    - Kiểm tra Code (Lint).
    - Chạy Test & **ML Evaluation** (Quality Gate).
    - Build Docker images và đẩy lên Artifact Registry.
    - Deploy tự động lên **Cloud Run**.

### 5. Kiểm tra kết quả
- Backend: `https://legal-backend-xxxx-as.a.run.app/docs`.
- Frontend: `https://legal-frontend-xxxx-as.a.run.app`.



---

## Ghi chú về MLOps
- **Model Versioning**: Mỗi lần build, ảnh Docker được gắn tag bằng `Git SHA`, giúp bạn có thể rollback (quay lại phiên bản cũ) bất cứ lúc nào.
- **Automated Evaluation**: Quy trình chạy `RUN_EVALUATION.py` đảm bảo Logic RAG của bạn không bị giảm chất lượng khi cập nhật code mới.
