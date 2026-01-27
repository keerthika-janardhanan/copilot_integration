# Gen AI & LLM Integration Flow

## Where We Use Gen AI and LLMs

```mermaid
flowchart TD
    User[👤 User Records Workflow] --> Recorder[📹 Recorder]
    
    Recorder -->|Captured Actions| LLM1[🤖 LLM: GPT-4o<br/>Script Generation]
    
    LLM1 -->|Generates| Script[📝 Test Script]
    
    Script --> Execute[🚀 Execute Tests]
    
    Execute -->|Test Runs| Check{Failure?}
    
    Check -->|Yes| LLM2[🤖 LLM: GPT-4o<br/>Self-Healing]
    
    LLM2 -->|Fixes Locators| Execute
    
    Check -->|No| Results[✅ Results]
    
    style LLM1 fill:#2196F3,stroke:#1565C0,color:#fff,stroke-width:4px
    style LLM2 fill:#9C27B0,stroke:#6A1B9A,color:#fff,stroke-width:4px
    style Recorder fill:#4CAF50,stroke:#2E7D32,color:#fff
    style Execute fill:#FF9800,stroke:#E65100,color:#fff
```

## Two AI Integration Points

### 1️⃣ Recorder → LLM (Script Generation)
```mermaid
flowchart LR
    A[📹 Recorder<br/>Captures Actions] -->|JSON Data| B[🤖 GPT-4o<br/>Analyzes & Generates]
    B --> C[📝 Playwright Script]
    
    style B fill:#2196F3,stroke:#1565C0,color:#fff,stroke-width:3px
```

### 2️⃣ Execute → LLM (Self-Healing)
```mermaid
flowchart LR
    A[🚀 Executor<br/>Runs Tests] -->|Locator Failed| B[🤖 GPT-4o<br/>Finds Alternative]
    B --> C[✅ Auto-Fixed & Retried]
    
    style B fill:#9C27B0,stroke:#6A1B9A,color:#fff,stroke-width:3px
```

---

## View in Mermaid Live Editor
Copy any diagram above to: **https://mermaid.live/**
