# Use-case diagram (concise)

**Actor:** User. **Secondary systems:** Firestore, Google Tasks API, Google Calendar API.

```mermaid
flowchart TB
    User((User))

    subgraph SYS["System: Energy-Aware Task Assistant"]
        UC1[Plan day / workload estimate]
        UC2[Overload detection & guidance]
        UC3[In-app task CRUD]
        UC4[Google Tasks sync]
        UC5[Google Calendar events]
    end

    User --> UC1
    User --> UC2
    User --> UC3
    User --> UC4
    User --> UC5

    UC1 --> FS[(Firestore)]
    UC2 --> FS
    UC3 --> FS
    UC4 --> GT[Google Tasks API]
    UC5 --> GC[Google Calendar API]
```

**Note:** UC1–UC3 lean on Firestore for tasks and stats; UC4–UC5 call Google APIs after OAuth.
