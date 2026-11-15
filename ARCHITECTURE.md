# Final system architecture (V5)

```mermaid
flowchart TD
    U[User: text or microphone] --> B[Browser UI: HTML CSS JavaScript]
    B -->|SpeechRecognition transcript| B
    B -->|POST /api/chat| F[Flask application]
    F --> N[LLM NLU if configured; otherwise rule NLU]
    N --> V[Validate intent and entities; resolve person against dataset]
    V --> D[Dialogue state and clarification]
    D --> Q[Query service: Pandas filters]
    Q --> X[(people.xlsx: factual source of truth)]
    X --> Q --> R[Grounded response text]
    R --> B
    B -->|SpeechSynthesis, optional| U
```

**Version evolution:** V1 Browser → Flask → deterministic rules → Pandas → Excel; V2 adds explicit intent/entity parsing and query-service separation; V3 adds dialogue state and clarification; V4 uses an LLM only as an NLU parser followed by validation and grounded spreadsheet lookup; V5 adds speech recognition and synthesis around the same backend.
