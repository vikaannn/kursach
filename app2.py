import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import threading
import time
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter
from queue import Queue
from functools import lru_cache
import os
import json
from pathlib import Path

# ==============================================
# КОНСТАНТЫ И НАСТРОЙКИ
# ==============================================
# Цветовая схема приложения
DARK_BG = "#1a1a2e"       # Темный фон
CARD_BG = "#16213e"       # Фон карточек
ACCENT_COLOR = "#4cc9f0"  # Акцентный цвет
TEXT_COLOR = "#ffffff"    # Цвет текста
GREEN_COLOR = "#4ad66d"   # Цвет для позитивных значений
RED_COLOR = "#f72585"     # Цвет для негативных значений
SAVE_COLOR = "#2ecc71"    # Цвет кнопки сохранения

# ==============================================
# КЛАСС ОКНА АВТОРИЗАЦИИ
# ==============================================
class LoginWindow:
    """Окно входа в систему с проверкой учетных данных"""
    
    def __init__(self, master):
        """Инициализация окна авторизации"""
        self.master = master
        self.master.title("Авторизация")
        self.master.geometry("400x300")
        self.master.resizable(False, False)
        self.master.configure(bg=DARK_BG)
        
        # Настройка стилей
        self._setup_styles()
        
        # Создание элементов интерфейса
        self._create_widgets()
    
    def _setup_styles(self):
        """Настройка стилей для элементов интерфейса"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('.', background=DARK_BG, foreground=TEXT_COLOR)
        self.style.configure('TEntry', foreground='#000000', fieldbackground='white')
    
    def _create_widgets(self):
        """Создание элементов интерфейса авторизации"""
        # Заголовок
        ttk.Label(
            self.master, 
            text="Вход в систему", 
            font=('Arial', 14, 'bold'),
            foreground=ACCENT_COLOR,
            background=DARK_BG
        ).pack(pady=10)
        
        # Фрейм для полей ввода
        input_frame = tk.Frame(self.master, bg=DARK_BG)
        input_frame.pack()
        
        # Поле ввода логина
        ttk.Label(input_frame, text="Логин:", foreground=TEXT_COLOR, background=DARK_BG).pack(anchor='w')
        self.login_entry = ttk.Entry(input_frame, style='TEntry')
        self.login_entry.pack(pady=5, fill='x')
        
        # Поле ввода пароля
        ttk.Label(input_frame, text="Пароль:", foreground=TEXT_COLOR, background=DARK_BG).pack(anchor='w')
        self.password_entry = ttk.Entry(input_frame, show="*", style='TEntry')
        self.password_entry.pack(pady=5, fill='x')
        
        # Кнопка входа
        login_btn = ttk.Button(
            self.master, 
            text="Войти", 
            command=self.check_credentials,
            style='Accent.TButton'
        )
        login_btn.pack(pady=10)
        
        # Метка для отображения ошибок
        self.error_label = tk.Label(
            self.master, 
            text="", 
            foreground=RED_COLOR,
            background=DARK_BG,
            font=('Arial', 10)
        )
        self.error_label.pack()
        
        # Стиль для акцентной кнопки
        self.style.configure('Accent.TButton', background=ACCENT_COLOR, foreground=DARK_BG)
    
    def check_credentials(self):
        """Проверка введенных учетных данных"""
        login = self.login_entry.get()
        password = self.password_entry.get()
        
        # Простая проверка логина/пароля (в реальном приложении нужно использовать безопасное хранение)
        if login == "vika" and password == "12345678":
            self.master.destroy()  # Закрываем окно авторизации
            root = tk.Tk()
            app = CryptoAggregatorApp(root)  # Запускаем основное приложение
            root.mainloop()
        else:
            self.error_label.config(text="Ошибка авторизации! Неверный логин или пароль")

# ==============================================
# КЛАСС ПРОКРУЧИВАЕМОГО ФРЕЙМА
# ==============================================
class ModernScrollableFrame(ttk.Frame):
    """Кастомный прокручиваемый фрейм для создания скроллинга в интерфейсе"""
    
    def __init__(self, container, *args, **kwargs):
        """Инициализация прокручиваемого фрейма"""
        super().__init__(container, *args, **kwargs)
        
        # Canvas для реализации прокрутки
        self.canvas = tk.Canvas(self, bg=DARK_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        
        # Фрейм, который будет прокручиваться
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Привязка событий для корректной работы прокрутки
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        # Размещение элементов
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

# ==============================================
# КЛАСС КАРТОЧКИ (UI-КОМПОНЕНТ)
# ==============================================
class ModernCard(tk.Frame):
    """Стилизованная карточка для группировки элементов интерфейса"""
    
    def __init__(self, master, title="", *args, **kwargs):
        """Инициализация карточки"""
        super().__init__(master, bg=DARK_BG, *args, **kwargs)
        
        # Контейнер карточки
        self.card_container = tk.Frame(self, bg=CARD_BG, bd=0, highlightthickness=0)
        self.card_container.pack(fill="both", expand=True, padx=5, pady=5, ipadx=10, ipady=10)
        
        # Заголовок карточки (если указан)
        if title:
            self._create_title(title)
        
        # Основное содержимое карточки
        self.content = tk.Frame(self.card_container, bg=CARD_BG)
        self.content.pack(fill="both", expand=True)
    
    def _create_title(self, title):
        """Создание заголовка карточки"""
        self.title_frame = tk.Frame(self.card_container, bg=CARD_BG)
        self.title_frame.pack(fill="x", pady=(0, 10))
        
        self.title_label = tk.Label(
            self.title_frame, 
            text=title, 
            bg=CARD_BG, 
            fg=ACCENT_COLOR,
            font=('Arial', 12, 'bold'),
            anchor="w"
        )
        self.title_label.pack(side="left")

# ==============================================
# КЛАСС АНИМАЦИИ ЗАГРУЗКИ
# ==============================================
class LoadingAnimation:
    """Анимация загрузки с тремя точками для визуальной индикации процесса"""
    
    def __init__(self, canvas, x, y, size=20, color=ACCENT_COLOR):
        """
        Инициализация анимации загрузки
        
        Args:
            canvas: Canvas для отрисовки
            x: Координата X начальной позиции
            y: Координата Y начальной позиции
            size: Размер точек
            color: Базовый цвет точек
        """
        self.canvas = canvas
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.dots = []
        self.animation_id = None
        self.active = False
        
        # Создаем три точки для анимации
        for i in range(3):
            dot = self.canvas.create_oval(
                x + i*(size+5), y,
                x + i*(size+5) + size, y + size,
                fill=color,
                state=tk.HIDDEN
            )
            self.dots.append(dot)
    
    def start(self):
        """Запуск анимации"""
        self.active = True
        for dot in self.dots:
            self.canvas.itemconfig(dot, state=tk.NORMAL)
        self.animate(0)
    
    def stop(self):
        """Остановка анимации"""
        self.active = False
        if self.animation_id:
            self.canvas.after_cancel(self.animation_id)
        for dot in self.dots:
            self.canvas.itemconfig(dot, state=tk.HIDDEN)
    
    def animate(self, index):
        """Анимация переключения между точками"""
        if not self.active:
            return
            
        # Сброс цвета всех точек
        for dot in self.dots:
            self.canvas.itemconfig(dot, fill=self.color)
        
        # Подсветка текущей точки
        self.canvas.itemconfig(self.dots[index], fill=TEXT_COLOR)
        
        # Планирование следующего шага анимации
        next_index = (index + 1) % 3
        self.animation_id = self.canvas.after(300, lambda: self.animate(next_index))

# ==============================================
# ОСНОВНОЙ КЛАСС ПРИЛОЖЕНИЯ
# ==============================================
class CryptoAggregatorApp:
    """Основной класс приложения-агрегатора криптовалют"""
    
    def __init__(self, root):
        """Инициализация основного приложения"""
        self.root = root
        self.root.title("Агрегатор криптовалюты")
        self.root.geometry("1350x1100")
        self.root.configure(bg=DARK_BG)
        
        # Настройка приложения
        self._setup_styles()
        self._create_ui()
        
        # Инициализация HTTP-сессии
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'CryptoAggregator/1.0'})
        
        # Очередь для безопасного обновления UI из других потоков
        self.ui_queue = Queue()
        
        # Структуры для хранения данных
        self.price_history = {'Bybit': [], 'MEXC': [], 'Binance': []}
        self.time_history = []
        self.realtime_data = {
            'Bybit': {'prices': [], 'times': []},
            'MEXC': {'prices': [], 'times': []},
            'Binance': {'prices': [], 'times': []}
        }
        
        # Настройки обновления
        self.running = True
        self.update_interval = 10  # Интервал основного обновления (сек)
        self.realtime_interval = 3  # Интервал обновления реального времени (сек)
        
        # Инициализация анимации загрузки
        self._init_loading_animation()
        
        # Запуск фоновых потоков
        self._start_background_threads()
        
        # Обработчики событий
        self.root.after(100, self.process_ui_queue)
        self.root.after(150, self.initial_loading)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def _init_loading_animation(self):
        """Инициализация анимации загрузки"""
        self.loading_canvas = tk.Canvas(
            self.main_frame.scrollable_frame, 
            bg=DARK_BG, 
            height=30, 
            highlightthickness=0
        )
        self.loading_animation = LoadingAnimation(
            self.loading_canvas, 
            x=50, 
            y=5, 
            size=8, 
            color=ACCENT_COLOR
        )
        self.loading_canvas.pack_forget()
    
    def _start_background_threads(self):
        """Запуск фоновых потоков для обновления данных"""
        # Поток для основного обновления данных
        self.update_thread = threading.Thread(target=self.auto_update, daemon=True)
        self.update_thread.start()
        
        # Поток для обновления данных в реальном времени
        self.realtime_thread = threading.Thread(target=self.auto_update_realtime, daemon=True)
        self.realtime_thread.start()
    
    def initial_loading(self):
        """Показ анимации загрузки при старте"""
        self.show_loading()
        self.root.after(1000, self.hide_loading)
    
    def show_loading(self):
        """Показать анимацию загрузки"""
        self.loading_canvas.pack(fill='x', pady=10)
        self.loading_animation.start()
        self.root.update()
    
    def hide_loading(self):
        """Скрыть анимацию загрузки"""
        self.loading_animation.stop()
        self.loading_canvas.pack_forget()
        self.root.update()
    
    def _setup_styles(self):
        """Настройка стилей для элементов интерфейса"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Базовые стили
        style.configure('.', background=DARK_BG, foreground=TEXT_COLOR)
        style.configure('TFrame', background=DARK_BG)
        style.configure('TLabel', background=DARK_BG, foreground=TEXT_COLOR, font=('Arial', 10))
        style.configure('TButton', background=CARD_BG, foreground=TEXT_COLOR, 
                       font=('Arial', 10, 'bold'), borderwidth=0)
        style.map('TButton', background=[('active', ACCENT_COLOR)])
        
        # Специальные стили
        style.configure('Accent.TButton', background=ACCENT_COLOR, foreground=DARK_BG)
        style.configure('Save.TButton', background=SAVE_COLOR, foreground=DARK_BG)
        style.map('Save.TButton', 
                 background=[('active', '#3aa856')],
                 foreground=[('active', DARK_BG)])
        style.configure('Header.TLabel', font=('Arial', 16, 'bold'), foreground=ACCENT_COLOR)
        style.configure('Buy.TLabel', foreground=GREEN_COLOR, font=('Arial', 12, 'bold'))
        style.configure('Sell.TLabel', foreground=RED_COLOR, font=('Arial', 12, 'bold'))
        style.configure('Table.TLabel', font=('Arial', 11), anchor='center')
        style.configure('TableHeader.TLabel', font=('Arial', 11, 'bold'), anchor='center')
        style.configure('Loading.TCanvas', background=DARK_BG)
    
    def _create_ui(self):
        """Создание пользовательского интерфейса"""
        self.main_frame = ModernScrollableFrame(self.root)
        self.main_frame.pack(fill="both", expand=True)
        
        # Создание всех компонентов интерфейса
        self._create_header()
        self._create_best_price_card()
        self._create_centered_price_table()
        self._create_realtime_charts()
        self._create_weekly_charts()
        self._create_top10_table()
    
    def _create_header(self):
        """Создание верхней панели приложения"""
        header_frame = ModernCard(self.main_frame.scrollable_frame)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        # Заголовок приложения
        title_label = tk.Label(
            header_frame.card_container, 
            text="АГРЕГАТОР КРИПТОВАЛЮТЫ", 
            bg=CARD_BG, 
            fg=TEXT_COLOR,
            font=('Arial', 20, 'bold')
        )
        title_label.pack(side="left", padx=10, pady=5)
        
        # Панель управления
        control_frame = tk.Frame(header_frame.card_container, bg=CARD_BG)
        control_frame.pack(side="right", padx=10, pady=5)
        
        # Кнопка сохранения данных
        save_btn = ttk.Button(
            control_frame, 
            text="💾 Сохранить", 
            style='Save.TButton', 
            command=self.save_data_to_file
        )
        save_btn.pack(side="left", padx=5)
        
        # Выбор криптовалюты
        self.crypto_var = tk.StringVar(value="BTC")
        crypto_menu = ttk.Combobox(
            control_frame,
            textvariable=self.crypto_var,
            values=["BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", "DOT", "AVAX"],
            state="readonly",
            width=10,
            font=('Arial', 11)
        )
        crypto_menu.pack(side="left", padx=5)
        
        # Обработчик изменения выбранной криптовалюты
        self.crypto_var.trace_add('write', lambda *args: self.on_crypto_change())
        
        # Кнопка обновления данных
        refresh_btn = ttk.Button(
            control_frame, 
            text="⟳ Обновить", 
            style='Accent.TButton', 
            command=self.manual_refresh
        )
        refresh_btn.pack(side="left", padx=5)
    
    def save_data_to_file(self):
        """Сохранение текущих данных в файл на рабочем столе"""
        try:
            # Определение пути к рабочему столу
            desktop = Path.home() / "Desktop"
            if not desktop.exists():
                desktop = Path.home() / "Рабочий стол"
            
            # Создание папки для сохранения
            save_dir = desktop / "CryptoData"
            save_dir.mkdir(exist_ok=True)
            
            # Формирование имени файла
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = save_dir / f"crypto_data_{self.crypto_var.get()}_{timestamp}.txt"
            
            # Сбор данных для сохранения
            data = {
                "crypto": self.crypto_var.get(),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "best_prices": {
                    "buy": self.best_buy_label.cget("text"),
                    "sell": self.best_sell_label.cget("text")
                },
                "exchange_prices": {},
                "top10_prices": {}
            }
            
            # Сбор данных по биржам
            for i, exchange in enumerate(self.exchanges):
                data["exchange_prices"][exchange] = {
                    "buy": self.price_labels[i][0].cget("text"),
                    "sell": self.price_labels[i][1].cget("text"),
                    "spread": self.price_labels[i][2].cget("text")
                }
            
            # Сбор данных топ-10 криптовалют
            for i, symbol in enumerate(self.top10_symbols):
                data["top10_prices"][symbol] = {
                    "Bybit": self.top10_labels[i][0].cget("text"),
                    "MEXC": self.top10_labels[i][1].cget("text"),
                    "Binance": self.top10_labels[i][2].cget("text")
                }
            
            # Сохранение в читаемом текстовом формате
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Данные криптовалютного агрегатора\n")
                f.write(f"Дата: {data['timestamp']}\n")
                f.write(f"Криптовалюта: {data['crypto']}\n\n")
                
                f.write("=== Лучшие цены ===\n")
                f.write(f"{data['best_prices']['buy']}\n")
                f.write(f"{data['best_prices']['sell']}\n\n")
                
                f.write("=== Цены по биржам ===\n")
                for exchange, prices in data['exchange_prices'].items():
                    f.write(f"{exchange}:\n")
                    f.write(f"  Купить: {prices['buy']}\n")
                    f.write(f"  Продать: {prices['sell']}\n")
                    f.write(f"  Спред: {prices['spread']}\n\n")
                
                f.write("=== Топ-10 криптовалют ===\n")
                for symbol, prices in data['top10_prices'].items():
                    f.write(f"{symbol}:\n")
                    f.write(f"  Bybit: {prices['Bybit']}\n")
                    f.write(f"  MEXC: {prices['MEXC']}\n")
                    f.write(f"  Binance: {prices['Binance']}\n\n")
            
            # Уведомление об успешном сохранении
            messagebox.showinfo(
                "Сохранение данных",
                f"Данные успешно сохранены в файл:\n{filename}"
            )
            
            # Дополнительное сохранение в JSON
            json_filename = save_dir / f"crypto_data_{self.crypto_var.get()}_{timestamp}.json"
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            messagebox.showerror(
                "Ошибка сохранения",
                f"Не удалось сохранить данные:\n{str(e)}"
            )
    
    def on_crypto_change(self):
        """Обработчик изменения выбранной криптовалюты"""
        self.show_loading()
        try:
            self.reset_chart_data()
            self.update_data()
        finally:
            self.hide_loading()
    
    def manual_refresh(self):
        """Ручное обновление данных"""
        self.show_loading()
        try:
            threading.Thread(target=self.update_data_with_callback).start()
        except:
            self.hide_loading()
            raise
    
    def update_data_with_callback(self):
        """Обновление данных с callback для скрытия анимации"""
        try:
            self.update_data()
        finally:
            self.ui_queue.put((self.hide_loading, ()))
    
    def _create_best_price_card(self):
        """Создание карточки с лучшими ценами"""
        self.best_price_card = ModernCard(self.main_frame.scrollable_frame, title="Лучшие цены")
        self.best_price_card.pack(fill="x", padx=10, pady=5)
        
        content = self.best_price_card.content
        
        # Фрейм для лучшей цены покупки
        self.best_buy_frame = tk.Frame(content, bg=CARD_BG)
        self.best_buy_frame.pack(fill="x", pady=5)
        
        tk.Label(
            self.best_buy_frame, 
            text="ЛУЧШАЯ ЦЕНА ПОКУПКИ:", 
            bg=CARD_BG, 
            fg=TEXT_COLOR,
            font=('Arial', 11)
        ).pack(side="left")
        
        self.best_buy_label = tk.Label(
            self.best_buy_frame, 
            text="загрузка...", 
            bg=CARD_BG, 
            fg=GREEN_COLOR,
            font=('Arial', 11, 'bold')
        )
        self.best_buy_label.pack(side="left", padx=5)
        
        # Фрейм для лучшей цены продажи
        self.best_sell_frame = tk.Frame(content, bg=CARD_BG)
        self.best_sell_frame.pack(fill="x", pady=5)
        
        tk.Label(
            self.best_sell_frame, 
            text="ЛУЧШАЯ ЦЕНА ПРОДАЖИ:", 
            bg=CARD_BG, 
            fg=TEXT_COLOR,
            font=('Arial', 11)
        ).pack(side="left")
        
        self.best_sell_label = tk.Label(
            self.best_sell_frame, 
            text="загрузка...", 
            bg=CARD_BG, 
            fg=RED_COLOR,
            font=('Arial', 11, 'bold')
        )
        self.best_sell_label.pack(side="left", padx=5)
    
    def _create_centered_price_table(self):
        """Создание таблицы с ценами по биржам"""
        table_card = ModernCard(self.main_frame.scrollable_frame, title="Цены по биржам")
        table_card.pack(fill="x", padx=10, pady=10)
        
        table_container = tk.Frame(table_card.content, bg=CARD_BG)
        table_container.pack(expand=True)
        
        self.price_table = tk.Frame(table_container, bg=CARD_BG)
        self.price_table.pack(pady=10)
        
        # Заголовки таблицы
        headers = ["Биржа", "Цена покупки", "Цена продажи", "Разница"]
        for col, header in enumerate(headers):
            tk.Label(
                self.price_table, 
                text=header, 
                bg=CARD_BG, 
                fg=ACCENT_COLOR,
                font=('Arial', 11, 'bold'),
                padx=15,
                pady=5
            ).grid(row=0, column=col)
        
        # Данные по биржам
        self.exchanges = ["Bybit", "MEXC", "Binance"]
        self.price_labels = []
        
        # Заполнение таблицы данными
        for row, exchange in enumerate(self.exchanges, start=1):
            # Название биржи
            tk.Label(
                self.price_table, 
                text=exchange, 
                bg=CARD_BG, 
                fg=TEXT_COLOR,
                font=('Arial', 11),
                padx=15,
                pady=5
            ).grid(row=row, column=0)
            
            # Цена покупки
            buy_label = tk.Label(
                self.price_table, 
                text="...", 
                bg=CARD_BG, 
                fg=GREEN_COLOR,
                font=('Arial', 11),
                padx=15,
                pady=5
            )
            buy_label.grid(row=row, column=1)
            
            # Цена продажи
            sell_label = tk.Label(
                self.price_table, 
                text="...", 
                bg=CARD_BG, 
                fg=RED_COLOR,
                font=('Arial', 11),
                padx=15,
                pady=5
            )
            sell_label.grid(row=row, column=2)
            
            # Разница (спред)
            diff_label = tk.Label(
                self.price_table, 
                text="...", 
                bg=CARD_BG, 
                fg=TEXT_COLOR,
                font=('Arial', 11),
                padx=15,
                pady=5
            )
            diff_label.grid(row=row, column=3)
            
            self.price_labels.append((buy_label, sell_label, diff_label))
    
    def _create_realtime_charts(self):
        """Создание графиков в реальном времени"""
        self.realtime_charts_frame = ModernCard(self.main_frame.scrollable_frame, title="Графики в реальном времени")
        self.realtime_charts_frame.pack(fill="x", padx=10, pady=10)
        
        self.realtime_chart_frames = []
        for exchange in self.exchanges:
            chart_frame = tk.Frame(self.realtime_charts_frame.content, bg=CARD_BG)
            chart_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
            self.realtime_chart_frames.append(chart_frame)
        
        self._init_realtime_charts()
    
    def _create_weekly_charts(self):
        """Создание исторических графиков за неделю"""
        self.weekly_charts_frame = ModernCard(self.main_frame.scrollable_frame, title="История за 7 дней")
        self.weekly_charts_frame.pack(fill="x", padx=10, pady=10)
        
        self.weekly_chart_frames = []
        for exchange in self.exchanges:
            chart_frame = tk.Frame(self.weekly_charts_frame.content, bg=CARD_BG)
            chart_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
            self.weekly_chart_frames.append(chart_frame)
        
        self._init_weekly_charts()
    
    def _create_top10_table(self):
        """Создание таблицы с топ-10 криптовалютами"""
        self.top10_card = ModernCard(self.main_frame.scrollable_frame, title="Топ-10 криптовалют")
        self.top10_card.pack(fill="x", padx=10, pady=10)
        
        table_container = tk.Frame(self.top10_card.content, bg=CARD_BG)
        table_container.pack(expand=True)
        
        self.top10_table = tk.Frame(table_container, bg=CARD_BG)
        self.top10_table.pack(pady=10)
        
        # Заголовки таблицы
        headers = ["Криптовалюта", "Bybit", "MEXC", "Binance"]
        for col, header in enumerate(headers):
            tk.Label(
                self.top10_table, 
                text=header, 
                bg=CARD_BG, 
                fg=ACCENT_COLOR,
                font=('Arial', 11, 'bold'),
                padx=10,
                pady=5
            ).grid(row=0, column=col)
        
        # Список криптовалют
        self.top10_symbols = ["BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", "DOT", "AVAX"]
        self.top10_labels = []
        
        # Заполнение таблицы данными
        for row, symbol in enumerate(self.top10_symbols, start=1):
            # Название криптовалюты
            tk.Label(
                self.top10_table, 
                text=symbol, 
                bg=CARD_BG, 
                fg=TEXT_COLOR,
                font=('Arial', 11),
                padx=10,
                pady=2
            ).grid(row=row, column=0)
            
            # Цены по биржам
            for col, exchange in enumerate(self.exchanges, start=1):
                label = tk.Label(
                    self.top10_table, 
                    text="...", 
                    bg=CARD_BG, 
                    fg=TEXT_COLOR,
                    font=('Arial', 11),
                    padx=10,
                    pady=2
                )
                label.grid(row=row, column=col)
                if col == 1:
                    self.top10_labels.append((label, None, None))
                elif col == 2:
                    self.top10_labels[-1] = (self.top10_labels[-1][0], label, None)
                else:
                    self.top10_labels[-1] = (self.top10_labels[-1][0], self.top10_labels[-1][1], label)
    
    def _init_realtime_charts(self):
        """Инициализация графиков реального времени"""
        self.realtime_figures = []
        self.realtime_axes = []
        self.realtime_canvases = []
        
        for i, exchange in enumerate(self.exchanges):
            # Создание фигуры matplotlib
            fig = Figure(figsize=(4, 2.5), dpi=100, facecolor=CARD_BG)
            ax = fig.add_subplot(111)
            ax.set_facecolor(CARD_BG)
            
            # Настройка осей
            ax.tick_params(axis='x', colors=TEXT_COLOR, labelsize=7)
            ax.tick_params(axis='y', colors=TEXT_COLOR, labelsize=8)
            ax.yaxis.label.set_color(TEXT_COLOR)
            ax.set_title(f'{exchange} (Real-time)', color=TEXT_COLOR, fontsize=9)
            
            # Форматирование чисел
            ax.yaxis.set_major_formatter(plt.FormatStrFormatter('%.2f'))
            
            # Настройка границ
            for spine in ax.spines.values():
                spine.set_color(ACCENT_COLOR)
            
            # Встраивание в Tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.realtime_chart_frames[i])
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
            # Сохранение ссылок
            self.realtime_figures.append(fig)
            self.realtime_axes.append(ax)
            self.realtime_canvases.append(canvas)
    
    def _init_weekly_charts(self):
        """Инициализация недельных графиков"""
        self.weekly_figures = []
        self.weekly_axes = []
        self.weekly_canvases = []
        
        for i, exchange in enumerate(self.exchanges):
            # Создание фигуры matplotlib
            fig = Figure(figsize=(4, 2.5), dpi=100, facecolor=CARD_BG)
            ax = fig.add_subplot(111)
            ax.set_facecolor(CARD_BG)
            
            # Настройка осей
            ax.tick_params(axis='x', colors=TEXT_COLOR, labelsize=7, rotation=45)
            ax.tick_params(axis='y', colors=TEXT_COLOR, labelsize=8)
            ax.yaxis.label.set_color(TEXT_COLOR)
            ax.set_title(f'{exchange} (7 days)', color=TEXT_COLOR, fontsize=9, pad=10)
            
            # Настройка отображения дат
            fig.autofmt_xdate(bottom=0.2, rotation=45, ha='right')
            fig.subplots_adjust(bottom=0.25, left=0.15)
            
            # Форматирование чисел
            ax.yaxis.set_major_formatter(plt.FormatStrFormatter('%.2f'))
            
            # Настройка границ
            for spine in ax.spines.values():
                spine.set_color(ACCENT_COLOR)
            
            # Встраивание в Tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.weekly_chart_frames[i])
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
            # Сохранение ссылок
            self.weekly_figures.append(fig)
            self.weekly_axes.append(ax)
            self.weekly_canvases.append(canvas)
    
    def process_ui_queue(self):
        """Обработка очереди задач для обновления UI из других потоков"""
        try:
            while not self.ui_queue.empty():
                task, args = self.ui_queue.get_nowait()
                task(*args)
        except:
            pass
        finally:
            self.root.after(100, self.process_ui_queue)
    
    def reset_chart_data(self):
        """Сброс данных графиков при изменении криптовалюты"""
        self.price_history = {'Bybit': [], 'MEXC': [], 'Binance': []}
        self.time_history = []
        self.realtime_data = {
            'Bybit': {'prices': [], 'times': []},
            'MEXC': {'prices': [], 'times': []},
            'Binance': {'prices': [], 'times': []}
        }
        
        # Очистка графиков
        for i in range(len(self.exchanges)):
            self.realtime_axes[i].clear()
            self.weekly_axes[i].clear()
            
            self.realtime_axes[i].set_title(f'{self.exchanges[i]} (Real-time)', color=TEXT_COLOR, fontsize=9)
            self.weekly_axes[i].set_title(f'{self.exchanges[i]} (7 days)', color=TEXT_COLOR, fontsize=9)
            
            self.realtime_canvases[i].draw()
            self.weekly_canvases[i].draw()
    
    def update_realtime_charts(self):
        """Обновление графиков в реальном времени"""
        symbol = self.crypto_var.get()
        
        try:
            for i, exchange in enumerate(self.exchanges):
                # Получение текущей цены
                price = self.fetch_current_price(symbol, exchange)
                
                if price is not None:
                    # Добавление новых данных
                    self.realtime_data[exchange]['prices'].append(price)
                    self.realtime_data[exchange]['times'].append(datetime.now())
                    
                    # Ограничение истории
                    if len(self.realtime_data[exchange]['prices']) > 20:
                        self.realtime_data[exchange]['prices'] = self.realtime_data[exchange]['prices'][-20:]
                        self.realtime_data[exchange]['times'] = self.realtime_data[exchange]['times'][-20:]
                    
                    # Очистка и перерисовка графика
                    self.realtime_axes[i].clear()
                    
                    # Настройка осей
                    self.realtime_axes[i].tick_params(axis='x', colors=TEXT_COLOR, labelsize=7, rotation=45)
                    self.realtime_axes[i].tick_params(axis='y', colors=TEXT_COLOR, labelsize=8)
                    self.realtime_axes[i].yaxis.set_major_formatter(plt.FormatStrFormatter('%.2f'))
                    self.realtime_axes[i].xaxis.set_major_formatter(DateFormatter('%H:%M'))
                    self.realtime_figures[i].subplots_adjust(bottom=0.25, left=0.15)
                    
                    # Построение графика
                    self.realtime_axes[i].plot(
                        self.realtime_data[exchange]['times'],
                        self.realtime_data[exchange]['prices'],
                        color=GREEN_COLOR, linewidth=1
                    )
                    
                    # Настройка заголовков
                    self.realtime_axes[i].set_title(f'{exchange} - {symbol} (Real-time)', color=TEXT_COLOR, fontsize=9)
                    self.realtime_axes[i].set_xlabel('Время', color=TEXT_COLOR, fontsize=8)
                    self.realtime_axes[i].set_ylabel('Цена (USD)', color=TEXT_COLOR, fontsize=8)
                    
                    # Настройка границ
                    for spine in self.realtime_axes[i].spines.values():
                        spine.set_color(ACCENT_COLOR)
                    
                    # Автомасштабирование
                    self.realtime_axes[i].relim()
                    self.realtime_axes[i].autoscale_view()
                    
                    # Обновление canvas через очередь UI
                    self.ui_queue.put((self.realtime_canvases[i].draw, ()))
        
        except Exception as e:
            print(f"Ошибка обновления графиков реального времени: {e}")
    
    def auto_update_realtime(self):
        """Автоматическое обновление графиков реального времени в отдельном потоке"""
        while self.running:
            try:
                self.update_realtime_charts()
            except Exception as e:
                print(f"Ошибка в потоке реального времени: {e}")
            
            # Пауза между обновлениями
            for _ in range(self.realtime_interval):
                if not self.running:
                    return
                time.sleep(1)
    
    def fetch_historical_data(self, symbol, exchange):
        """Получение исторических данных за 7 дней для указанной криптовалюты и биржи"""
        try:
            if exchange == "Binance":
                url = f"https://api.binance.com/api/v3/klines?symbol={symbol}USDT&interval=1d&limit=7"
                response = self.session.get(url, timeout=5)
                response.raise_for_status()
                data = response.json()
                return [float(item[4]) for item in data]
            
            elif exchange == "Bybit":
                url = f"https://api.bybit.com/v5/market/kline?category=spot&symbol={symbol}USDT&interval=D&limit=7"
                response = self.session.get(url, timeout=5)
                response.raise_for_status()
                data = response.json()
                if data['retCode'] == 0:
                    return [float(item[4]) for item in data['result']['list']]
            
            elif exchange == "MEXC":
                url = f"https://api.mexc.com/api/v3/klines?symbol={symbol}USDT&interval=1d&limit=7"
                response = self.session.get(url, timeout=5)
                response.raise_for_status()
                data = response.json()
                return [float(item[4]) for item in data]
        except Exception as e:
            print(f"Ошибка получения исторических данных {exchange} для {symbol}: {e}")
            return None
    
    def update_week_charts(self):
        """Обновление недельных графиков"""
        symbol = self.crypto_var.get()
        dates = [datetime.now() - timedelta(days=i) for i in range(6, -1, -1)]
        
        try:
            for i, exchange in enumerate(self.exchanges):
                # Получение исторических данных
                data = self.fetch_historical_data(symbol, exchange)
                
                if data and len(data) == 7:
                    # Очистка и перерисовка графика
                    self.weekly_axes[i].clear()
                    self.weekly_axes[i].plot(dates, data[-7:], color=GREEN_COLOR, linewidth=1)
                    
                    # Настройка осей
                    self.weekly_axes[i].tick_params(axis='x', colors=TEXT_COLOR, labelsize=7, rotation=45)
                    self.weekly_axes[i].tick_params(axis='y', colors=TEXT_COLOR, labelsize=8)
                    self.weekly_axes[i].yaxis.set_major_formatter(plt.FormatStrFormatter('%.2f'))
                    self.weekly_axes[i].xaxis.set_major_formatter(DateFormatter('%d.%m'))
                    self.weekly_figures[i].subplots_adjust(bottom=0.25, left=0.15)
                    
                    # Настройка заголовков
                    self.weekly_axes[i].set_title(f'{exchange} - {symbol} (7 дней)', color=TEXT_COLOR, fontsize=9)
                    self.weekly_axes[i].set_xlabel('Дата', color=TEXT_COLOR, fontsize=8)
                    self.weekly_axes[i].set_ylabel('Цена (USD)', color=TEXT_COLOR, fontsize=8)
                    
                    # Настройка границ
                    for spine in self.weekly_axes[i].spines.values():
                        spine.set_color(ACCENT_COLOR)
                    
                    # Автомасштабирование
                    self.weekly_axes[i].relim()
                    self.weekly_axes[i].autoscale_view()
                    
                    # Обновление canvas через очередь UI
                    self.ui_queue.put((self.weekly_canvases[i].draw, ()))
                else:
                    print(f"Недостаточно данных для {exchange} (получено {len(data) if data else 0} точек)")
        
        except Exception as e:
            print(f"Ошибка обновления недельных графиков: {e}")
    
    def fetch_bid_ask_prices(self, symbol, exchange):
        """Получение цен покупки и продажи для указанной криптовалюты на бирже"""
        try:
            if exchange == "Bybit":
                url = f"https://api.bybit.com/v5/market/orderbook?category=spot&symbol={symbol}USDT&limit=1"
                response = self.session.get(url, timeout=3)
                response.raise_for_status()
                data = response.json()
                if data['retCode'] == 0:
                    return float(data['result']['a'][0][0]), float(data['result']['b'][0][0])
            
            elif exchange == "MEXC":
                url = f"https://api.mexc.com/api/v3/depth?symbol={symbol}USDT&limit=1"
                response = self.session.get(url, timeout=3)
                response.raise_for_status()
                data = response.json()
                return float(data['asks'][0][0]), float(data['bids'][0][0])
            
            elif exchange == "Binance":
                url = f"https://api.binance.com/api/v3/depth?symbol={symbol}USDT&limit=1"
                response = self.session.get(url, timeout=3)
                response.raise_for_status()
                data = response.json()
                return float(data['asks'][0][0]), float(data['bids'][0][0])
        except Exception as e:
            print(f"Ошибка получения цен покупки/продажи {exchange} для {symbol}: {e}")
            return None, None
    
    def calculate_spread(self, ask_price, bid_price):
        """Расчет спреда между ценой покупки и продажи"""
        if ask_price is None or bid_price is None:
            return "Ошибка"
        spread = ask_price - bid_price
        spread_percent = (spread / bid_price) * 100 if bid_price != 0 else 0
        return f"{spread:,.4f} ({spread_percent:.2f}%)"
    
    def update_price_table(self, symbol):
        """Обновление таблицы с ценами по биржам"""
        for i, exchange in enumerate(self.exchanges):
            # Получение цен покупки и продажи
            ask_price, bid_price = self.fetch_bid_ask_prices(symbol, exchange)
            
            if ask_price is not None and bid_price is not None:
                # Обновление UI через очередь
                self.ui_queue.put((
                    lambda b, s, d, i=i: (
                        self.price_labels[i][0].config(text=f"${b:,.4f}"),
                        self.price_labels[i][1].config(text=f"${s:,.4f}"),
                        self.price_labels[i][2].config(text=d)
                    ),
                    (bid_price, ask_price, self.calculate_spread(ask_price, bid_price))
                ))
            else:
                self.ui_queue.put((
                    lambda i=i: (
                        self.price_labels[i][0].config(text="Ошибка"),
                        self.price_labels[i][1].config(text="Ошибка"),
                        self.price_labels[i][2].config(text="Ошибка")
                    ),
                    ()
                ))
    
    def fetch_current_price(self, symbol, exchange):
        """Получение текущей цены криптовалюты на бирже"""
        try:
            if exchange == "Bybit":
                url = f"https://api.bybit.com/v5/market/tickers?category=spot&symbol={symbol}USDT"
                response = self.session.get(url, timeout=3)
                response.raise_for_status()
                data = response.json()
                if data['retCode'] == 0 and data['result']['list']:
                    return float(data['result']['list'][0]['lastPrice'])
            
            elif exchange == "MEXC":
                url = f"https://api.mexc.com/api/v3/ticker/24hr?symbol={symbol}USDT"
                response = self.session.get(url, timeout=3)
                response.raise_for_status()
                data = response.json()
                if 'lastPrice' in data:
                    return float(data['lastPrice'])
            
            elif exchange == "Binance":
                url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}USDT"
                response = self.session.get(url, timeout=3)
                response.raise_for_status()
                data = response.json()
                if 'lastPrice' in data:
                    return float(data['lastPrice'])
        except Exception as e:
            print(f"Ошибка получения данных {exchange} для {symbol}: {e}")
            return None
    
    def update_top10_prices(self):
        """Обновление цен для топ-10 криптовалют"""
        for i, symbol in enumerate(self.top10_symbols):
            # Получение цен с разных бирж
            bybit_price = self.fetch_current_price(symbol, "Bybit")
            mexc_price = self.fetch_current_price(symbol, "MEXC")
            binance_price = self.fetch_current_price(symbol, "Binance")
            
            # Обновление UI через очередь
            self.ui_queue.put((
                lambda b, m, bn, i=i: (
                    self.top10_labels[i][0].config(text=f"${b:,.2f}" if b else "Ошибка"),
                    self.top10_labels[i][1].config(text=f"${m:,.2f}" if m else "Ошибка"),
                    self.top10_labels[i][2].config(text=f"${bn:,.2f}" if bn else "Ошибка")
                ),
                (bybit_price, mexc_price, binance_price)
            ))
    
    def update_best_prices(self):
        """Обновление лучших цен покупки и продажи"""
        symbol = self.crypto_var.get()
        prices = {}
        
        # Сбор цен со всех бирж
        for exchange in self.exchanges:
            price = self.fetch_current_price(symbol, exchange)
            if price is not None:
                prices[exchange] = price
        
        # Проверка наличия данных
        if not prices:
            self.ui_queue.put((
                lambda: (
                    self.best_buy_label.config(text="Невозможно определить цены: ошибка данных"),
                    self.best_sell_label.config(text="")
                ),
                ()
            ))
            return
        
        # Определение лучших цен
        best_buy_exchange = min(prices, key=prices.get)
        best_buy_price = prices[best_buy_exchange]
        
        best_sell_exchange = max(prices, key=prices.get)
        best_sell_price = prices[best_sell_exchange]
        
        # Обновление UI
        self.ui_queue.put((
            lambda: (
                self.best_buy_label.config(text=f"{best_buy_exchange}: ${best_buy_price:,.4f}"),
                self.best_sell_label.config(text=f"{best_sell_exchange}: ${best_sell_price:,.4f}")
            ),
            ()
        ))
    
    def update_data(self):
        """Основной метод обновления всех данных"""
        try:
            symbol = self.crypto_var.get()
            self.update_best_prices()
            self.update_price_table(symbol)
            self.update_week_charts()
            self.update_top10_prices()
        except Exception as e:
            print(f"Ошибка при обновлении данных: {e}")
            raise
        finally:
            if hasattr(self, 'loading_animation'):
                self.ui_queue.put((self.hide_loading, ()))
    
    def auto_update(self):
        """Автоматическое обновление данных в отдельном потоке"""
        while self.running:
            try:
                self.update_data()
            except Exception as e:
                print(f"Ошибка при автоматическом обновлении: {e}")
            
            # Пауза между обновлениями
            for _ in range(self.update_interval):
                if not self.running:
                    return
                time.sleep(1)
    
    def on_close(self):
        """Обработчик закрытия приложения"""
        self.running = False
        if self.update_thread.is_alive():
            self.update_thread.join(timeout=1)
        if self.realtime_thread.is_alive():
            self.realtime_thread.join(timeout=1)
        self.session.close()
        self.root.destroy()

# ==============================================
# ТОЧКА ВХОДА
# ==============================================
if __name__ == "__main__":
    login_root = tk.Tk()
    login_app = LoginWindow(login_root)
    login_root.mainloop()