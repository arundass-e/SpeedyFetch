import argparse
import os
import threading
import tkinter as tk
from tkinter import messagebox, ttk
import requests


class SpeedyFetchApp:

  def __init__(self, root):
    self.root = root
    self.root.title("SpeedyFetch v1.2 - Multi-Threaded Downloader")

    # Maximized / Full Screen window state
    try:
      self.root.state("zoomed")
    except Exception:
      self.root.attributes("-zoomed", True)

    self.style = ttk.Style()
    self.style.theme_use("clam")

    # Main Container Frame
    main_frame = ttk.Frame(root, padding=30)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Title
    title_label = ttk.Label(
        main_frame,
        text="⚡ SpeedyFetch v1.2 (Requests Engine)",
        font=("Helvetica", 22, "bold"),
    )
    title_label.pack(pady=(0, 20))

    # Configuration Input Frame
    input_frame = ttk.LabelFrame(
        main_frame, text=" Download Configuration ", padding=15
    )
    input_frame.pack(fill=tk.X, pady=10)

    ttk.Label(input_frame, text="Target URL:", font=("Helvetica", 11)).grid(
        row=0, column=0, sticky=tk.W, pady=8
    )
    self.url_entry = ttk.Entry(input_frame, font=("Helvetica", 11))
    self.url_entry.grid(
        row=0, column=1, sticky=tk.EW, padx=10, pady=8, ipady=4
    )

    ttk.Label(input_frame, text="Threads:", font=("Helvetica", 11)).grid(
        row=1, column=0, sticky=tk.W, pady=8
    )
    self.threads_entry = ttk.Entry(input_frame, font=("Helvetica", 11), width=10)
    self.threads_entry.insert(0, "4")
    self.threads_entry.grid(
        row=1, column=1, sticky=tk.W, padx=10, pady=8, ipady=4
    )

    input_frame.columnconfigure(1, weight=1)

    self.download_btn = ttk.Button(
        input_frame, text="Start Download", command=self.start_download_thread
    )
    self.download_btn.grid(row=2, column=1, sticky=tk.E, padx=10, pady=10)

    # Progress & Status Frame
    progress_frame = ttk.LabelFrame(
        main_frame, text=" Download Progress & Status ", padding=20
    )
    progress_frame.pack(fill=tk.BOTH, expand=True, pady=15)

    self.progress_bar = ttk.Progressbar(
        progress_frame, orient="horizontal", mode="determinate", length=600
    )
    self.progress_bar.pack(fill=tk.X, pady=20)

    self.status_label = ttk.Label(
        progress_frame,
        text="Status: Ready to fetch...",
        font=("Helvetica", 11, "bold"),
    )
    self.status_label.pack(anchor=tk.W, pady=5)

    self.details_label = ttk.Label(
        progress_frame,
        text="Awaiting download task...",
        font=("Helvetica", 10),
        foreground="#555555",
    )
    self.details_label.pack(anchor=tk.W, pady=5)

  def start_download_thread(self):
    url = self.url_entry.get().strip()
    if not url:
      messagebox.showerror("Error", "Please enter a valid HTTP/HTTPS URL!")
      return

    if not url.startswith(("http://", "https://")):
      url = "https://" + url

    try:
      num_threads = int(self.threads_entry.get().strip())
      if num_threads <= 0:
        raise ValueError
    except ValueError:
      messagebox.showerror("Error", "Please enter a valid thread count!")
      return

    self.download_btn.config(state=tk.DISABLED)
    self.progress_bar["value"] = 0

    # Run background thread
    download_thread = threading.Thread(
        target=self.run_downloader_backend, args=(url, num_threads), daemon=True
    )
    download_thread.start()

  def run_downloader_backend(self, url, num_threads):
    try:
      self.update_ui_status("Connecting to server...", "Fetching file headers...")

      headers = {
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SpeedyFetch/1.2"
      }

      # 1. Fetch file size using requests safely
      try:
        head_res = requests.head(url, headers=headers, timeout=15)
        file_size = int(head_res.headers.get("Content-Length", 0))
      except Exception:
        # Fallback to GET stream if HEAD fails
        head_res = requests.get(url, headers=headers, stream=True, timeout=15)
        file_size = int(head_res.headers.get("Content-Length", 0))
        head_res.close()

      if file_size == 0:
        raise ValueError(
            "Cannot determine file size or server does not support"
            " Content-Length."
        )

      # Extract filename safely
      filename = url.split("/")[-1].split("?")[0]
      if not filename or "." not in filename:
        filename = "downloaded_file.bin"

      downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
      os.makedirs(downloads_dir, exist_ok=True)
      output_filename = os.path.join(downloads_dir, filename)

      self.update_ui_status(
          f"Downloading using {num_threads} threads...",
          f"Saving to: {output_filename}",
      )

      chunk_size = file_size // num_threads
      threads = []
      downloaded_bytes_lock = threading.Lock()
      total_downloaded = [0]

      def download_chunk(start_byte, end_byte, thread_id):
        chunk_headers = {
            "Range": f"bytes={start_byte}-{end_byte}",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SpeedyFetch/1.2"
            ),
        }
        part_filename = f"{output_filename}.part{thread_id}"
        try:
          with requests.get(
              url, headers=chunk_headers, stream=True, timeout=30
          ) as response:
            with open(part_filename, "wb") as f:
              for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                  f.write(chunk)
                  with downloaded_bytes_lock:
                    total_downloaded[0] += len(chunk)
                    current = total_downloaded[0]

                  percent = (current / file_size) * 100
                  mb_curr = current / (1024 * 1024)
                  mb_total = file_size / (1024 * 1024)

                  self.root.after(
                      0,
                      lambda p=percent: self.progress_bar.__setitem__("value", p),
                  )
                  self.update_ui_status(
                      f"Downloading... {percent:.1f}%",
                      f"Progress: {mb_curr:.2f} MB / {mb_total:.2f} MB",
                  )
        except Exception as e:
          print(f"Error in thread {thread_id}: {e}")

      # Start threads
      for i in range(num_threads):
        start = i * chunk_size
        end = (
            file_size - 1 if i == num_threads - 1 else (start + chunk_size - 1)
        )
        t = threading.Thread(
            target=download_chunk, args=(start, end, i), daemon=True
        )
        threads.append(t)
        t.start()

      for t in threads:
        t.join()

      # Merge chunk files
      self.update_ui_status("Merging chunks...", "Finalizing file...")
      with open(output_filename, "wb") as outfile:
        for i in range(num_threads):
          part_filename = f"{output_filename}.part{i}"
          if os.path.exists(part_filename):
            with open(part_filename, "rb") as infile:
              outfile.write(infile.read())
            os.remove(part_filename)

      self.root.after(
          0,
          lambda: messagebox.showinfo(
              "Success", f"File successfully downloaded and saved to:\n{output_filename}"
          ),
      )
      self.update_ui_status(
          "Download Complete! ✅", f"Saved at: {output_filename}"
      )

    except Exception as e:
      self.root.after(
          0, lambda: messagebox.showerror("Download Error", str(e))
      )
      self.update_ui_status("Download Failed ❌", str(e))
    finally:
      self.root.after(
          0, lambda: self.download_btn.config(state=tk.NORMAL)
      )

  def update_ui_status(self, status_text, details_text):
    self.root.after(
        0, lambda: self.status_label.config(text=f"Status: {status_text}")
    )
    self.root.after(
        0, lambda: self.details_label.config(text=details_text)
    )


if __name__ == "__main__":
  import sys

  if len(sys.argv) > 1:
    parser = argparse.ArgumentParser(
        description="SpeedyFetch Multi-threaded Downloader"
    )
    parser.add_argument("url", help="URL input")
    parser.add_argument("-o", "--output", required=True, help="Output file")
    parser.add_argument("-t", "--threads", type=int, default=4, help="Threads")
    args = parser.parse_args()
  else:
    root = tk.Tk()
    app = SpeedyFetchApp(root)
    root.mainloop()