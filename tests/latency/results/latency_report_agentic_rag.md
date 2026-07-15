# RAG Pipeline Latency Benchmark Report

Generated: 2026-07-14 13:52:32
Total queries: 10

## 1. End-to-End Latency Summary

| Metric | Value |
|--------|-------|
| MEAN | 6.9149s |
| MEDIAN | 6.8371s |
| MIN | 0.9779s |
| MAX | 12.8059s |
| STDEV | 3.4048s |
| P90 | 12.8059s |
| P95 | 12.8059s |

## 2. Per-Node Latency Breakdown (seconds)

| Node | Mean | Median | Min | Max | Stdev | Runs |
|------|------|--------|-----|-----|-------|------|
| answer | 5.4699 | 5.4352 | 2.0786 | 9.7773 | 2.4808 | 8 |
| checker | 1.3215 | 1.6050 | 0.0002 | 2.8216 | 0.9871 | 10 |
| clarifier | 1.5864 | 1.5864 | 1.5864 | 1.5864 | 0.0000 | 1 |
| contextualize | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 10 |
| fallback | 0.0003 | 0.0003 | 0.0003 | 0.0003 | 0.0000 | 1 |
| retriever | 0.0649 | 0.0423 | 0.0370 | 0.2609 | 0.0690 | 10 |
| router | 0.9877 | 0.8994 | 0.7969 | 1.5549 | 0.2296 | 10 |

**Slowest node (avg):** `answer` at 5.4699s

## 3. Retriever Sub-Step Analysis (seconds)

| Sub-Step | Mean | Median | Min | Max |
|----------|------|--------|-----|-----|
| embedding | 0.0450 | 0.0249 | 0.0207 | 0.2230 |
| filtering | 0.0000 | 0.0000 | 0.0000 | 0.0001 |
| qdrant_search | 0.0199 | 0.0174 | 0.0153 | 0.0379 |

## 4. Per-Query Detail

### 4.1. [Q01] PENAL

**Question:** Tội giết người bị xử phạt như thế nào theo Bộ luật Hình sự?

**Answer:**

Tội giết người bị xử phạt theo các quy định của Bộ luật Hình sự như sau:

1. **Tội giết người thông thường**: 
   - Theo Điều 123 (Tội giết người), người nào giết người thuộc một trong các trường hợp quy định sẽ bị phạt tù từ 12 năm đến 20 năm, tù chung thân hoặc tử hình.

2. **Tội giết người do vượt quá giới hạn phòng vệ chính đáng**:
   - Theo Điều 126 (Tội giết người do vượt quá giới hạn phòng vệ chính đáng hoặc do vượt quá mức cần thiết khi bắt giữ người phạm tội), người nào giết người trong trường hợp này sẽ bị phạt cải tạo không giam giữ đến 02 năm hoặc phạt tù từ 03 tháng đến 02 năm. Nếu phạm tội đối với 02 người trở lên, mức phạt sẽ tăng lên từ 02 năm đến 05 năm.

3. **Hình phạt tử hình**:
   - Theo Điều 40 (Tử hình), hình phạt tử hình chỉ áp dụng đối với người phạm tội đặc biệt nghiêm trọng thuộc các nhóm tội xâm phạm an ninh quốc gia, xâm phạm tính mạng con người, và một số tội phạm đặc biệt nghiêm trọng khác.

4. **Căn cứ quyết định hình phạt**:
   - Theo Điều 50 (Căn cứ quyết định hình phạt), Tòa án sẽ căn cứ vào tính chất và mức độ nguy hiểm cho xã hội của hành vi phạm tội, nhân thân người phạm tội, cũng như các tình tiết giảm nhẹ và tăng nặng trách nhiệm hình sự để quyết định hình phạt.

Tóm lại, hình phạt cho tội giết người có thể rất nghiêm khắc, tùy thuộc vào tính chất và hoàn cảnh của từng vụ án cụ thể.

**Latency:** 9.4789s total | Docs retrieved: 10 | Path: contextualize -> router -> retriever -> checker -> writer

