# Streaming RAG Pipeline Latency Benchmark Report

Generated: 2026-07-17 14:03:54
Total queries: 10

## 1. Latency Summary

| Metric | E2E Value | TTFT Value |
|--------|-----------|------------|
| MEAN | 9.8818s | 4.5550s |
| MEDIAN | 11.0789s | 4.7214s |
| MIN | 1.2298s | 1.2298s |
| MAX | 15.6441s | 9.3386s |
| STDEV | 4.3434s | - |
| P90 | 15.6441s | - |

## 2. Per-Node Latency Breakdown (seconds)

| Node | Mean | Median | Min | Max | Stdev | Runs |
|------|------|--------|-----|-----|-------|------|
| answer | 7.5383 | 8.2664 | 2.6979 | 11.6758 | 3.3753 | 8 |
| checker | 2.2224 | 2.1195 | 0.0002 | 5.9906 | 1.9635 | 10 |
| clarifier | 2.0306 | 2.0306 | 2.0306 | 2.0306 | 0.0000 | 1 |
| contextualize | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 10 |
| fallback | 0.0001 | 0.0001 | 0.0001 | 0.0001 | 0.0000 | 1 |
| retriever | 0.0677 | 0.0417 | 0.0365 | 0.2737 | 0.0728 | 10 |
| router | 1.3493 | 1.2128 | 0.9909 | 2.2385 | 0.3893 | 10 |

**Slowest node (avg):** `answer` at 7.5383s

## 3. Retriever Sub-Step Analysis (seconds)

| Sub-Step | Mean | Median | Min | Max |
|----------|------|--------|-----|-----|
| embedding | 0.0436 | 0.0222 | 0.0168 | 0.2144 |
| filtering | 0.0000 | 0.0000 | 0.0000 | 0.0001 |
| qdrant_search | 0.0240 | 0.0202 | 0.0174 | 0.0592 |

## 4. Per-Query Detail

### 4.1. [Q01] PENAL

**Question:** Tội giết người bị xử phạt như thế nào theo Bộ luật Hình sự?

**Latency:** TTFT: 6.0996s | E2E: 14.0415s total | Docs retrieved: 10 | Path: contextualize -> router -> retriever -> checker -> writer

### 4.2. [Q02] CIVIL

**Question:** Quyền thừa kế theo pháp luật được quy định ra sao?

**Latency:** TTFT: 5.6243s | E2E: 12.1544s total | Docs retrieved: 5 | Path: contextualize -> router -> retriever -> checker -> writer

### 4.3. [Q03] BUSINESS

**Question:** Phạm vi điều chỉnh của Luật Doanh nghiệp 2020 là gì?

**Latency:** TTFT: 1.2298s | E2E: 1.2298s total | Docs retrieved: 0 | Path: contextualize -> router -> retriever -> checker -> fallback

### 4.4. [Q04] MARRIAGE

**Question:** Điều kiện kết hôn theo Luật Hôn nhân và Gia đình là gì?

**Latency:** TTFT: 4.4768s | E2E: 6.6997s total | Docs retrieved: 4 | Path: contextualize -> router -> retriever -> checker -> writer

### 4.5. [Q05] PROCEDURE

**Question:** Thủ tục đăng ký thành lập doanh nghiệp gồm những bước nào?

**Latency:** TTFT: 2.3125s | E2E: 12.1752s total | Docs retrieved: 4 | Path: contextualize -> router -> retriever -> checker -> writer

### 4.6. [Q06] PENAL

**Question:** Tội trộm cắp tài sản có giá trị từ 50 triệu trở lên bị xử phạt thế nào?

**Latency:** TTFT: 9.3386s | E2E: 9.3386s total | Docs retrieved: 10 | Path: contextualize -> router -> retriever -> checker -> clarifier

### 4.7. [Q07] CIVIL

**Question:** Hợp đồng dân sự vô hiệu trong trường hợp nào?

**Latency:** TTFT: 6.0011s | E2E: 11.5357s total | Docs retrieved: 5 | Path: contextualize -> router -> retriever -> checker -> writer

### 4.8. [Q08] BUSINESS

**Question:** Doanh nghiệp xã hội cần đáp ứng những tiêu chí gì?

**Latency:** TTFT: 3.5398s | E2E: 5.3769s total | Docs retrieved: 2 | Path: contextualize -> router -> retriever -> checker -> writer

### 4.9. [Q09] MARRIAGE

**Question:** Quyền và nghĩa vụ của cha mẹ đối với con cái theo luật hôn nhân gia đình?

**Latency:** TTFT: 4.9659s | E2E: 15.6441s total | Docs retrieved: 3 | Path: contextualize -> router -> retriever -> checker -> writer

### 4.10. [Q10] PROCEDURE

**Question:** Quy trình giải quyết tranh chấp lao động cá nhân được thực hiện như thế nào?

**Latency:** TTFT: 1.9612s | E2E: 10.6221s total | Docs retrieved: 4 | Path: contextualize -> router -> retriever -> checker -> writer

## 5. Quick Comparison Table

| ID | Category | TTFT (s) | E2E (s) | Docs | Terminal | Question |
|----|----------|----------|---------|------|----------|----------|
| Q01 | penal | 6.0996 | 14.0415 | 10 | writer | Tội giết người bị xử phạt như thế nào th... |
| Q02 | civil | 5.6243 | 12.1544 | 5 | writer | Quyền thừa kế theo pháp luật được quy đị... |
| Q03 | business | 1.2298 | 1.2298 | 0 | fallback | Phạm vi điều chỉnh của Luật Doanh nghiệp... |
| Q04 | marriage | 4.4768 | 6.6997 | 4 | writer | Điều kiện kết hôn theo Luật Hôn nhân và ... |
| Q05 | procedure | 2.3125 | 12.1752 | 4 | writer | Thủ tục đăng ký thành lập doanh nghiệp g... |
| Q06 | penal | 9.3386 | 9.3386 | 10 | clarifier | Tội trộm cắp tài sản có giá trị từ 50 tr... |
| Q07 | civil | 6.0011 | 11.5357 | 5 | writer | Hợp đồng dân sự vô hiệu trong trường hợp... |
| Q08 | business | 3.5398 | 5.3769 | 2 | writer | Doanh nghiệp xã hội cần đáp ứng những ti... |
| Q09 | marriage | 4.9659 | 15.6441 | 3 | writer | Quyền và nghĩa vụ của cha mẹ đối với con... |
| Q10 | procedure | 1.9612 | 10.6221 | 4 | writer | Quy trình giải quyết tranh chấp lao động... |