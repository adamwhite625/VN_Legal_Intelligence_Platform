# Lab 1: Nền tảng GCP và Quản lý Phân quyền IAM

## Mục tiêu
Bài lab này giúp bạn nắm vững các thao tác nền tảng: Tạo Project, quản lý Billing, kích hoạt dịch vụ (APIs) và cơ chế phân quyền IAM theo chuẩn Linux/Bash.

---

## Phụ lục: Hướng dẫn cài đặt Google Cloud CLI (gcloud)

### 1. Cài đặt trên Linux (Debian/Ubuntu)
```bash
sudo apt-get update
sudo apt-get install apt-transport-https ca-certificates gnupg curl
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
sudo apt-get update && sudo apt-get install google-cloud-sdk
```

### 2. Cài đặt trên macOS
Sử dụng Homebrew:
```bash
brew install --cask google-cloud-sdk
```

---

## Hướng dẫn thực hành chi tiết (CLI Linux & Web Console)

### Bước 1: Khởi tạo và Đăng nhập
- **CLI (Bash):** Chạy `gcloud init`.
- **Console (Web):** Truy cập [console.cloud.google.com](https://console.cloud.google.com).

### Bước 2: Tạo dự án (Project) mới
- **CLI (Bash):**
  ```bash
  export PROJECT_ID="thien-ai-lab-2026"
  gcloud projects create $PROJECT_ID --name "AI Engineer Lab"
  gcloud config set project $PROJECT_ID
  ```
- **Console (Web):** Nhấn ô chọn Project -> **New Project** -> Đặt tên -> **Create**.

### Bước 3: Liên kết Thanh toán & Kích hoạt API
- **CLI (Bash):**
  ```bash
  # Lấy mã Billing Account
  gcloud beta billing accounts list
  
  # Liên kết (Thay mã ID của bạn vào)
  gcloud beta billing projects link $PROJECT_ID --billing-account 012345-XXXXXX-XXXXXX
  
  # Bật API máy ảo
  gcloud services enable compute.googleapis.com cloudresourcemanager.googleapis.com
  ```
- **Console (Web):** 
  1. Menu **Billing** -> Đảm bảo project đã được gắn với tài khoản thanh toán.
  2. Menu **APIs & Services** -> **Library** -> Tìm "Compute Engine API" -> Nhấn **Enable**.

### Bước 4: Tạo Service Account (Tài khoản dịch vụ)
- **CLI (Bash):**
  ```bash
  export SA_NAME="lab-sa"
  gcloud iam service-accounts create $SA_NAME --display-name "Lab Service Account"
  ```
- **Console (Web):** Vào **IAM & Admin** -> **Service Accounts** -> **Create Service Account** -> Đặt tên `lab-sa` -> **Create and Continue**.

### Bước 5: Phân quyền IAM (Cấp quyền Viewer)
- **CLI (Bash):**
  ```bash
  export SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
  
  gcloud projects add-iam-policy-binding $PROJECT_ID \
      --member "serviceAccount:$SA_EMAIL" \
      --role "roles/viewer"
  ```
- **Console (Web):** Trong bước tạo SA ở trên, tại mục **Role**, chọn **Project** -> **Viewer** -> Nhấn **Done**.

### Bước 6: Tạo Key và Kiểm tra
- **CLI (Bash):**
  ```bash
  # Tải Key
  gcloud iam service-accounts keys create key.json --iam-account=$SA_EMAIL
  
  # Đăng nhập bằng SA
  gcloud auth activate-service-account --key-file=key.json
  
  # Kiểm tra (Thành công nếu hiện danh sách Zone)
  gcloud compute zones list
  ```
- **Console (Web):** Vào danh sách **Service Accounts** -> Nhấn vào `lab-sa` -> Tab **Keys** -> **Add Key** -> **Create new key** -> **JSON**.

### Bước 7: Dọn dẹp
- **CLI:** `gcloud projects delete $PROJECT_ID`
- **Console:** Vào **IAM & Admin** -> **Settings** -> **Shut Down**.