| Node | Time (s) | % of Total |
|------|----------|------------|
| contextualize | 0.0000 | 0.0% |
| router | 1.5549 | 16.4% |
| retriever | 0.2609 | 2.8% |
| checker | 1.4649 | 15.5% |
| answer | 6.1896 | 65.3% |

**Retriever sub-steps:**

| Sub-Step | Time (s) |
|----------|----------|
| embedding | 0.2230 |
| qdrant_search | 0.0379 |
| filtering | 0.0000 |

---

### 4.2. [Q02] CIVIL

**Question:** Quyền thừa kế theo pháp luật được quy định ra sao?

**Answer:**

Quyền thừa kế theo pháp luật được quy định như sau:

1. **Khái niệm thừa kế theo pháp luật**: Thừa kế theo pháp luật là việc thừa kế được thực hiện theo hàng thừa kế, điều kiện và trình tự do pháp luật quy định. Điều này có nghĩa là khi không có di chúc, tài sản sẽ được phân chia theo quy định của pháp luật. (Theo Điều 649 Bộ luật Dân sự 2015).

2. **Quyền lập di chúc**: Cá nhân có quyền lập di chúc để định đoạt tài sản của mình, và nếu không có di chúc, tài sản sẽ được để lại cho người thừa kế theo pháp luật. (Theo Điều 609 Bộ luật Dân sự 2015).

3. **Xác lập quyền sở hữu**: Người thừa kế sẽ được xác lập quyền sở hữu đối với tài sản thừa kế theo quy định của pháp luật. (Theo Điều 234 Bộ luật Dân sự 2015).

4. **Thời điểm phát sinh quyền và nghĩa vụ**: Quyền và nghĩa vụ của người thừa kế phát sinh kể từ thời điểm mở thừa kế, tức là thời điểm người để lại di sản qua đời. (Theo Điều 614 Bộ luật Dân sự 2015).

5. **Quy định về thừa kế quốc tế**: Thừa kế được xác định theo pháp luật của nước mà người để lại di sản có quốc tịch ngay trước khi chết, và việc thực hiện quyền thừa kế đối với bất động sản được xác định theo pháp luật của nước nơi có bất động sản đó. (Theo Điều 680 Bộ luật Dân sự 2015). 

Tóm lại, quyền thừa kế theo pháp luật được quy định rõ ràng về khái niệm, quyền lập di chúc, xác lập quyền sở hữu, thời điểm phát sinh quyền và nghĩa vụ, cũng như các quy định liên quan đến thừa kế quốc tế.

**Latency:** 12.8059s total | Docs retrieved: 5 | Path: contextualize -> router -> retriever -> checker -> writer

| Node | Time (s) | % of Total |
|------|----------|------------|
| contextualize | 0.0000 | 0.0% |
| router | 1.1570 | 9.0% |
| retriever | 0.0476 | 0.4% |
| checker | 1.8180 | 14.2% |
| answer | 9.7773 | 76.3% |

**Retriever sub-steps:**

| Sub-Step | Time (s) |
|----------|----------|
| embedding | 0.0291 |
| qdrant_search | 0.0184 |
| filtering | 0.0001 |

---

### 4.3. [Q03] BUSINESS

**Question:** Phạm vi điều chỉnh của Luật Doanh nghiệp 2020 là gì?

**Answer:**

Xin lỗi, hiện tại cơ sở dữ liệu của tôi chưa có văn bản pháp lý chính xác về vấn đề này. Để đảm bảo an toàn pháp lý, tôi xin phép không tự suy đoán. Bạn vui lòng tham vấn luật sư trực tiếp.

**Latency:** 0.9779s total | Docs retrieved: 0 | Path: contextualize -> router -> retriever -> checker -> fallback

| Node | Time (s) | % of Total |
|------|----------|------------|
| contextualize | 0.0000 | 0.0% |
| router | 0.9297 | 95.1% |
| retriever | 0.0422 | 4.3% |
| checker | 0.0002 | 0.0% |
| fallback | 0.0003 | 0.0% |

**Retriever sub-steps:**

