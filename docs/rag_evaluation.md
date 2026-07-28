---

## 1. Tổng quan các Phương pháp Đánh giá RAG

Trong thực tế, có 4 nhóm phương pháp đánh giá RAG chính, từ đơn giản đến phức tạp:

### 1.1. Đánh giá dựa trên chuỗi văn bản (String-based Metrics)
Đây là phương pháp truyền thống, so sánh độ khớp về mặt ký tự giữa câu trả lời của AI và câu trả lời mẫu (Ground Truth).
- **BLEU / ROUGE / METEOR:** Thường dùng trong dịch thuật hoặc tóm tắt.
- **Ưu điểm:** Nhanh, rẻ, khách quan.
- **Nhược điểm:** Rất kém trong việc đánh giá "ý nghĩa". Một câu trả lời đúng về ý nhưng dùng từ khác (đồng nghĩa) vẫn bị chấm điểm thấp.

### 1.2. Đánh giá dựa trên Model (Model-based Evaluation)
Sử dụng một model khác để chấm điểm model hiện tại. Đây là xu hướng hiện nay.
- **Embedding Similarity:** Đo khoảng cách vector giữa câu trả lời và câu mẫu.
- **LLM-as-a-Judge (Dự án này sử dụng):** Dùng GPT-4o để đọc và chấm điểm dựa trên tiêu chí (Accuracy, Relevance...).
- **Ưu điểm:** Hiểu được ngữ nghĩa, cực kỳ linh hoạt.
- **Nhược điểm:** Tốn chi phí API, có thể bị thiên kiến (bias) theo model giám khảo.

### 1.3. Đánh giá dựa trên Framework chuyên dụng
Sử dụng các bộ công chỉ số được cộng đồng nghiên cứu đúc kết.
- **RAGAS / DeepEval:** Tự động tính toán các chỉ số như *Faithfulness*, *Context Precision*.
- **Ưu điểm:** Có chuẩn chung, dễ so sánh giữa các dự án.

### 1.4. Đánh giá bởi con người (Human Evaluation)
Đây vẫn được coi là "Gold Standard" (Tiêu chuẩn vàng).
- Người có chuyên môn (ví dụ: Luật sư) đọc và đánh giá trực tiếp.
- **Ưu điểm:** Độ tin cậy cao nhất.
- **Nhược điểm:** Rất chậm và cực kỳ tốn chi phí con người.

---

## 2. Kiến trúc Đánh giá trong dự án này (Evaluation Pipeline)

Dự án sử dụng một hệ thống đánh giá tự động hóa (Automated Evaluation Pipeline) được triển khai trong file `RUN_EVALUATION.py`. Quy trình này thực hiện qua các bước:

1.  **Test Dataset:** Sử dụng một bộ câu hỏi mẫu (`tests/evaluation_dataset.json`) có sẵn câu trả lời chuẩn (Ground Truth) và các tài liệu tham chiếu mong đợi.
2.  **Batch Execution:** Chạy thử nghiệm đồng loạt các câu hỏi qua hệ thống Chatbot thực tế.
3.  **LLM-as-a-Judge:** Sử dụng một mô hình LLM mạnh (như GPT-4o) để đóng vai trò "Giám khảo" đánh giá chất lượng câu trả lời dựa trên các tiêu chí định sẵn.
4.  **Reporting:** Xuất báo cáo dưới các định dạng JSON, CSV, HTML để theo dõi sự thay đổi chất lượng qua từng phiên bản code.

---

## 2. Các Chỉ số Đánh giá Chi tiết

Dự án tập trung vào hai nhóm chỉ số chính:

### 3.1. Chi tiết về các Chỉ số Retrieval (MRR & nDCG)

Trong dự án này, việc đánh giá Retriever không chỉ là "tìm thấy hay không" mà là "tìm thấy ở vị trí nào".

#### **A. MRR (Mean Reciprocal Rank)**
- **Khái niệm:** Đo lường vị trí của tài liệu liên quan **đầu tiên** được tìm thấy.
- **Công thức:** $MRR = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{rank_i}$
- **Ví dụ thực tế:**
    - Câu hỏi: "Mức phạt tội trộm cắp tài sản?"
    - Kết quả trả về: [Điều 101, Điều 173 (Đúng), Điều 155].
    - Tài liệu đúng nằm ở vị trí thứ 2 -> **Reciprocal Rank = 1/2 = 0.5**.
    - Nếu tài liệu đúng nằm ở vị trí thứ 1 -> **Score = 1.0**.

#### **B. nDCG (normalized Discounted Cumulative Gain)**
- **Khái niệm:** Đánh giá chất lượng của **toàn bộ danh sách** kết quả. Nó ưu tiên các tài liệu liên quan nằm ở top đầu.
- **Công thức DCG:** $DCG_k = \sum_{i=1}^{k} \frac{rel_i}{\log_2(i+1)}$
- **Công thức nDCG:** $nDCG_k = \frac{DCG_k}{IDCG_k}$ (Trong đó IDCG là giá trị DCG lý tưởng khi mọi tài liệu đúng đều nằm ở đầu).
- **Ví dụ thực tế:**
    - Bạn hỏi về "Thủ tục ly hôn". Hệ thống trả về 5 tài liệu.
    - Nếu 3 tài liệu quan trọng nhất nằm ở vị trí 1, 2, 3 -> nDCG xấp xỉ **1.0**.
    - Nếu 3 tài liệu đó bị đẩy xuống vị trí 3, 4, 5 -> nDCG sẽ **giảm mạnh** vì mẫu số $\log_2(i+1)$ tăng dần theo vị trí.

