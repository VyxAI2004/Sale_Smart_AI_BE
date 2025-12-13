---
description: Tài liệu tích hợp Frontend cho hệ thống AI Assistant Chatbot (Global, Project, Product)
---

# 🤖 AI Assistant & Chatbot API Guide

Tài liệu này hướng dẫn Frontend Developer tích hợp hệ thống Chatbot đa năng (Multi-Context AI).

## 1. Tổng Quan (Concepts)

Hệ thống Chatbot hỗ trợ 3 ngữ cảnh làm việc (Contexts):

1.  **Global Chat**: Trợ lý ảo chung, hỏi đáp kiến thức eCommerce, Marketing (không gắn với dự án/sản phẩm cụ thể).
2.  **Project Chat**: Tư vấn chiến lược dựa trên thông tin **Dự Án** (Target Audience, Budget, Goals...).
3.  **Product Chat**: Phân tích sâu về **Sản Phẩm** (Dựa trên Specs, Reviews, Market Analysis).

Mỗi cuộc hội thoại là một **Session** được lưu trữ vĩnh viễn (Persistent) và gắn liền với User.

---

## 2. API Endpoints Chính

Base URL: `/api/v1`

### A. Gửi Tin Nhắn (Chat Core)

Dùng để gửi câu hỏi và nhận câu trả lời từ AI. API này xử lý thông minh dựa trên params bạn gửi.

*   **Endpoint**: `POST /assistant/chat`
*   **Content-Type**: `application/json`

**Các trường hợp sử dụng (Use Cases):**

#### 1. Tạo cuộc trò chuyện mới (Chat Global/General)
Dùng khi User bấm nút "New Chat" ở trang chủ hoặc Dashboard.

```json
// Request
{
  "query": "Làm thế nào để tối ưu SEO cho shop thời trang?",
  "session_id": null,   // Quan trọng: Để null để tạo session mới
  "project_id": null
}
```

#### 2. Chat trong ngữ cảnh Dự Án (Project Context)
Dùng khi User đang ở trang **Project Detail** và muốn hỏi về dự án đó.

```json
// Request
{
  "query": "Với ngân sách này thì nên chạy quảng cáo kênh nào?",
  "project_id": "uuid-cua-project-hien-tai", // Gửi ID dự án
  "session_id": null // Hoặc ID cũ nếu đang chat tiếp
}
```

#### 3. Tiếp tục cuộc trò chuyện (Chat Continuing)
Dùng khi User đang chat dở một session nào đó (bất kể Global hay Project).

```json
// Request
{
  "query": "Giải thích rõ hơn ý trên đi",
  "session_id": "uuid-cua-session-dang-chat" // Lấy từ response trước đó
}
```

**Response Mẫu:**
```json
{
  "answer": "Dựa trên ngân sách 50 triệu của dự án X, bạn nên...",
  "session_id": "uuid-session-vua-dung", // Lưu lại ID này cho request sau
  "sources": ["Project Info", "General Knowledge"]
}
```

### A2. Gửi Tin Nhắn (Streaming - Recommended)

Để đạt hiệu ứng "gõ chữ" mượt mà (Typewriter effect), hãy dùng API Stream.

*   **Endpoint**: `POST /assistant/chat/stream`
*   **Response Content-Type**: `application/x-ndjson`
*   **Cách xử lý (Frontend)**: Đọc stream từng dòng. Mỗi dòng là một JSON object.

**Stream Format:**
```json
{"session_id": "uuid-...", "text": ""} // Chunk đầu tiên chứa Session ID
{"session_id": "uuid-...", "text": "Chào"}
{"session_id": "uuid-...", "text": " bạn"}
...
```

---

### B. Quản Lý Lịch Sử (Sidebar / History List)

Dùng để hiển thị danh sách các cuộc hội thoại cũ (giống Sidebar của ChatGPT).

**1. Lấy danh sách Sessions:**
*   **Endpoint**: `GET /assistant/sessions`
*   **Response**: Mảng các sessions, sắp xếp theo thời gian update mới nhất.
    ```json
    [
      {
        "id": "uuid-1",
        "title": "Chiến lược SEO thời trang...",
        "session_type": "global", // 'global', 'project_consult', 'product_consult'
        "updated_at": "2025-12-13T14:00:00"
      },
      ...
    ]
    ```