| Sub-Step | Time (s) |
|----------|----------|
| embedding | 0.0251 |
| qdrant_search | 0.0171 |
| filtering | 0.0000 |

---

### 4.4. [Q04] MARRIAGE

**Question:** Điều kiện kết hôn theo Luật Hôn nhân và Gia đình là gì?

**Answer:**

Theo Điều 3 của Luật Hôn nhân và Gia đình 2014, kết hôn là việc nam và nữ xác lập quan hệ vợ chồng với nhau theo quy định của Luật này về điều kiện kết hôn và đăng ký kết hôn. Cụ thể, điều kiện kết hôn được quy định tại Điều 8 của Luật này, bao gồm các yêu cầu về độ tuổi, tình trạng hôn nhân và các điều kiện khác mà pháp luật quy định. 

Do đó, để kết hôn hợp pháp, các bên phải đáp ứng đầy đủ các điều kiện theo quy định tại Điều 8 của Luật Hôn nhân và Gia đình 2014.

**Latency:** 6.8210s total | Docs retrieved: 4 | Path: contextualize -> router -> retriever -> checker -> writer

| Node | Time (s) | % of Total |
|------|----------|------------|
| contextualize | 0.0000 | 0.0% |
| router | 0.9930 | 14.6% |
| retriever | 0.0509 | 0.7% |
| checker | 2.8216 | 41.4% |
| answer | 2.9492 | 43.2% |

**Retriever sub-steps:**

| Sub-Step | Time (s) |
|----------|----------|
| embedding | 0.0246 |
| qdrant_search | 0.0263 |
| filtering | 0.0000 |

---

### 4.5. [Q05] PROCEDURE

**Question:** Thủ tục đăng ký thành lập doanh nghiệp gồm những bước nào?

**Answer:**

Thủ tục đăng ký thành lập doanh nghiệp gồm các bước sau:

1. **Người thành lập doanh nghiệp hoặc người được ủy quyền thực hiện đăng ký doanh nghiệp**: Theo Điều 26 Luật Doanh nghiệp 2020, người thành lập doanh nghiệp có thể thực hiện đăng ký theo một trong ba phương thức: 
   - Đăng ký trực tiếp tại Cơ quan đăng ký kinh doanh.
   - Đăng ký qua dịch vụ bưu chính.
   - Đăng ký qua mạng thông tin điện tử.

2. **Nộp hồ sơ đăng ký doanh nghiệp**: Nếu chọn phương thức đăng ký qua mạng thông tin điện tử, người thành lập doanh nghiệp cần nộp hồ sơ qua Cổng thông tin quốc gia về đăng ký doanh nghiệp. Hồ sơ này phải bao gồm các dữ liệu theo quy định của Luật và được thể hiện dưới dạng văn bản điện tử.

3. **Xem xét tính hợp lệ của hồ sơ**: Theo Điều 26, trong thời hạn 03 ngày làm việc kể từ ngày nhận hồ sơ, Cơ quan đăng ký kinh doanh có trách nhiệm xem xét tính hợp lệ của hồ sơ đăng ký doanh nghiệp.

4. **Cấp Giấy chứng nhận đăng ký doanh nghiệp**: Nếu hồ sơ hợp lệ, Cơ quan đăng ký kinh doanh sẽ cấp Giấy chứng nhận đăng ký doanh nghiệp. Nếu hồ sơ chưa hợp lệ, cơ quan này phải thông báo bằng văn bản nội dung cần sửa đổi, bổ sung.

5. **Thông báo từ chối đăng ký (nếu có)**: Trong trường hợp từ chối đăng ký doanh nghiệp, Cơ quan đăng ký kinh doanh phải thông báo bằng văn bản cho người thành lập doanh nghiệp và nêu rõ lý do từ chối.

Tóm lại, thủ tục đăng ký thành lập doanh nghiệp bao gồm việc nộp hồ sơ, xem xét tính hợp lệ, cấp Giấy chứng nhận hoặc thông báo từ chối.

**Latency:** 6.8533s total | Docs retrieved: 4 | Path: contextualize -> router -> retriever -> checker -> writer