---

## 4. Trích xuất Code Evaluation (Mẫu)
Sử dụng phương pháp **LLM-as-a-Judge** để chấm điểm trên thang từ 1-5 cho các tiêu chí:

-   **Accuracy (Tính chính xác):** Câu trả lời có đúng với căn cứ pháp luật không? Có bị bịa đặt (hallucination) không?
-   **Completeness (Tính đầy đủ):** Đã trả lời hết các ý trong câu hỏi chưa? Có dẫn chiếu Điều, Khoản đầy đủ không?
-   **Relevance (Tính liên quan):** Câu trả lời có tập trung đúng vào vấn đề người dùng hỏi không? Có bị lan man không?

---

## 3. Trích xuất Code Evaluation (Mẫu)

Dưới đây là cách hệ thống tính toán và trình bày kết quả tóm tắt:

```python
# Trích xuất từ RUN_EVALUATION.py
def print_summary(batch_result, report):
    print(f"SYSTEM QUALITY: {report.overall_quality}")
    
    print(f"ANSWER GENERATION QUALITY")
    print(f"  Accuracy: {batch_result.avg_accuracy:.2f}/5")
    print(f"  Completeness: {batch_result.avg_completeness:.2f}/5")
    print(f"  Relevance: {batch_result.avg_relevance:.2f}/5")
    
    print(f"RETRIEVAL METRICS")
    print(f"  MRR: {batch_result.avg_mrr:.3f}")
    print(f"  nDCG: {batch_result.avg_ndcg:.3f}")
```

---

## 5. Mở rộng Kiến thức để Phỏng vấn

Khi phỏng vấn, bạn cần phân biệt rõ giữa **Phương pháp đánh giá** (Cách đo) và **Kỹ thuật cải tiến** (Thứ được đo).

### 5.1. Phân biệt Phương pháp đánh giá vs Kỹ thuật Retrieval
Đừng nhầm lẫn Hybrid Search là một cách đánh giá. 
- **Kỹ thuật Retrieval (Cái chúng ta tối ưu):** Hybrid Search (Vector + BM25), Reranking, Agentic RAG.
- **Phương pháp Đánh giá (Thước đo):** LLM-as-a-Judge, RAGAS Metrics, MRR/nDCG.

> **Ví dụ trả lời:** "Em dùng phương pháp **LLM-as-a-Judge** để đánh giá hiệu quả của kỹ thuật **Hybrid Search**. Kết quả cho thấy khi dùng Hybrid Search, chỉ số MRR của hệ thống tăng lên đáng kể."

### 5.2. Mối quan hệ giữa LLM-as-a-Judge và Framework (RAGAS)
- **LLM-as-a-Judge:** Là cơ chế cốt lõi (dùng LLM để chấm điểm).
- **RAGAS:** Là một công cụ (Tool) đóng gói sẵn các Prompt và công thức dựa trên cơ chế LLM-as-a-Judge để tính toán các chỉ số chuẩn như Faithfulness.

### 5.3. Khái niệm "RAG Triad" (Kiềng 3 chân của RAG)
Đây là khung lý thuyết quan trọng nhất để đánh giá một hệ thống RAG toàn diện:
1.  **Context Relevance:** Ngữ cảnh tìm được có thực sự liên quan đến câu hỏi không? (Đánh giá Retriever).
2.  **Groundedness (Faithfulness):** Câu trả lời có thực sự dựa trên ngữ cảnh đó không, hay do LLM tự bịa ra? (Đánh giá Hallucination).
3.  **Answer Relevance:** Câu trả lời cuối cùng có giải quyết đúng vấn đề người dùng hỏi không?

---

## 6. Hướng dẫn trả lời phỏng vấn về Evaluation

**Câu hỏi: Làm sao bạn biết Chatbot của bạn trả lời đúng hay sai?**
> *Trả lời:* "Em không đánh giá bằng cảm tính. Em xây dựng một **Evaluation Pipeline** tự động. Em chuẩn bị một bộ Test Dataset với các tình huống pháp lý thực tế. Sau đó, em sử dụng kỹ thuật **LLM-as-a-Judge** để chấm điểm câu trả lời dựa trên 3 tiêu chí: **Accuracy, Completeness và Relevance**. Đồng thời, em đo lường hiệu quả của bộ phận tìm kiếm bằng các chỉ số như **MRR và nDCG** để đảm bảo tài liệu luật luôn được lấy ra đúng nhất."

**Câu hỏi: Tại sao bạn không dùng các framework có sẵn như RAGAS?**
> *Trả lời:* "Việc tự xây dựng (Custom Pipeline) giúp em kiểm soát sâu hơn vào các tiêu chí đặc thù của ngành luật, ví dụ như việc kiểm tra dẫn chiếu Điều/Khoản chính xác. Tuy nhiên, em cũng nắm rõ các framework như **RAGAS** và hoàn toàn có thể tích hợp chúng để lấy các chỉ số như Faithfulness hay Context Precision nếu dự án yêu cầu mở rộng."
