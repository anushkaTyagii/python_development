import tkinter as tk  
from tkinter import messagebox, scrolledtext  
import speech_recognition as sr   
import webbrowser 
import json
from datetime import datetime
import threading  

# Load user preferences
def load_preferences():
    try:
        with open("preferences.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"preferred_search_engine": "google", "theme": "alexa"}

# Save user preferences
def save_preferences(preferences):
    with open("preferences.json", "w") as file:
        json.dump(preferences, file)

# Initialize recognizer
s = sr.Recognizer()
preferences = load_preferences()

def recognize_speech_from_mic():
    with sr.Microphone() as micro:
        status_label.config(text="Listening...")
        audio = s.listen(micro)
        status_label.config(text="Processing...")
        try:
            query = s.recognize_google(audio, language='en-in')
            status_label.config(text="Ready")
            return query
        except sr.UnknownValueError:
            status_label.config(text="Error")
            messagebox.showerror("Error", "Sorry, could not understand audio.")
        except sr.RequestError as e:
            status_label.config(text="Error")
            messagebox.showerror("Error", f"Could not request results from Google Speech Recognition service; {e}")
        status_label.config(text="Ready")
        return None

def start_listening():
    query = recognize_speech_from_mic()
    if query:
        query_entry.delete(0, tk.END)
        query_entry.insert(0, query)
        log_action("recognized", query)
        log_display.config(state='normal')
        log_display.insert(tk.END, f"Recognized: {query}\n")
        log_display.config(state='disabled')
        if "search" in query.lower():
            search_query()
        elif "update preferences" in query.lower():
            open_settings_window()

def search_query():
    query = query_entry.get()
    if query:
        search_engines = {
            "google": f"https://www.google.com/search?q={query}",
            "bing": f"https://www.bing.com/search?q={query}",
            "duckduckgo": f"https://duckduckgo.com/?q={query}",
            "yahoo": f"https://search.yahoo.com/search?p={query}"
        }
        search_url = search_engines.get(preferences['preferred_search_engine'], search_engines["google"])
        webbrowser.open(search_url)
        log_action("search", query)
        log_display.config(state='normal')
        log_display.insert(tk.END, f"Searched: {query}\n")
        log_display.config(state='disabled')
    else:
        messagebox.showwarning("Warning", "Please say or enter a query first.")

def log_action(action, query):
    with open("log.txt", "a") as log_file:
        log_file.write(f"{datetime.now()}: {action} - {query}\n")

def update_preferences():
    new_engine = search_engine_var.get().lower()
    preferences['preferred_search_engine'] = new_engine
    save_preferences(preferences)
    messagebox.showinfo("Info", f"Preferences updated to use {new_engine} as search engine.")
    log_display.config(state='normal')
    log_display.insert(tk.END, f"Preferences updated to use {new_engine} as search engine.\n")
    log_display.config(state='disabled')

def open_settings_window():
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.config(bg="#232F3E")

    preferences_label = tk.Label(settings_window, text="Preferred Search Engine:", bg="#232F3E", fg="#FFFFFF")
    preferences_label.pack()

    global search_engine_var
    search_engine_var = tk.StringVar(value=preferences['preferred_search_engine'])
    engines = ["Google", "Bing", "DuckDuckGo", "Yahoo"]
    for engine in engines:
        rb = tk.Radiobutton(settings_window, text=engine, variable=search_engine_var, value=engine.lower(), bg="#232F3E", fg="#FFFFFF", selectcolor="#232F3E")
        rb.pack()

    update_button = tk.Button(settings_window, text="Update Preferences", command=update_preferences, bg="#00A8E1", fg="#FFFFFF")
    update_button.pack()

    theme_label = tk.Label(settings_window, text="Theme:", bg="#232F3E", fg="#FFFFFF")
    theme_label.pack()

    theme_var = tk.StringVar(value=preferences['theme'])
    themes = ["Alexa", "Light", "Dark"]
    for theme in themes:
        rb = tk.Radiobutton(settings_window, text=theme, variable=theme_var, value=theme.lower(), command=lambda: change_theme(theme_var.get()), bg="#232F3E", fg="#FFFFFF", selectcolor="#232F3E")
        rb.pack()

def change_theme(theme):
    preferences['theme'] = theme
    save_preferences(preferences)
    apply_theme()

def apply_theme():
    theme = preferences.get('theme', 'alexa')
    if theme == 'alexa':
        root.config(bg='#232F3E')
        query_label.config(bg='#232F3E', fg='#FFFFFF')
        status_label.config(bg='#232F3E', fg='#FFFFFF')
        query_entry.config(bg='#FFFFFF', fg='#000000')
        log_display.config(bg='#FFFFFF', fg='#000000')
        for widget in root.winfo_children():
            if isinstance(widget, tk.Button):
                widget.config(bg='#00A8E1', fg='#FFFFFF')
            if isinstance(widget, tk.Label) and widget != status_label:
                widget.config(bg='#232F3E', fg='#FFFFFF')
    elif theme == 'light':
        root.config(bg='white')
        query_label.config(bg='#FFFFFF', fg='#000000')   
        status_label.config(bg='#FFFFFF', fg='#000000') 
        query_entry.config(bg='#666666', fg='#FFFFFF')  
        log_display.config(bg='#666666', fg='#FFFFFF')  
        for widget in root.winfo_children():
            if isinstance(widget, tk.Button):
                widget.config(bg='SystemButtonFace', fg='black')
            if isinstance(widget, tk.Label) and widget != status_label:
                widget.config(bg='white', fg='black')
    elif theme == 'dark':
        root.config(bg='#333333')
        query_label.config(bg='#333333', fg='#FFFFFF')
        status_label.config(bg='#333333', fg='#FFFFFF')
        query_entry.config(bg='#666666', fg='#FFFFFF')
        log_display.config(bg='#666666', fg='#FFFFFF')
        for widget in root.winfo_children():
            if isinstance(widget, tk.Button):
                widget.config(bg='#444444', fg='#FFFFFF')
            if isinstance(widget, tk.Label) and widget != status_label:
                widget.config(bg='#333333', fg='#FFFFFF')

def show_help():
    messagebox.showinfo("Help", "Instructions:\n\n1. Click 'Listen' to start listening to your voice.\n2. Say your query or command.\n3. Click 'Search' to search the query.\n4. Open 'Settings' to change preferences.\n\nVoice Commands:\n- 'search' to trigger search\n- 'update preferences' to open settings")

def continuous_listening():
    while True:
        start_listening()
        time.sleep(1)

# Create the main window
root = tk.Tk()
root.title("Speech Recognition")

# Create and place widgets
query_label = tk.Label(root, text="Query:")
query_label.pack()

query_entry = tk.Entry(root, width=50)
query_entry.pack()

listen_button = tk.Button(root, width=5, height=1, text="Listen", command=start_listening)
listen_button.pack()

search_button = tk.Button(root, width=5, height=1, text="Search", command=search_query)
search_button.pack()

settings_button = tk.Button(root, width=5, height=1, text="Settings", command=open_settings_window)
settings_button.pack()

help_button = tk.Button(root, width=5, height=1, text="Help", command=show_help)
help_button.pack()

status_label = tk.Label(root, text="Status: Ready", fg="green")
status_label.pack()

log_label = tk.Label(root, text="Log:")
log_label.pack()

log_display = scrolledtext.ScrolledText(root, width=60, height=10, state='disabled')
log_display.pack()

exit_button = tk.Button(root, width=5, height=1, text="Exit", command=root.quit)
exit_button.pack()

apply_theme()

# Start continuous listening in a separate thread
listener_thread = threading.Thread(target=continuous_listening, daemon=True)
listener_thread.start()

# Run the main event loop
root.mainloop()