| Node | Time (s) | % of Total |
|------|----------|------------|
| contextualize | 0.0000 | 0.0% |
| router | 0.8495 | 12.4% |
| retriever | 0.0424 | 0.6% |
| checker | 0.0003 | 0.0% |
| answer | 5.9553 | 86.9% |

**Retriever sub-steps:**

| Sub-Step | Time (s) |
|----------|----------|
| embedding | 0.0270 |
| qdrant_search | 0.0153 |
| filtering | 0.0000 |

---

### 4.6. [Q06] PENAL

**Question:** Tội trộm cắp tài sản có giá trị từ 50 triệu trở lên bị xử phạt thế nào?

**Answer:**

1. Bạn có biết rõ về loại tài sản bị trộm cắp là gì không?  
2. Ai là người bị hại trong vụ trộm cắp này?  
3. Bạn đang tìm hiểu về hình phạt cho người phạm tội hay quyền lợi của người bị hại?  

**Latency:** 4.1777s total | Docs retrieved: 10 | Path: contextualize -> router -> retriever -> checker -> clarifier

| Node | Time (s) | % of Total |
|------|----------|------------|
| contextualize | 0.0000 | 0.0% |
| router | 0.8692 | 20.8% |
| retriever | 0.0416 | 1.0% |
| checker | 1.6743 | 40.1% |
| clarifier | 1.5864 | 38.0% |

**Retriever sub-steps:**

| Sub-Step | Time (s) |
|----------|----------|
| embedding | 0.0235 |
| qdrant_search | 0.0180 |
| filtering | 0.0001 |

---

### 4.7. [Q07] CIVIL

**Question:** Hợp đồng dân sự vô hiệu trong trường hợp nào?

**Answer:**

Hợp đồng dân sự vô hiệu trong các trường hợp sau:

1. **Không tuân thủ quy định về hình thức**: Theo Điều 129 (Bộ luật Dân sự 2015), giao dịch dân sự vi phạm quy định điều kiện có hiệu lực về hình thức thì vô hiệu, trừ trường hợp các bên đã thực hiện ít nhất hai phần ba nghĩa vụ trong giao dịch.

2. **Bị nhầm lẫn**: Theo Điều 126 (Bộ luật Dân sự 2015), nếu giao dịch dân sự được xác lập có sự nhầm lẫn làm cho một bên hoặc các bên không đạt được mục đích của việc xác lập giao dịch, bên bị nhầm lẫn có quyền yêu cầu Tòa án tuyên bố giao dịch vô hiệu.

3. **Bị lừa dối, đe dọa, cưỡng ép**: Theo Điều 127 (Bộ luật Dân sự 2015), khi một bên tham gia giao dịch do bị lừa dối hoặc bị đe dọa, cưỡng ép thì có quyền yêu cầu Tòa án tuyên bố giao dịch đó là vô hiệu.

4. **Người không nhận thức và làm chủ được hành vi của mình**: Theo Điều 132 (Bộ luật Dân sự 2015), giao dịch dân sự được xác lập bởi người không nhận thức và làm chủ được hành vi của mình cũng bị coi là vô hiệu.

5. **Các trường hợp khác theo quy định**: Theo Điều 407 (Bộ luật Dân sự 2015), các quy định về giao dịch dân sự vô hiệu từ Điều 123 đến Điều 133 cũng được áp dụng đối với hợp đồng vô hiệu.

**Latency:** 10.2527s total | Docs retrieved: 5 | Path: contextualize -> router -> retriever -> checker -> writer

| Node | Time (s) | % of Total |
|------|----------|------------|
| contextualize | 0.0000 | 0.0% |
| router | 0.8639 | 8.4% |
| retriever | 0.0456 | 0.4% |
| checker | 1.7845 | 17.4% |
| answer | 7.5528 | 73.7% |

**Retriever sub-steps:**

| Sub-Step | Time (s) |
|----------|----------|
| embedding | 0.0296 |
| qdrant_search | 0.0160 |
| filtering | 0.0000 |

---

### 4.8. [Q08] BUSINESS

**Question:** Doanh nghiệp xã hội cần đáp ứng những tiêu chí gì?

