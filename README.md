# ⚡ SpeedyFetch v1.2

> A high-performance, multi-threaded IDM-style file downloader built with Python, featuring a modern Tkinter GUI and HTTP Byte-Range request splitting.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://Status/Stable-brightgreen.svg)

**SpeedyFetch** is a lightweight yet powerful desktop download manager designed to accelerate file downloads by splitting files into concurrent chunks using HTTP Range requests.

---

## 🚀 Key Features

* **Multi-Threaded Download Engine:** Splits any downloadable file into multiple parallel parts to maximize bandwidth utilization.
* **HTTP Byte-Range Requests:** Uses custom `Range: bytes=start-end` headers to download specific file segments concurrently.
* **Smart Chunk Merging:** Automatically reassembles temporary part files (`.partN`) into the final clean binary file upon completion.
* **Modern Tkinter GUI:** Maximized responsive layout with real-time progress bars, speed metrics, and status trackers.
* **Dual Operation Mode:** Supports both a full graphical user interface (GUI) and a command-line interface (CLI) for automation.
* **Robust Error Handling:** Built-in SSL context management, custom User-Agent headers to prevent server blocking, and DNS/connection safeguards.

---

## 🛠️ Tech Stack

* **Language:** Python 3.x
* **GUI Framework:** Tkinter / ttk (Custom Styled Theme)
* **Networking:** `requests` library
* **Concurrency:** Python `threading` & `Locks` for thread-safe progress updates

---

## 📦 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/arundass-e/SpeedyFetch.git](https://github.com/arundass-e/SpeedyFetch.git)
   cd SpeedyFetch
