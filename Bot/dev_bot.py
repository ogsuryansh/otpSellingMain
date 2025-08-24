#!/usr/bin/env python3

import os
import sys
import time
import signal
import subprocess
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv

load_dotenv()

class BotRestartHandler(FileSystemEventHandler):
    
    def __init__(self, restart_callback):
        self.restart_callback = restart_callback
        self.last_restart = 0
        self.restart_delay = 2
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        if not event.src_path.endswith('.py'):
            return
        
        current_time = time.time()
        if current_time - self.last_restart < self.restart_delay:
            return
        
        print(f"\n🔄 File changed: {event.src_path}")
        print("🔄 Restarting bot...")
        
        self.last_restart = current_time
        self.restart_callback()

class DevBotRunner:
    
    def __init__(self):
        self.process = None
        self.observer = None
        self.running = True
        
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        print("\n🛑 Shutting down development bot...")
        self.running = False
        self.stop_bot()
        if self.observer:
            self.observer.stop()
        sys.exit(0)
    
    def start_bot(self):
        try:
            if self.process:
                self.stop_bot()
            
            print("🚀 Starting bot...")
            self.process = subprocess.Popen(
                [sys.executable, "main.py"],
                env=dict(os.environ, BOT_TOKEN=os.getenv('BOT_TOKEN', '')),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            threading.Thread(target=self.monitor_output, daemon=True).start()
            
        except Exception as e:
            print(f"❌ Error starting bot: {e}")
    
    def stop_bot(self):
        if self.process:
            print("🛑 Stopping bot...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None
    
    def monitor_output(self):
        if not self.process:
            return
        
        for line in iter(self.process.stdout.readline, ''):
            if line:
                print(line.rstrip())
        
        if self.running:
            print("⚠️ Bot process ended unexpectedly")
    
    def restart_bot(self):
        self.start_bot()
    
    def start_watcher(self):
        event_handler = BotRestartHandler(self.restart_bot)
        self.observer = Observer()
        self.observer.schedule(event_handler, '.', recursive=True)
        self.observer.start()
        
        print("👀 Watching for file changes...")
        print("📁 Monitoring directory: .")
        print("🔄 Bot will auto-restart when Python files change")
        print("🛑 Press Ctrl+C to stop")
    
    def run(self):
        print("🚀 Development Bot Runner")
        print("=" * 40)
        
        if not os.getenv('BOT_TOKEN'):
            print("❌ Error: BOT_TOKEN environment variable not set")
            print("Please set your bot token:")
            print("export BOT_TOKEN=your_bot_token_here")
            return
        
        self.start_bot()
        
        self.start_watcher()
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    runner = DevBotRunner()
    runner.run()
