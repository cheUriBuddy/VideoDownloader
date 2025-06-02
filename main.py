import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import subprocess
import threading
import os
import re
import platform
import webbrowser



# Validate URL
def is_valid_url(url):
    return re.match(r'^https?://', url) is not None

# Open folder
def open_folder(path):
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.run(["open", path])
        else:
            subprocess.run(["xdg-open", path])
    except Exception as e:
        messagebox.showerror("Error", f"Could not open folder:\n{e}")

# Toggle controls
def toggle_controls(state=tk.NORMAL):
    download_button.config(state=state)
    clear_button.config(state=state)
    browse_button.config(state=state)
    url_entry.config(state=state)
    audio_radio.config(state=state)
    video_radio.config(state=state)

# Theme toggle
def toggle_theme():
    is_light = root["bg"] == "#f5f5f5"
    
    bg = "#2d2d2d" if is_light else "#f5f5f5"
    fg = "#ffffff" if is_light else "#000000"
    accent = "#66d9ef" if is_light else "#0077cc"
    entry_bg = "#3c3f41" if is_light else "white"
    entry_fg = "#ffffff" if is_light else "black"
    log_bg = "#1e1e1e" if is_light else "white"
    log_fg = "#00ff99" if is_light else "black"

    root.configure(bg=bg)
    title_label.configure(bg=bg, fg=accent)
    progress_label.configure(bg=bg, fg=fg)

    for widget in root.winfo_children():
        if isinstance(widget, (tk.Label, tk.Radiobutton)):
            widget.configure(bg=bg, fg=fg)

    # Input fields
    url_entry.configure(bg=entry_bg, fg=entry_fg, insertbackground=entry_fg)
    folder_entry.configure(bg=entry_bg, fg=entry_fg, insertbackground=entry_fg)
    log_output.configure(bg=log_bg, fg=log_fg, insertbackground=log_fg)


# Download logic
def download_video():
    url = url_entry.get().strip()
    mode = format_var.get()
    folder = folder_path.get()

    log_output.delete(1.0, tk.END)
    progress_var.set(0)

    if not url:
        messagebox.showwarning("Missing URL", "Please enter a YouTube URL.")
        toggle_controls()
        return
    if not is_valid_url(url):
        messagebox.showerror("Invalid URL", "Please enter a valid URL starting with http or https.")
        toggle_controls()
        return
    if not folder:
        messagebox.showwarning("Missing Folder", "Please choose a download folder.")
        toggle_controls()
        return

    command = ["yt-dlp", url, "-P", folder]
    if mode == "audio":
        command += ["-x", "--audio-format", "mp3"]

    log_output.insert(tk.END, "Starting download...\n")

    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        for line in process.stdout:
            log_output.insert(tk.END, line)
            log_output.see(tk.END)
            match = re.search(r'\[download\]\s+(\d{1,3}\.\d)%', line)
            if match:
                percent = float(match.group(1))
                progress_var.set(percent)
                progress_label.config(text=f"{percent:.1f}%")


        process.wait()

        if process.returncode == 0:
            log_output.insert(tk.END, "\nDownload completed successfully.")
            response = messagebox.askyesno("Download Complete", "Download completed!\n\nOpen folder now?")
            if response:
                open_folder(folder)
            webbrowser.open_new_tab("https://www.youtube.com/@cheUriBuddy")
        else:
            log_output.insert(tk.END, "\nDownload failed.")
            messagebox.showerror("Failed", "Download failed.")
    except FileNotFoundError:
        messagebox.showerror("Error", "yt-dlp is not installed or not in system PATH.")
    finally:
        toggle_controls()

# Thread runner
def threaded_download():
    toggle_controls(tk.DISABLED)
    thread = threading.Thread(target=download_video)
    thread.start()

# Browse folder
def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_path.set(folder)

# Clear fields
def clear_fields():
    url_entry.delete(0, tk.END)
    folder_path.set("")
    log_output.delete(1.0, tk.END)
    progress_var.set(0)

# --- GUI Setup ---
root = tk.Tk()
root.title("cheUriBuddy's Video Downloader")
root.geometry("750x620")
root.configure(bg="#f5f5f5")
# root.iconbitmap("logo.ico")

default_font = ("Segoe UI", 11)
title_font = ("Segoe UI", 16, "bold")
root.option_add("*Font", default_font)

# Grid config
for i in range(3):
    root.grid_columnconfigure(i, weight=1)

# Title + Theme toggle
title_label = tk.Label(root, text="🎬 cheUriBuddy's Video Downloader", font=title_font, bg="#f5f5f5", fg="#0077cc")
title_label.grid(row=0, column=0, columnspan=2, pady=(15, 10), sticky="w", padx=20)
theme_btn = tk.Button(root, text="🌓 Toggle Theme", command=toggle_theme)
theme_btn.grid(row=0, column=2, sticky="e", padx=20)

# URL input
tk.Label(root, text="Any Video URL:", bg="#f5f5f5").grid(row=1, column=0, columnspan=3, sticky="w", padx=20)
url_entry = tk.Entry(root, width=80, relief="solid", borderwidth=1)
url_entry.grid(row=2, column=0, columnspan=3, padx=20, pady=5, sticky="ew")

# Format selection
tk.Label(root, text="Download Format:", bg="#f5f5f5").grid(row=3, column=0, sticky="w", padx=20)
format_var = tk.StringVar(value="video")
video_radio = tk.Radiobutton(root, text="Video", variable=format_var, value="video", bg="#f5f5f5")
audio_radio = tk.Radiobutton(root, text="Audio Only (mp3)", variable=format_var, value="audio", bg="#f5f5f5")
video_radio.grid(row=4, column=0, sticky="w", padx=20)
audio_radio.grid(row=4, column=1, sticky="w")

# Folder selector
tk.Label(root, text="Save To Folder:", bg="#f5f5f5").grid(row=5, column=0, columnspan=3, sticky="w", padx=20, pady=(10, 0))
folder_path = tk.StringVar()
folder_entry = tk.Entry(root, textvariable=folder_path, width=60, relief="solid", borderwidth=1)
folder_entry.grid(row=6, column=0, columnspan=2, padx=20, pady=5, sticky="ew")
browse_button = tk.Button(root, text="Browse", command=browse_folder, bg="#0077cc", fg="white", activebackground="#005fa3")
browse_button.grid(row=6, column=2, sticky="w", padx=5)

# Action buttons
download_button = tk.Button(root, text="⬇ Download", command=threaded_download, bg="#28a745", fg="white", activebackground="#218838")
download_button.grid(row=7, column=0, padx=20, pady=15, sticky="ew")
clear_button = tk.Button(root, text="🗑 Clear", command=clear_fields, bg="#dc3545", fg="white", activebackground="#c82333")
clear_button.grid(row=7, column=1, padx=10, pady=15, sticky="ew")

# Progress bar
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.grid(row=8, column=0, columnspan=3, padx=20, pady=(5, 0), sticky="ew")

# Percentage label
progress_label = tk.Label(root, text="0%", bg="#f5f5f5", fg="#000000")
progress_label.grid(row=9, column=0, columnspan=3, sticky="n", pady=(0, 10))


# Log area
tk.Label(root, text="Download Log:", bg="#f5f5f5").grid(row=9, column=0, columnspan=3, sticky="w", padx=20)
log_output = scrolledtext.ScrolledText(root, width=95, height=18, font=("Consolas", 10))
log_output.grid(row=10, column=0, columnspan=3, padx=20, pady=5, sticky="nsew")
root.grid_rowconfigure(10, weight=1)

# Run app
root.mainloop()
