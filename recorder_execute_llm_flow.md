# Recorder → LLM → Execute Flow Diagram

## Complete Integration Flow

```mermaid
flowchart TD
    subgraph Recording["📹 RECORDER COMPONENT"]
        R1[User Actions Captured]
        R2[DOM Elements Extracted]
        R3[Context Data Collected]
        R1 --> R2 --> R3
    end
    
    subgraph LLM["🤖 LLM/AI PROCESSING"]
        L1[GPT-4o Receives Recording]
        L2[Analyzes User Intent]
        L3[Generates Playwright Code]
        L4[Optimizes Locators]
        L5[Adds Error Handling]
        L1 --> L2 --> L3 --> L4 --> L5
    end
    
    subgraph AIElements["🧠 AI ELEMENTS"]
        A1[Self-Healing Logic]
        A2[Smart Wait Strategies]
        A3[Dynamic Locator Selection]
        A4[Failure Prediction]
    end
    
    subgraph Execution["🚀 EXECUTE COMPONENT"]
        E1[Load Generated Script]
        E2[Read Test Data]
        E3[Launch Parallel Browsers]
        E4[Execute Tests]
        E1 --> E2 --> E3 --> E4
    end
    
    subgraph Runtime["⚡ RUNTIME AI"]
        RT1{Locator Failed?}
        RT2[AI Finds Alternative]
        RT3[Update & Retry]
        RT1 -->|Yes| RT2 --> RT3
        RT1 -->|No| RT4[Continue]
    end
    
    Recording -->|Raw Data| L1
    L5 -->|Generated Script| E1
    L5 -.->|Embeds AI Logic| AIElements
    AIElements -.->|Injected Into| E1
    E4 --> RT1
    RT3 --> E4
    RT4 --> Results[📊 Results]
    
    style Recording fill:#E8F5E9,stroke:#4CAF50,stroke-width:3px
    style LLM fill:#E3F2FD,stroke:#2196F3,stroke-width:3px
    style AIElements fill:#FFF9C4,stroke:#FBC02D,stroke-width:3px
    style Execution fill:#FFF3E0,stroke:#FF9800,stroke-width:3px
    style Runtime fill:#F3E5F5,stroke:#9C27B0,stroke-width:3px
```

## Detailed Data Flow

```mermaid
sequenceDiagram
    participant User as 👤 User
    participant Recorder as 📹 Recorder
    participant LLM as 🤖 LLM (GPT-4o)
    participant AI as 🧠 AI Elements
    participant Executor as 🚀 Executor
    participant Browser as 🌐 Browser
    
    User->>Recorder: Performs manual workflow
    Recorder->>Recorder: Captures clicks, inputs, navigation
    Recorder->>Recorder: Extracts locators (id, class, xpath)
    Recorder->>LLM: Sends recording JSON
    
    Note over LLM: AI Processing Phase
    LLM->>LLM: Analyzes user intent
    LLM->>LLM: Generates Playwright code
    LLM->>LLM: Optimizes selectors
    LLM->>AI: Embeds self-healing logic
    LLM->>AI: Adds smart waits
    LLM->>Executor: Returns complete script
    
    User->>Executor: Triggers execution
    Executor->>Executor: Loads test data (Excel)
    Executor->>Browser: Launches parallel instances
    
    loop For Each Test Data Row
        Browser->>Browser: Execute test steps
        Browser->>AI: Check locator validity
        
        alt Locator Found
            AI->>Browser: Continue execution
        else Locator Failed
            AI->>AI: Find alternative locator
            AI->>Browser: Retry with new locator
        end
    end
    
    Browser->>Executor: Return results
    Executor->>User: Display dashboard
```

## Technical Architecture

