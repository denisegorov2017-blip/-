from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import os
from improved_coefficient_calculator import main

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_processed = time.time()
        
    def on_modified(self, event):
        if time.time() - self.last_processed < 2:  # Защита от двойного срабатывания
            return
            
        if event.src_path.endswith(("sheet_1_Лист_1.csv", "test_data.csv")):
            print(f"Обнаружено изменение в {os.path.basename(event.src_path)}, пересчитываем...")
            try:
                main()
                print("Пересчет завершен успешно!")
            except Exception as e:
                print(f"Ошибка при пересчете: {str(e)}")
                
            self.last_processed = time.time()

def start_watching():
    path = "исходные_данные"
    event_handler = FileChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    
    try:
        print(f"Отслеживание изменений в папке {path}...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_watching()
