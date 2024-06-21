import subprocess
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pytube import YouTube


def download_video_from_youtube(url, output_path):
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        stream.download(output_path=output_path)
        return os.path.join(output_path, stream.default_filename)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to download video: {e}")
        return None


def get_video_duration(video_file):
    duration_cmd = [
        'ffprobe', '-v', 'error', '-show_entries',
        'format=duration', '-of',
        'default=noprint_wrappers=1:nokey=1', video_file
    ]
    duration_output = subprocess.run(duration_cmd, stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
    try:
        return float(duration_output)
    except ValueError:
        messagebox.showerror("Error", "Could not get video duration")
        return None


def generate_clips(video_file, output_dir, chunk_duration, scale, format, progress):
    duration_seconds = get_video_duration(video_file)
    if duration_seconds is None:
        return

    num_chunks = int(duration_seconds / chunk_duration)
    progress["maximum"] = num_chunks

    for i in range(num_chunks):
        start_time = i * chunk_duration
        output_file = os.path.join(output_dir, f"chunk_{i:03d}.{format}")

        if format == 'gif':
            cmd = [
                'ffmpeg', '-ss', str(start_time), '-t', str(chunk_duration),
                '-i', video_file, '-vf', f'scale={scale}', output_file
            ]
        else:  # mp4 format
            cmd = [
                'ffmpeg', '-ss', str(start_time), '-t', str(chunk_duration),
                '-i', video_file, '-vf', f'scale={scale}', '-c:a', 'copy', output_file
            ]

        subprocess.run(cmd)
        print(f"Generated {format.upper()} {output_file}")
        progress["value"] += 1
        root.update_idletasks()

    messagebox.showinfo("Success", f"Generated {num_chunks} clips")


def browse_file(entry):
    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mkv")])
    if file_path:
        entry.delete(0, tk.END)
        entry.insert(0, file_path)


def browse_directory(entry):
    directory_path = filedialog.askdirectory()
    if directory_path:
        entry.delete(0, tk.END)
        entry.insert(0, directory_path)


def on_generate():
    youtube_url = youtube_url_entry.get()
    local_video_file = local_video_file_entry.get()
    output_dir = output_dir_entry.get()
    chunk_duration = int(chunk_duration_entry.get())
    scale = scale_entry.get()
    format = format_var.get()

    if youtube_url:
        # Download the video from YouTube
        print("Downloading video...")
        video_file = download_video_from_youtube(youtube_url, output_dir)
        if not video_file:
            return
        print(f"Downloaded video to {video_file}")
    elif local_video_file and os.path.isfile(local_video_file):
        video_file = local_video_file
    else:
        messagebox.showerror("Error", "Please enter a YouTube URL or select a local video file")
        return

    if not output_dir or not os.path.isdir(output_dir):
        messagebox.showerror("Error", "Invalid output directory")
        return

    # Generate GIFs or video clips from the video
    print("Generating clips...")
    generate_clips(video_file, output_dir, chunk_duration, scale, format, progress_bar)
    print("Clip generation completed")


# Set up the GUI
root = tk.Tk()
root.title("Shreyas yt/vid clip gify gen")
root.geometry("600x450")
root.configure(bg='#2c3e50')

# Style elements
label_font = ("Helvetica", 12, "bold")
entry_font = ("Helvetica", 10)
button_font = ("Helvetica", 10, "bold")
button_bg = "#1abc9c"
button_fg = "#ecf0f1"
label_fg = "#ecf0f1"
entry_bg = "#34495e"
entry_fg = "#ecf0f1"

# YouTube URL
tk.Label(root, text="YouTube URL:", font=label_font, fg=label_fg, bg=root['bg']).grid(row=0, column=0, sticky=tk.W,
                                                                                      pady=10, padx=10)
youtube_url_entry = tk.Entry(root, width=50, font=entry_font, bg=entry_bg, fg=entry_fg, relief=tk.FLAT)
youtube_url_entry.grid(row=0, column=1, columnspan=2, pady=10, padx=10)

# Local Video File
tk.Label(root, text="Local Video File:", font=label_font, fg=label_fg, bg=root['bg']).grid(row=1, column=0, sticky=tk.W,
                                                                                           pady=10, padx=10)
local_video_file_entry = tk.Entry(root, width=50, font=entry_font, bg=entry_bg, fg=entry_fg, relief=tk.FLAT)
local_video_file_entry.grid(row=1, column=1, pady=10, padx=10)
tk.Button(root, text="Browse", command=lambda: browse_file(local_video_file_entry), font=button_font, bg=button_bg,
          fg=button_fg, relief=tk.FLAT).grid(row=1, column=2, pady=10, padx=10)

# Output Directory
tk.Label(root, text="Output Directory:", font=label_font, fg=label_fg, bg=root['bg']).grid(row=2, column=0, sticky=tk.W,
                                                                                           pady=10, padx=10)
output_dir_entry = tk.Entry(root, width=50, font=entry_font, bg=entry_bg, fg=entry_fg, relief=tk.FLAT)
output_dir_entry.grid(row=2, column=1, pady=10, padx=10)
tk.Button(root, text="Browse", command=lambda: browse_directory(output_dir_entry), font=button_font, bg=button_bg,
          fg=button_fg, relief=tk.FLAT).grid(row=2, column=2, pady=10, padx=10)

# Chunk Duration
tk.Label(root, text="Chunk Duration (seconds):", font=label_font, fg=label_fg, bg=root['bg']).grid(row=3, column=0,
                                                                                                   sticky=tk.W, pady=10,
                                                                                                   padx=10)
chunk_duration_entry = tk.Entry(root, width=10, font=entry_font, bg=entry_bg, fg=entry_fg, relief=tk.FLAT)
chunk_duration_entry.grid(row=3, column=1, sticky=tk.W, pady=10, padx=10)

# Scale
tk.Label(root, text="Scale (e.g., 480:-1):", font=label_font, fg=label_fg, bg=root['bg']).grid(row=4, column=0,
                                                                                               sticky=tk.W, pady=10,
                                                                                               padx=10)
scale_entry = tk.Entry(root, width=10, font=entry_font, bg=entry_bg, fg=entry_fg, relief=tk.FLAT)
scale_entry.grid(row=4, column=1, sticky=tk.W, pady=10, padx=10)

# Format
tk.Label(root, text="Format:", font=label_font, fg=label_fg, bg=root['bg']).grid(row=5, column=0, sticky=tk.W, pady=10,
                                                                                 padx=10)
format_var = tk.StringVar(value="gif")
tk.Radiobutton(root, text="GIF", variable=format_var, value="gif", font=label_font, fg=label_fg, bg=root['bg'],
               selectcolor=root['bg']).grid(row=5, column=1, sticky=tk.W, pady=10, padx=10)
tk.Radiobutton(root, text="MP4", variable=format_var, value="mp4", font=label_font, fg=label_fg, bg=root['bg'],
               selectcolor=root['bg']).grid(row=5, column=2, sticky=tk.W, pady=10, padx=10)

# Generate Button
tk.Button(root, text="Generate", command=on_generate, font=button_font, bg=button_bg, fg=button_fg,
          relief=tk.FLAT).grid(row=6, column=0, columnspan=3, pady=20)

# Progress Bar
progress_bar = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate")
progress_bar.grid(row=7, column=0, columnspan=3, pady=20)

# Set default values
chunk_duration_entry.insert(0, "10")
scale_entry.insert(0, "480:-1")

root.mainloop()
