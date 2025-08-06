import os
import subprocess
import platform
import ctypes
import psutil
import datetime
import requests

from livekit.agents import function_tool, RunContext

notes_memory = []
todo_list = []

@function_tool()
async def get_weather(context: RunContext, query: str) -> str:
    try:
        city = query.strip().split()[-1]
        resp = requests.get(f"https://wttr.in/{city}?format=3")
        return resp.text.strip() if resp.ok else f"{city} साठी हवामान मिळत नाही."
    except Exception as e:
        return f"Weather tool error: {e}"

@function_tool()
async def manage_notes(context: RunContext, query: str) -> str:
    q = query.lower()
    if "add" in q:
        note = query.split("add", 1)[1].strip()
        notes_memory.append(note)
        return f"Check! Note added: {note}"
    if "remove" in q:
        note = query.split("remove", 1)[1].strip()
        if note in notes_memory:
            notes_memory.remove(note)
            return f"Will do, Sir. Note removed: {note}"
        return f"Note not found: {note}"
    if "list" in q:
        return "\n".join(notes_memory) or "No notes saved."
    if "clear" in q:
        notes_memory.clear()
        return "All notes cleared."
    return "Invalid notes command."

@function_tool()
async def manage_todo(context: RunContext, query: str) -> str:
    q = query.lower()
    if "add" in q:
        task = query.split("add", 1)[1].strip()
        todo_list.append({"task": task, "done": False})
        return f"Task added: {task}"
    if "complete" in q:
        task = query.split("complete", 1)[1].strip()
        for t in todo_list:
            if t["task"] == task:
                t["done"] = True
                return f"Task completed: {task}"
        return f"Task not found: {task}"
    if "list" in q:
        return "\n".join(f"[{'✔' if t['done'] else '❌'}] {t['task']}" for t in todo_list) or "No tasks."
    if "clear" in q:
        todo_list.clear()
        return "All tasks cleared."
    return "Invalid todo command."

@function_tool()
async def control_os(context: RunContext, query: str) -> str:
    q = query.lower()
    try:
        if "lock" in q:
            if platform.system() == "Windows":
                ctypes.windll.user32.LockWorkStation()
                return "System locked."
        elif "shutdown" in q:
            if platform.system() == "Windows":
                # Enable required privileges
                ctypes.windll.advapi32.InitiateSystemShutdownW(None, "Shutting down", 0, True, False)
                return "System shutdown initiated."

        elif "restart" in q or "reboot" in q:
            if platform.system() == "Windows":
                ctypes.windll.advapi32.InitiateSystemShutdownW(None, "Restarting", 0, True, True)
                return "System restart initiated."

        elif "run script" in q:
            script = query.split("run script", 1)[1].strip()
            if not script.endswith(".py") or not os.path.exists(script):
                return f"Cannot run script: {script}"
            subprocess.Popen(["python", script], shell=True)
            return f"Running script: {script}"

        else:
            return "Invalid OS command."
    except Exception as e:
        return f"OS tool error: {e}"

@function_tool()
async def get_system_status(context: RunContext, query: str) -> str:
    try:
        b = psutil.sensors_battery()
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        return f"🔋 {b.percent if b else 'N/A'}%, 🧠 {cpu}%, 💾 {ram}% RAM"
    except Exception as e:
        return f"System tool error: {e}"

@function_tool()
async def get_current_time(context: RunContext, query: str) -> str:
    now = datetime.datetime.now()
    return now.strftime("🕒 %A, %d %B %Y %I:%M %p")

@function_tool()
async def launch_application(context: RunContext, query: str) -> str:
    """Launch common Windows applications using natural language."""
    import subprocess

    q = query.lower()
    app_paths = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "paint": "mspaint.exe",
        "cmd": "cmd.exe",
        "file explorer": "explorer.exe",
        "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "word": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
        "excel": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
        "vscode": r"C:\Users\<YOUR_USERNAME>\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    }

    for name, path in app_paths.items():
        if name in q:
            try:
                subprocess.Popen(path, shell=True)
                return f"Opening {name.title()}..."
            except Exception as e:
                return f"Failed to open {name}: {e}"

    return "Sorry, I couldn't recognize the application."

