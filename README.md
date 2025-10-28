# IEEE Reference Extractor — Step-by-Step Guide

## 1) What this app does (in one minute)

The IEEE Reference Extractor takes academic PDFs, finds the **References** section, parses each entry into structured data (authors, title, year, venue, pages, DOI/URL, etc.), optionally **enriches** it via CrossRef/DOI APIs, and exports the cleaned results to **BibTeX, RIS, JSON, or CSV**. It comes with a modern **PySide6 GUI**, background worker threads with progress signals, and a rotating **enterprise logging** system. 

---

## 2) Quick start (run it now)

1. **Install prerequisites**

   * Python 3.10+ and system packages for PyMuPDF (`fitz`) and PySide6.
   * Recommended: a virtualenv.

2. **Install Python deps**

   ```bash
   pip install -r requirements.txt
   ```

   (Ensure packages like `PySide6`, `PyMuPDF`, `qt-material`, `requests` are present.)

3. **Launch the app**

   ```bash
   python main.py
   ```

   The entry point sets up config, logging, theme, and shows the main window. 

4. **Choose folders in the UI**

   * Click **Input** → select a folder containing PDFs.
   * Click **Output** → select an export folder.
   * The GUI verifies you’re ready and shows how many PDFs it found.  

5. **Pick output format & options**

   * Choose **BibTeX / RIS / JSON / CSV** from the format dropdown.
   * Toggle ML parsing + API enrichment as needed. 

6. **Start**

   * Click **Start**. Processing runs in a background thread; the UI shows progress per PDF and logs.  

7. **Finish**

   * A completion dialog summarizes totals; you can open the output folder directly. 

---

## 3) The processing pipeline (step by step)

### Step A — Column-aware text extraction from PDF

* A **PDFProcessor** reads each PDF, extracts text with column awareness (left → right columns), and detects the **REFERENCES** section boundaries using multiple headings (REFERENCES/REFERENCE/BIBLIOGRAPHY/WORKS CITED) and the next section markers (APPENDIX/ACKNOWLEDGMENT). It returns just the references text.   

### Step B — ML-assisted reference parsing

* **ReferenceParser** cleans/normalizes text, splits it into entries using heuristics for numbered styles (`[1]`, `1.`), author–year, and line-based fallbacks.  
* For each entry it extracts DOI/URL, quoted **title**, **year**, **authors** (before the title), and venue details (**journal/booktitle**, **volume/issue/pages**). It also determines a **citation type** (article/inproceedings/book/etc.) and computes a **confidence** score, then removes near-duplicate records via title similarity.    

### Step C — Metadata enrichment (optional)

* If enabled, **MetadataEnricher** tries:

  1. **DOI** resolution (preferred): resolve DOI via `doi.org` and map CSL fields to authors/year/venue/ISSN/etc. 
  2. **CrossRef**: either `lookup_by_doi` or `search_by_title` with a rate-limited client.  
     The enricher merges results and tags which source enriched the record.   

### Step D — Export to your chosen formats

* **ExportManager** orchestrates **BibTeX/RIS/JSON/CSV** exporters and can write multiple formats at once.  
* **BibTeX** entries respect entry type, author/title/venue/pages/year/DOI/URL and include a note with the confidence score. Citation keys are generated from last author + year.   
* **RIS** emits standard tags (AU/TI/JO/VL/IS/SP/EP/DO/UR/KW).  
* **JSON/CSV** contain full normalized fields and simple metadata (export time, version).  

### Step E — Save to the app database (SQLite)

* References can be inserted one-by-one or in **bulk** with created/updated timestamps; you can list, search, update, and delete them as needed.     

---

## 4) How the GUI, workers, and logging fit together

### The GUI (MainWindow)

* Provides inputs/outputs pickers, options (style, format, ML parsing, enrichment), real-time logs, and a stats view (counts, average confidence, by-year/type breakdowns). It also includes an “About” dialog listing key features.    

### Worker threads

* The **WorkerManager** creates a `QThread`, moves an **ExtractionWorker** into it, and wires signals: progress/logs/PDF-completed/finished/error. The worker processes PDFs sequentially, emits UI-friendly updates, and totals reference counts. Cancellation is supported.   

### Enterprise logging

* A central **LoggerManager** configures colored console output, rotating file logs (main, error, daily), and a **Qt signal handler** so the GUI shows live logs—useful for troubleshooting and audit.  

---

## 5) Configuration & theming

* The app creates standard directories (`config`, `data`, `logs`, `cache`, `Output`) at startup. It loads configuration, validates fields (e.g., export format, citation style, log level ranges), sets log level, and applies the selected `qt-material` theme.   
* You can update config keys (paths, thresholds, style) programmatically; validation covers ranges (workers, similarity/confidence thresholds), paths, and allowed enums.  

---

## 6) Operational tips & troubleshooting

* **No PDFs detected?** The GUI disables Start until input/output are set and at least one `*.pdf` exists in the folder. 
* **Want multiple outputs?** Use `ExportManager.export_multiple_formats()` to emit `.bib`, `.ris`, `.json`, and `.csv` together. 
* **Performance:** Parsing runs in a background thread and emits granular progress so the UI stays responsive even with many PDFs. 
* **Auditability:** Check the rotating logs; the logger initializes multiple handlers and a Qt signal bridge for real-time log streaming into the GUI.  

---

## 7) End-to-end flow (at a glance)

1. **Load config + logger + UI** → apply theme, show window. 
2. **User selects folders & options** → GUI validates readiness. 
3. **Start** → Worker thread kicks off; for each PDF:

   * Extract column-aware text → find **References**. 
   * Parse/normalize entries; deduplicate. 
   * (Optional) Enrich via DOI/CrossRef.  
   * Export to the chosen format(s). 
   * Save to SQLite and update live stats/logs. 
4. **Finish dialog** with totals and quick link to the output folder. 

---

## 8) (Optional) Hardening & reliability pointers

* **Rate limiting:** CrossRef calls are gated by a simple rate-limiter to avoid 429s. 
* **Resilience:** Worker emits error signals; GUI surfaces them and keeps logs with rotation/backups.  
* **Validation:** Config validator guards formats/styles/levels/ranges for safer operation. 

---

