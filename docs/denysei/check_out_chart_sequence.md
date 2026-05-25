```mermaid
sequenceDiagram
    participant T as Teacher Browser
    participant F as Flask Server
    participant DB as MySQL Database

    T->>F: GET /docent_home
    F->>DB: SELECT FLOOR((CASE feeling + energy + satisfaction_percentage) / 3) WHERE DATE(created_at) = CURDATE()
    DB-->>F: [{gemiddelde_score}, ...]
    F->>F: Pass checkout_data to template
    F-->>T: render docent_home.html met checkout_data
    T->>T: JSON.parse checkout_data
    T->>T: Chart.js rendert bar chart (1 bar per student, geen namen)
```