# AutoDash: private AI dashboards from any data file

Drop in a CSV or Excel file and get a polished, interactive dashboard in seconds.
**The AI never sees your data.** It only gets column names and types, plans the dashboard,
and every number is calculated on your own computer.

```
your file ──► profile (names + types only) ──► AI plans KPIs & charts (JSON)
    │                                                   │
    └──────────────► pandas calculates locally ◄────────┘
                               │
                     dashboard.html (opens in your browser)
```

## Quick start
```bash
pip install -r requirements.txt
python autodash.py sample/shipments.csv
python autodash.py my_data.xlsx --title "Ops review"
```
Your browser opens with the dashboard. The HTML file is saved next to the data file as shipments_dashboard.html.

## Preview

<img width="1570" height="892" alt="Dash Board -1" src="https://github.com/user-attachments/assets/b4fce11a-da4b-4455-8cad-a6db9f2d0e83" />
<img width="1623" height="790" alt="Dash Board -2" src="https://github.com/user-attachments/assets/624a0afa-daee-47c2-b4e5-bd5da1747bf4" />
<img width="1601" height="564" alt="Dash Board -3" src="https://github.com/user-attachments/assets/c5f0c15d-abed-4925-8738-0e085c511545" />


## Privacy options
| Mode | What leaves your computer |
|---|---|
| `--no-ai` | Nothing. |
| Default | Column names, their type, how many different values each has, and a rough size range ("1,000–10,000 rows"). **No actual values.** |
| `--share-categories` | The above, plus the labels of very short lists (6 options or fewer), like `Mode: Air, Ocean, Road`. Anything that looks like a person or company (Customer, Supplier, Email, Phone, Address…) is never shared. |
| `--show-ai-request` | Prints exactly what would be sent, then stops. Nothing is sent. |

Every time AutoDash talks to an AI, it saves the exact request as a .ai_request.json file next to the dashboard. You can open it and check what was sent.


## Project layout
```
autodash.py            command line entry point
autodash/profile.py    reads the file, detects types, builds the AI-safe schema
autodash/planner.py    AI planner (JSON schema) + rules fallback
autodash/compute.py    validates the plan and calculates everything with pandas
autodash/render.py     builds the HTML dashboard (SVG charts, no external libraries)
autodash/llm.py        Groq / Claude / Gemini client
sample/shipments.csv   made-up freight data to try it with
```

## Taking it further
 
AutoDash works on its own, but it gets more useful when it's part of a bigger setup. Here are the two directions I'd take it next.
 
### 1. Automate it with n8n
 
Right now you run AutoDash by hand. With n8n, it can run by itself whenever new data turns up.
 
**Idea A: a new file arrives → a dashboard appears**
```
Google Drive / OneDrive trigger ("new file in /reports")
   → download the file
   → Execute Command node: python autodash.py <file> --no-open
   → email or Slack the dashboard to the team
```
 
**Idea B: a weekly report, every Monday**
```
Schedule trigger (Mon 9:00)
   → export last week's data from the database or Google Sheet
   → run AutoDash
   → email the HTML (or a PDF) to the manager
```
 
**Idea C: a small upload page**
Wrap AutoDash in a tiny API (FastAPI) and call it from an n8n webhook or form. Anyone on the team can upload a file and get a dashboard back, without touching Python.
 
A few practical notes:
- The **Execute Command** node only works when n8n is self-hosted on the same machine as AutoDash, not on n8n Cloud.
- Use `--no-ai` in scheduled runs if the data is sensitive and nobody is around to check what's being sent.
- Keep the `.env` file with the API key on the server only, never inside the n8n workflow itself.
### 2. Move it into Power BI (Pro / Premium / Fabric)
 
The HTML dashboard is great for quick looks, but many companies live in Power BI. This is how AutoDash could plug in:
 
**Step 1: generate a Power BI starter pack (no special licence needed)**
AutoDash already knows which numbers matter. The same plan can be turned into:
- **DAX measures** written with your real column names, ready to paste
- a **layout guide** saying which visual goes where
- a **theme file** so the report matches the HTML version
**Step 2: generate the report itself (Power BI Projects / PBIP)**
Power BI can now save reports as plain text files (the PBIP format). That means a script can *write* a report. AutoDash could output a PBIP folder that opens in Power BI Desktop with the pages already built. This is the most exciting option, but it's also the newest and least battle-tested part of Power BI, so expect some trial and error.
 
**Step 3: what Premium / Fabric capacity adds**
With a company Fabric or Premium capacity, a few extra things open up:
- **Copilot in Power BI** can draft and refine report pages from a prompt. It's a nice companion to the AutoDash plan.
- **Scheduled and automatic refresh**, so the report updates whenever the data does.
- **Fabric notebooks** can run Python inside the Microsoft environment. The AutoDash logic could run there, right next to the company data.
- **Deployment pipelines** let you move reports from test to production in a controlled way.
The privacy idea stays the same throughout: the AI designs, the company's own systems calculate.


## Known limits
 
- The AI plans from column **names**. Clear names (`RevenueINR`, `DeliveryDate`) give much better dashboards than vague ones (`Amt`, `Col7`).
- It makes one dashboard page. Multi-page reports would be a good next feature.
- Very large files (millions of rows) will work, but slowly. A database connection would be the next step for that.
- The output is HTML, not a Power BI file, yet. See "Taking it further" above.

## Why I built it this way
 
I wanted something a company could actually say yes to. "Upload your data to our AI" is a hard sell. "The AI only ever sees your column headers, and here's the exact file it was sent" is a much easier conversation.
