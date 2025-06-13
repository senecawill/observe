# **Software Specification: Local LLM Code Search with Regex-Based Indexing**

## **1. Overview**

This is a standalone Flask-based application that performs regex-based searches over a local codebase (including documentation) and provides context for an OpenAI-compatible LLM. The tool supports:

- Searching **all text/code files** in a repository (C++, Python, Markdown, etc.).
- Automatic traversal of **all subdirectories**, respecting `.chatignore` files for exclusions.
- A **Flask-based API** that receives LLM-style web requests and dynamically fetches relevant code snippets.
- **On-demand searches** with no caching.
- Configuration via a **simple `.ini` file**.
- **Results automatically formatted** and injected as context into LLM queries.

---

## **2. System Architecture**

### **2.1 Components**

- **Flask Web Server**: Handles API requests in an OpenAI-compatible format.
- **Regex Search Engine**: Performs on-demand searches across the codebase.
- **File Scanner**: Recursively scans all relevant files while respecting `.chatignore`.
- **INI Configuration Loader**: Loads settings from a config file.
- **Context Preparer**: Formats retrieved code snippets for the LLM.

### **2.2 Directory Structure**

```
/code-search-llm
│── main.py               # Flask application entry point
│── config.ini            # User-defined settings
│── search_engine.py      # Regex-based search logic
│── file_scanner.py       # Handles file traversal & .chatignore parsing
│── llm_connector.py      # Prepares context & interfaces with the LLM
│── requirements.txt      # Dependencies
│── README.md             # Documentation
```

---

## **3. Configuration**

Settings are managed in a `.ini` file:

### **Example `config.ini`**

```ini
[General]
codebase_root = /path/to/repository     # Root directory for scanning
llm_api_url = http://127.0.0.1:8000/v1  # OpenAI-compatible LLM endpoint

[Search]
ignore_patterns = *.log, *.bin, __pycache__  # Patterns to ignore (global)
max_results = 10                              # Limit search results per query

[ChatIgnore]
use_chatignore = true  # Enable or disable .chatignore support
```

---

## **4. Features**

### **4.1 Regex-Based Search**

✅ **Searches all text-based files** within the project directory.  
✅ Supports **complex regex patterns** for advanced matching.  
✅ Retrieves **matching lines + context (e.g., function names, comments, or surrounding code)**.  
✅ Ignores **binary files and non-text files automatically**.  
✅ **Exclusion via `.chatignore`** at both project and subdirectory levels.

### **4.2 `.chatignore` Support**

✅ Users can create a `.chatignore` file in any directory.  
✅ Uses a **`.gitignore`-like syntax** for excluding specific files/folders.  
✅ Example `.chatignore`:

```
# Ignore all log files
*.log
# Ignore third-party libraries
/vendor/
# Ignore specific files
secrets.py
```

### **4.3 OpenAI-Compatible API**

✅ **Flask-based API** mimicking OpenAI requests.  
✅ Accepts user queries (e.g., “Where is the authentication logic implemented?”).  
✅ **Performs a regex search** and retrieves relevant context.  
✅ Injects retrieved snippets into the LLM request **before forwarding it to the configured LLM**.  
✅ Supports **multiple file results** as context.

### **4.4 Automatic Context Injection for LLM**

✅ **Dynamically constructs context** from regex search results.  
✅ **Formats snippets for clarity**, including file paths, function names, and surrounding comments.  
✅ **Limits result length** to avoid overloading the LLM.

---

## **5. API Endpoints**

### **5.1 Search & LLM Request (`/v1/chat/completions`)**

#### **Request**

```json
{
  "model": "local-llm",
  "messages": [
    {"role": "user", "content": "Where is user authentication handled?"}
  ]
}
```

#### **Processing**

1. Extracts user query.
2. Performs a **regex search** across the codebase.
3. Retrieves **matching snippets** with surrounding context.
4. Reformats results into structured LLM-friendly input.
5. **Calls the LLM API** with the query + code snippets.

#### **Response**

```json
{
  "id": "chat-xyz",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "User authentication is handled in `auth.py` inside the `authenticate_user` function."
      }
    }
  ]
}
```

---

## **6. Implementation Details**

### **6.1 File Scanner (`file_scanner.py`)**

- Recursively scans `codebase_root`, filtering ignored files via `.chatignore` and `ignore_patterns`.
- Returns a **list of files** to be searched.

### **6.2 Regex Search Engine (`search_engine.py`)**

- Reads each file **line-by-line**, applying regex matching.
- Returns **filename, line number, and matched content**.

### **6.3 LLM Connector (`llm_connector.py`)**

- Collects **search results**.
- Constructs an LLM-friendly **context block**.
- Sends **final query** to the **OpenAI-compatible LLM API**.

---

## **7. Installation & Usage**

### **7.1 Installation**

```bash
git clone https://github.com/your-repo/code-search-llm.git
cd code-search-llm
pip install -r requirements.txt
```

### **7.2 Running the Server**

```bash
python main.py
```

### **7.3 Testing with cURL**

```bash
curl -X POST "http://127.0.0.1:5000/v1/chat/completions" -H "Content-Type: application/json" \
-d '{"model": "local-llm", "messages": [{"role": "user", "content": "Where is user authentication handled?"}]}'
```

---

## **8. Future Enhancements**

✅ **Parallelized search for speed improvements**.  
✅ **Caching of recent queries to avoid redundant processing**.  
✅ **Hybrid search (regex + embeddings) for smarter retrieval**.  
✅ **Fine-tuned ranking of search results** based on file relevance.

---

## **9. Summary**

|Feature|Status|
|---|---|
|**Flask-based API**|✅ Done|
|**Regex Code Search**|✅ Done|
|**.chatignore Support**|✅ Done|
|**Dynamic LLM Context**|✅ Done|
|**Configuration via INI**|✅ Done|
|**Multi-threading**|🔜 Future|
|**Hybrid Search (Embeddings)**|🔜 Future|

---

### **Next Steps**

- ✅ Implement `file_scanner.py` to traverse directories and apply `.chatignore` rules.
- ✅ Develop `search_engine.py` to perform regex-based searches efficiently.
- ✅ Build `llm_connector.py` to format search results and inject them into LLM queries.
- ✅ Develop `main.py` to expose the Flask API.

---

This specification provides a **lightweight yet extensible** approach to **code-aware LLM interaction** using regex-based search. 🚀

Would you like me to generate the initial Python implementation? 🎯