**Answer:**

Doanh nghiệp xã hội cần đáp ứng các tiêu chí sau đây:

1. Là doanh nghiệp được đăng ký thành lập theo quy định của Luật này.
2. Mục tiêu hoạt động nhằm giải quyết vấn đề xã hội, môi trường vì lợi ích cộng đồng.
3. Sử dụng ít nhất 51% tổng lợi nhuận sau thuế hằng năm của doanh nghiệp để tái đầu tư nhằm thực hiện mục tiêu đã đăng ký.

Theo Điều 10 (Luật Doanh nghiệp 2020).

**Latency:** 4.4585s total | Docs retrieved: 2 | Path: contextualize -> router -> retriever -> checker -> writer

| Node | Time (s) | % of Total |
|------|----------|------------|
| contextualize | 0.0000 | 0.0% |
| router | 0.7969 | 17.9% |
| retriever | 0.0401 | 0.9% |
| checker | 1.5358 | 34.4% |
| answer | 2.0786 | 46.6% |

**Retriever sub-steps:**

| Sub-Step | Time (s) |
|----------|----------|
| embedding | 0.0225 |
| qdrant_search | 0.0176 |
| filtering | 0.0000 |

---

### 4.9. [Q09] MARRIAGE

**Question:** Quyền và nghĩa vụ của cha mẹ đối với con cái theo luật hôn nhân gia đình?

**Answer:**

Quyền và nghĩa vụ của cha mẹ đối với con cái theo Luật Hôn nhân và Gia đình 2014 được quy định như sau:

1. **Quyền và nghĩa vụ chung của cha mẹ**:
   - Theo Điều 68, quyền và nghĩa vụ của cha mẹ và con được tôn trọng và bảo vệ. Con sinh ra không phụ thuộc vào tình trạng hôn nhân của cha mẹ đều có quyền và nghĩa vụ như nhau đối với cha mẹ của mình.

2. **Quyền yêu cầu và nghĩa vụ nuôi dưỡng**:
   - Theo Điều 83, cha, mẹ trực tiếp nuôi con có quyền yêu cầu người không trực tiếp nuôi con thực hiện các nghĩa vụ theo quy định tại Điều 82 của Luật này và yêu cầu người không trực tiếp nuôi con cùng các thành viên gia đình tôn trọng quyền được nuôi con của mình.

3. **Trách nhiệm chăm sóc và giáo dục**:
   - Theo Điều 81, sau khi ly hôn, cha mẹ vẫn có quyền và nghĩa vụ trông nom, chăm sóc, nuôi dưỡng, giáo dục con chưa thành niên. Vợ, chồng có thể thỏa thuận về người trực tiếp nuôi con và nghĩa vụ, quyền của mỗi bên; nếu không thỏa thuận được, Tòa án sẽ quyết định dựa trên quyền lợi của con.

4. **Cấm cản trở quyền thăm nom**:
   - Theo Điều 83, cha, mẹ trực tiếp nuôi con cùng các thành viên gia đình không được cản trở người không trực tiếp nuôi con trong việc thăm nom, chăm sóc, nuôi dưỡng, giáo dục con.

Tóm lại, cha mẹ có quyền và nghĩa vụ bảo vệ, chăm sóc, nuôi dưỡng và giáo dục con cái, đồng thời phải tôn trọng quyền thăm nom của người không trực tiếp nuôi con.

**Latency:** 7.8866s total | Docs retrieved: 3 | Path: contextualize -> router -> retriever -> checker -> writer

| Node | Time (s) | % of Total |
|------|----------|------------|
| contextualize | 0.0000 | 0.0% |
| router | 0.8099 | 10.3% |
| retriever | 0.0411 | 0.5% |
| checker | 2.1152 | 26.8% |
| answer | 4.9150 | 62.3% |

**Retriever sub-steps:**

| Sub-Step | Time (s) |
|----------|----------|
| embedding | 0.0244 |
| qdrant_search | 0.0167 |
| filtering | 0.0000 |

---

### 4.10. [Q10] PROCEDURE