**2. Lấy nội dung chi tiết 1 Session:**
Khi user click vào một mục trong Sidebar.
*   **Endpoint**: `GET /assistant/sessions/{session_id}`
*   **Response**: Chi tiết tin nhắn.
    ```json
    {
      "id": "uuid-1",
      "messages": [
        {"role": "user", "content": "Hello"},
        {"role": "ai", "content": "Chào bạn..."}
      ]
    }
    ```

---

### C. Product Consultant (Product Specific)

Dành riêng cho trang **Chi tiết sản phẩm (Product Detail)**.
Mặc dù API `/assistant/chat` cũng hỗ trợ, nhưng khuyến khích dùng API riêng này để đảm bảo ngữ cảnh sâu nhất (bao gồm cả phân tích thị trường AI).

*   **Endpoint**: `POST /products/{product_id}/market/consult`
*   **Payload**:
    ```json
    {
      "query": "Sản phẩm này giá có đắt không?",
      "session_id": "..." // Optional
    }
    ```

---

## 3. Frontend Implementation Flows

### Flow 1: Global Chat Page
1.  **On Load**: Gọi `GET /assistant/sessions` → Render Sidebar.
2.  **Click New Chat**:
    *   Clear khung chat.
    *   Set biến `currentSessionId = null`.
3.  **User Send Message**:
    *   Gọi `POST /assistant/chat` với `session_id: currentSessionId`.
    *   Nhận Response → Hiển thị tin nhắn AI.
    *   Update `currentSessionId = response.data.session_id`.
    *   Gọi lại `GET /sessions` để update Sidebar (hoặc push session mới vào sidebar thủ công).

### Flow 2: Project Detail Page
1.  User vào trang Project A.
2.  Hiển thị nút "Ask AI about Project".
3.  Khi bấm nút → Mở chat box.
4.  User hỏi → Gọi `POST /assistant/chat` với `project_id: ProjectA.id`.

---

## 4. Technical Implementation Guide (For Frontend Devs)

Để đạt trải nghiệm "Chatbot hoàn hảo" (mượt mà như ChatGPT), chúng ta sử dụng kỹ thuật **Streaming Response** với định dạng **NDJSON (Newline Delimited JSON)**.

### Tại sao không dùng WebSocket?
*   **Simplicity**: Streaming qua HTTP (SSE/NDJSON) đơn giản hơn, không cần quản lý connection state phức tạp như WebSocket s(reconnect, heartbeat...).
*   **Firewall Friendly**: Chạy trên HTTP/HTTPS chuẩn, không bị chặn bởi firewall công ty.
*   **Fit for Purpose**: Chúng ta chỉ cần server đẩy text về client (One-way streaming during generation), không cần giao tiếp 2 chiều thời gian thực liên tục (như Game).

### Hướng dẫn xử lý Stream (Javascript Example)

Sử dụng `fetch` API và `ReadableStreamDefaultReader` để đọc dữ liệu từng chunk.

```javascript
async function chatStream(query, sessionId, projectId) {
    const response = await fetch('/api/v1/assistant/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            query: query, 
            session_id: sessionId,
            project_id: projectId 
        })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let currentSessionId = sessionId;

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        // Decode chunk bytes to text
        const chunkText = decoder.decode(value);
        
        // NDJSON: Mỗi dòng là một JSON object. Cần tách dòng vì một chunk có thể chứa nhiều dòng.
        const lines = chunkText.split('\n');
        
        for (const line of lines) {
            if (!line.trim()) continue;
            try {
                const data = JSON.parse(line);
                
                // 1. Cập nhật Session ID (nếu chưa có)
                if (data.session_id) {
                    currentSessionId = data.session_id;
                    // Save to State if needed
                }
                
                // 2. Append Text vào UI
                if (data.text) {
                    // appendToMessageUI(data.text);
                    console.log("Chunk:", data.text);
                }
            } catch (e) {
                console.warn("Parse error", e);
            }
        }
    }
    
    return currentSessionId;
}
```