```mermaid
graph LR
    subgraph Input["INPUT LAYER"]
        I1[User Actions]
        I2[DOM Snapshot]
        I3[Screenshots]
    end
    
    subgraph RecorderEngine["RECORDER ENGINE"]
        RE1[Event Listener]
        RE2[Element Inspector]
        RE3[Context Analyzer]
    end
    
    subgraph LLMLayer["LLM LAYER"]
        LL1[Prompt Engineering]
        LL2[GPT-4o API]
        LL3[Code Generation]
        LL4[Validation]
    end
    
    subgraph AILayer["AI INTELLIGENCE LAYER"]
        AL1[Locator Optimizer]
        AL2[Self-Healing Engine]
        AL3[Smart Retry Logic]
        AL4[Failure Predictor]
    end
    
    subgraph ExecutionEngine["EXECUTION ENGINE"]
        EE1[Script Loader]
        EE2[Data Manager]
        EE3[Browser Controller]
        EE4[Parallel Orchestrator]
    end
    
    subgraph Output["OUTPUT LAYER"]
        O1[Test Results]
        O2[Screenshots]
        O3[Traces]
        O4[Reports]
    end
    
    Input --> RecorderEngine
    RecorderEngine --> LLMLayer
    LLMLayer --> AILayer
    AILayer --> ExecutionEngine
    ExecutionEngine --> Output
    
    ExecutionEngine -.->|Runtime Feedback| AILayer
    
    style Input fill:#E8F5E9
    style RecorderEngine fill:#4CAF50,color:#fff
    style LLMLayer fill:#2196F3,color:#fff
    style AILayer fill:#FBC02D
    style ExecutionEngine fill:#FF9800,color:#fff
    style Output fill:#9C27B0,color:#fff
```

## Component Interaction Details

```mermaid
flowchart TD
    Start([User Records Workflow]) --> R[📹 RECORDER]
    
    R -->|Captures| D1[Click Events]
    R -->|Captures| D2[Input Values]
    R -->|Captures| D3[Navigation]
    R -->|Captures| D4[Assertions]
    
    D1 & D2 & D3 & D4 --> JSON[Recording JSON]
    
    JSON -->|Sent to| LLM[🤖 LLM API]
    
    LLM -->|Prompt| P1["Analyze this workflow:<br/>- User intent<br/>- Key actions<br/>- Data patterns"]
    
    P1 --> G1[Generate Playwright Code]
    
    G1 --> AI1[🧠 Inject AI: Self-Healing]
    AI1 --> AI2[🧠 Inject AI: Smart Waits]
    AI2 --> AI3[🧠 Inject AI: Retry Logic]
    
    AI3 --> Script[✅ Complete Test Script]
    
    Script --> E[🚀 EXECUTOR]
    
    E --> E1[Load Script]
    E --> E2[Load Data from Excel]
    E --> E3[Launch Browsers]
    
    E3 --> B1[Browser 1: ID=10005]
    E3 --> B2[Browser 2: ID=10003]
    E3 --> B3[Browser 3: ID=10007]
    
    B1 & B2 & B3 --> Run[Execute Test Steps]
    
    Run --> Check{AI Check:<br/>Element Found?}
    
    Check -->|No| Heal[🧠 AI Self-Heal:<br/>Find Alternative]
    Heal --> Retry[Retry Action]
    Retry --> Run
    
    Check -->|Yes| Continue[Continue]
    
    Continue --> Results[📊 Results Dashboard]
    
    style R fill:#4CAF50,color:#fff
    style LLM fill:#2196F3,color:#fff
    style AI1 fill:#FBC02D
    style AI2 fill:#FBC02D
    style AI3 fill:#FBC02D
    style E fill:#FF9800,color:#fff
    style Heal fill:#9C27B0,color:#fff
```

## Key Integration Points

### 1️⃣ Recorder → LLM
- **Data Sent**: User actions, DOM elements, context
- **Format**: JSON with timestamps and metadata
- **Trigger**: User clicks "Generate Script"

### 2️⃣ LLM → AI Elements
- **Process**: LLM generates code with embedded AI logic
- **AI Features Injected**:
  - Self-healing locator strategies
  - Smart wait conditions
  - Dynamic retry mechanisms
  - Error prediction patterns

### 3️⃣ AI Elements → Executor
- **Integration**: AI logic embedded in generated script
- **Runtime**: AI activates during execution failures
- **Feedback Loop**: Executor reports back to AI for learning

### 4️⃣ Executor → Runtime AI
- **Trigger**: Locator failure or timeout
- **Action**: AI finds alternative selectors
- **Result**: Auto-heals and continues execution

---

## Visualization in Mermaid Live Editor

Copy any diagram above to: **https://mermaid.live/**

## Color Legend
- 🟢 **Green**: Recording/Input
- 🔵 **Blue**: LLM Processing
- 🟡 **Yellow**: AI Intelligence
- 🟠 **Orange**: Execution
- 🟣 **Purple**: Self-Healing/Results