**Question:** Quy trình giải quyết tranh chấp lao động cá nhân được thực hiện như thế nào?

**Answer:**

Quy trình giải quyết tranh chấp lao động cá nhân được thực hiện theo các bước sau:

1. **Hòa giải**: Tranh chấp lao động cá nhân phải được giải quyết thông qua thủ tục hòa giải của hòa giải viên lao động. Nếu hòa giải thành nhưng các bên không thực hiện hoặc thực hiện không đúng, hoặc hòa giải không thành, hoặc hết thời hạn hòa giải mà hòa giải viên lao động không tiến hành hòa giải, thì các bên có thể tiếp tục đến bước tiếp theo. (Theo Điều 32, Bộ luật Lao động 2019).

2. **Thẩm quyền giải quyết**: Nếu hòa giải không thành, tranh chấp lao động cá nhân có thể được đưa ra giải quyết bởi các cơ quan, tổ chức có thẩm quyền như hòa giải viên lao động, Hội đồng trọng tài lao động hoặc Tòa án nhân dân. (Theo Điều 187, Bộ luật Lao động 2019).

3. **Cấm hành động đơn phương**: Trong thời gian tranh chấp lao động đang được giải quyết, không bên nào được hành động đơn phương chống lại bên kia. (Theo Điều 186, Bộ luật Lao động 2019).

Quy trình này đảm bảo rằng các bên liên quan có cơ hội giải quyết tranh chấp một cách hòa bình trước khi đưa ra các biện pháp pháp lý chính thức.

**Latency:** 5.4365s total | Docs retrieved: 4 | Path: contextualize -> router -> retriever -> checker -> writer

| Node | Time (s) | % of Total |
|------|----------|------------|
| contextualize | 0.0000 | 0.0% |
| router | 1.0525 | 19.4% |
| retriever | 0.0370 | 0.7% |
| checker | 0.0003 | 0.0% |
| answer | 4.3413 | 79.9% |

**Retriever sub-steps:**

| Sub-Step | Time (s) |
|----------|----------|
| embedding | 0.0207 |
| qdrant_search | 0.0162 |
| filtering | 0.0001 |

---

## 5. Quick Comparison Table

| ID | Category | E2E (s) | Docs | Embed (s) | Qdrant (s) | Terminal | Question |
|----|----------|---------|------|-----------|------------|----------|----------|
| Q01 | penal | 9.4789 | 10 | 0.2230 | 0.0379 | writer | Tội giết người bị xử phạt như thế nào theo Bộ luật... |
| Q02 | civil | 12.8059 | 5 | 0.0291 | 0.0184 | writer | Quyền thừa kế theo pháp luật được quy định ra sao? |
| Q03 | business | 0.9779 | 0 | 0.0251 | 0.0171 | fallback | Phạm vi điều chỉnh của Luật Doanh nghiệp 2020 là g... |
| Q04 | marriage | 6.8210 | 4 | 0.0246 | 0.0263 | writer | Điều kiện kết hôn theo Luật Hôn nhân và Gia đình l... |
| Q05 | procedure | 6.8533 | 4 | 0.0270 | 0.0153 | writer | Thủ tục đăng ký thành lập doanh nghiệp gồm những b... |
| Q06 | penal | 4.1777 | 10 | 0.0235 | 0.0180 | clarifier | Tội trộm cắp tài sản có giá trị từ 50 triệu trở lê... |
| Q07 | civil | 10.2527 | 5 | 0.0296 | 0.0160 | writer | Hợp đồng dân sự vô hiệu trong trường hợp nào? |
| Q08 | business | 4.4585 | 2 | 0.0225 | 0.0176 | writer | Doanh nghiệp xã hội cần đáp ứng những tiêu chí gì? |
| Q09 | marriage | 7.8866 | 3 | 0.0244 | 0.0167 | writer | Quyền và nghĩa vụ của cha mẹ đối với con cái theo ... |
| Q10 | procedure | 5.4365 | 4 | 0.0207 | 0.0162 | writer | Quy trình giải quyết tranh chấp lao động cá nhân đ... |