@function_tool()
async def send_whatsapp_message(context: RunContext, query: str) -> str:
    """
    Send WhatsApp message using a natural language command.
    Example: 'Send hello to +919322593526'
    """
    import pywhatkit as kit
    import re
    import datetime

    try:
        # Extract phone number using regex
        match = re.search(r"\+?\d{10,13}", query)
        if not match:
            return "Couldn't find a valid phone number."

        phone_number = match.group()
        # Extract message
        message = query.replace(f"to {phone_number}", "").replace("send", "").strip()

        # Set time 2 minutes from now
        now = datetime.datetime.now()
        send_hour = now.hour
        send_min = now.minute + 2
        if send_min >= 60:
            send_hour += 1
            send_min -= 60

        kit.sendwhatmsg(phone_number, message, send_hour, send_min, wait_time=15, tab_close=True)
        return f"Scheduled WhatsApp message to {phone_number}: '{message}'"
    except Exception as e:
        return f"Failed to send WhatsApp message: {e}"
    
@function_tool()
async def stream_song(context: RunContext, query: str) -> str:
    import requests, vlc, time
    song_name = query.replace("stream", "").strip()
    url = "https://musicfetch-musicfetch-default.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY"),
        "X-RapidAPI-Host": "musicfetch-musicfetch-default.p.rapidapi.com"
    }
    res = requests.get(url, headers=headers, params={"name": song_name})
    data = res.json()
    if not data or not data.get("tracks"):
        return f"काही गाणं सापडलं नाही: {song_name}"
    track = data["tracks"][0]
    stream_url = track.get("url") or track.get("audio")
    if not stream_url:
        return "स्ट्रीम URL उपलब्ध नाही."
    player = vlc.MediaPlayer(stream_url)
    player.play()
    time.sleep(5)
    return f"स्ट्रीम करतोय: {track['name']} — {track['artists'][0]}"

@function_tool()
async def execute_task(context: RunContext, query: str) -> str:
    from selenium import webdriver
    from selenium.webdriver.edge.service import Service as EdgeService
    from selenium.webdriver.edge.options import Options as EdgeOptions
    from webdriver_manager.microsoft import EdgeChromiumDriverManager

    try:
        edge_options = EdgeOptions()
        edge_options.add_argument("--start-maximized")
        edge_options.add_argument("--disable-infobars")
        edge_options.add_argument("--disable-extensions")
        edge_options.add_argument("--disable-dev-shm-usage")
        edge_options.add_argument("--no-sandbox")
        edge_options.add_argument("--headless=new")  # New headless mode for Edge
        edge_options.add_experimental_option("detach", True)

        driver = webdriver.Edge(
            service=EdgeService(EdgeChromiumDriverManager().install()),
            options=edge_options
        )

        q = query.lower()
        url = "https://www.google.com"

        if "order food" in q or "food delivery" in q:
            url = "https://www.swiggy.com/"
        elif "book hotel" in q:
            url = "https://www.booking.com/"
        elif "book cab" in q or "taxi" in q:
            url = "https://www.uber.com/in/en/"
        elif "flight" in q or "book flight" in q:
            url = "https://www.makemytrip.com/flights/"
        elif "movie" in q or "book ticket" in q:
            url = "https://in.bookmyshow.com/"
        elif "restaurant near me" in q:
            url = "https://www.google.com/maps/search/restaurants+near+me/"
        elif "search" in q:
            search = q.replace("search", "").strip()
            url = f"https://www.google.com/search?q={search}"
        else:
            url = f"https://www.google.com/search?q={q}"

        driver.get(url)
        return f"✅ Task executed: {url}"

    except Exception as e:
        return f"❌ Selenium Error: {e}"
