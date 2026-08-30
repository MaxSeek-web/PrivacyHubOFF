"""
PrivacyHub — Desktop приложение для создания и управления правилами конфиденциальности.
Возможности:
- Создание, редактирование, удаление правил
- Прикрепление скриншотов/изображений
- Экспорт в .txt, .md и .pdf
- Окно предпросмотра
- Публикация с генерацией share-ссылки (base64 JSON)
- Публичные правила (встроенные шаблоны PrivacyHub)
- Настройки темы (Dark/Light) и языка (EN/RU/KK)
- Автоперевод через MyMemory API
- Вход по email/password
"""

import json
import os
import shutil
import base64
import urllib.request
import urllib.parse
import threading
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, filedialog, simpledialog, Toplevel

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
from fpdf import FPDF

APP_NAME = "PrivacyHub"
APP_VERSION = "2.1.0"
DATA_DIR = os.path.join(os.path.expanduser("~"), ".privacyhub")
DB_FILE = os.path.join(DATA_DIR, "privacy_rules.json")
EXPORTS_DIR = os.path.join(DATA_DIR, "exports")
IMAGES_DIR = os.path.join(DATA_DIR, "images")

THEMES = {"dark": "darkly", "light": "litera"}
LANGS = {"en": "English", "ru": "Русский", "kk": "Қазақша"}

I18N = {
    "en": {
        "app_title": "PrivacyHub", "new_rule": "➕ New Rule", "delete": "🗑️ Delete",
        "save": "💾 Save", "preview": "👁️ Preview", "print_pdf": "📄 Print PDF",
        "downloads": "📥 Downloads", "open_exports": "📂 Open Export Folder",
        "search": "Search", "rule_name": "Rule Name:", "version": "Version:",
        "status": "Status:", "content": "📝 Rule Content", "images": "🖼️ Attached Images:",
        "add_image": "➕ Add Screenshot", "remove_image": "❌ Remove Selected",
        "templates": "⚡ Templates:", "draft": "Draft", "under_review": "Under Review",
        "approved": "Approved", "archived": "Archived", "publish": "🌐 Publish",
        "public_rules": "📢 Public Rules", "settings": "⚙️ Settings",
        "community_rules": "🌍 Community", "authors_rules": "✍️ Authors",
        "community_rules_title": "🌍 Community Rules", "authors_rules_title": "✍️ Authors' Rules",
        "theme_dark": "Dark Theme", "theme_light": "Light Theme", "language": "Language",
        "copy_link": "Copy Link", "share_msg": "Shareable code copied to clipboard:",
        "confirm_publish": "Publish this rule? A shareable code will be generated.",
        "published": "Published", "public_rules_title": "📢 Public Rules",
        "publish_to": "Publish to:", "publish_community": "Community", "publish_authors": "Authors",
        "banned_message": "You are banned from publishing rules.", "admin_panel": "🛡️ Admin",
        "admin_title": "🛡️ Admin Panel", "admin_users": "Registered Users", "ban": "Ban", "unban": "Unban",
        "user_banned": "Banned", "user_active": "Active",
        "save_to_my": "Save to My Rules", "select_rule_warn": "Please select or create a rule first.",
        "translate_wait": "Translating...", "translate_done": "Translation complete.",
        "ok": "OK", "cancel": "Cancel", "rules_list": "📁 Rules",
        "choose_theme": "Theme", "choose_lang": "Language", "apply": "Apply",
        "restart_needed": "Settings applied. The theme updated.", "status_ready": "Ready",
        "saved": "Saved", "deleted": "Deleted", "published_rules": "Published rules from PrivacyHub",
        "login": "🚪 Login", "logout": "🚪 Logout", "register": "📝 Register",
        "email": "Email", "password": "Password", "confirm_password": "Confirm Password",
        "login_btn": "Login", "register_btn": "Register",
        "logged_in": "Logged in successfully!", "logged_out": "Logged out.",
        "invalid_credentials": "Invalid email or password.", "email_exists": "Email already registered.",
        "password_mismatch": "Passwords do not match.", "password_short": "Password too short (min 4).",
        "invalid_email": "Invalid email address.", "auth": "Auth",
        "enter_code": "Enter verification code", "code": "Code", "verify": "Verify", "back": "Back",
        "invalid_code": "Invalid code", "attempts_left": "attempts left",
        "too_many_attempts": "Too many attempts. Locked for", "locked": "Locked. Try again in",
        "seconds": "seconds", "minutes": "minutes",
        "verify_prompt": "A verification code has been sent to your email. Enter it below.", "demo_code": "Code",
        "login_required_publish": "Please log in to publish rules.", "only_admin_community": "Only admin can publish to Community.", "delete_public": "🗑️ Delete from Public", "delete_from_public_confirm": "Delete this public rule?", "cannot_delete_builtin": "Cannot delete built-in template rules.",
        "comments": "💬 Comments", "comments_title": "💬 Comments", "add_comment": "➕ Add Comment", "comment_author": "Author", "comment_text": "Comment", "comment_date": "Date", "no_comments": "No comments yet.", "comment_placeholder": "Enter your comment...", "comment_added": "Comment added.",
    },
    "ru": {
        "app_title": "PrivacyHub", "new_rule": "➕ Новое правило", "delete": "🗑️ Удалить",
        "save": "💾 Сохранить", "preview": "👁️ Предпросмотр", "print_pdf": "📄 Печать в PDF",
        "downloads": "📥 Загрузки", "open_exports": "📂 Открыть папку экспорта",
        "search": "Поиск", "rule_name": "Название правила:", "version": "Версия:",
        "status": "Статус:", "content": "📝 Содержание правила", "images": "🖼️ Прикреплённые изображения:",
        "add_image": "➕ Добавить скриншот", "remove_image": "❌ Удалить выбранное",
        "templates": "⚡ Шаблоны:", "draft": "Черновик", "under_review": "На рассмотрении",
        "approved": "Утверждено", "archived": "Архив", "publish": "🌐 Опубликовать",
        "public_rules": "📢 Другие правила", "settings": "⚙️ Настройки",
        "community_rules": "🌍 Сообщество", "authors_rules": "✍️ Авторы",
        "community_rules_title": "🌍 Правила от сообщества", "authors_rules_title": "✍️ Правила от авторов",
        "theme_dark": "Тёмная тема", "theme_light": "Светлая тема", "language": "Язык",
        "copy_link": "Копировать ссылку", "share_msg": "Код для публикации скопирован в буфер:",
        "confirm_publish": "Опубликовать правило? Будет создан share-код.",
        "published": "Опубликовано", "public_rules_title": "📢 Публичные правила",
        "publish_to": "Опубликовать в:", "publish_community": "Сообщество", "publish_authors": "Авторы",
        "banned_message": "Вам запрещено публиковать правила.", "admin_panel": "🛡️ Админ",
        "admin_title": "🛡️ Панель администратора", "admin_users": "Зарегистрированные пользователи", "ban": "Забанить", "unban": "Разбанить",
        "user_banned": "Забанен", "user_active": "Активен",
        "save_to_my": "Сохранить в Мои правила", "select_rule_warn": "Сначала выберите или создайте правило.",
        "translate_wait": "Перевод...", "translate_done": "Перевод завершён.",
        "ok": "OK", "cancel": "Отмена", "rules_list": "📁 Репозитории правил",
        "choose_theme": "Тема", "choose_lang": "Язык", "apply": "Применить",
        "restart_needed": "Настройки применены. Тема обновлена.", "status_ready": "Готово",
        "saved": "Сохранено", "deleted": "Удалено", "published_rules": "Опубликованные правила PrivacyHub",
        "login": "🚪 Вход", "logout": "🚪 Выйти", "register": "📝 Регистрация",
        "email": "Email", "password": "Пароль", "confirm_password": "Подтвердите пароль",
        "login_btn": "Войти", "register_btn": "Зарегистрироваться",
        "logged_in": "Вход выполнен!", "logged_out": "Вы вышли.",
        "invalid_credentials": "Неверный email или пароль.", "email_exists": "Email уже зарегистрирован.",
        "password_mismatch": "Пароли не совпадают.", "password_short": "Пароль слишком короткий (мин 4).",
        "invalid_email": "Некорректный email.", "auth": "Вход",
        "enter_code": "Введите код подтверждения", "code": "Код", "verify": "Подтвердить", "back": "Назад",
        "invalid_code": "Неверный код", "attempts_left": "попыток осталось",
        "too_many_attempts": "Слишком много попыток. Блокировка на", "locked": "Заблокировано. Попробуйте через",
        "seconds": "секунд", "minutes": "минут",
        "verify_prompt": "Код подтверждения отправлен на вашу почту. Введите его ниже.", "demo_code": "Код",
        "login_required_publish": "Войдите в систему, чтобы публиковать правила.", "only_admin_community": "Только администратор может публиковать в Сообщество.", "delete_public": "🗑️ Удалить из публичных", "delete_from_public_confirm": "Удалить это публичное правило?", "cannot_delete_builtin": "Нельзя удалить встроенные шаблоны.",
        "comments": "💬 Комментарии", "comments_title": "💬 Комментарии", "add_comment": "➕ Добавить комментарий", "comment_author": "Автор", "comment_text": "Комментарий", "comment_date": "Дата", "no_comments": "Пока нет комментариев.", "comment_placeholder": "Введите ваш комментарий...", "comment_added": "Комментарий добавлен.",
    },
    "kk": {
        "app_title": "PrivacyHub", "new_rule": "➕ Жаңа ереже", "delete": "🗑️ Жою",
        "save": "💾 Сақтау", "preview": "👁️ Алдын ала қарау", "print_pdf": "📄 PDF-ке басып шығару",
        "downloads": "📥 Жүктеулер", "open_exports": "📂 Экспорттау бумасын ашу",
        "search": "Іздеу", "rule_name": "Ереже атауы:", "version": "Нұсқа:",
        "status": "Күй:", "content": "📝 Ереже мазмұны", "images": "🖼️ Тіркелген суреттер:",
        "add_image": "➕ Скриншот қосу", "remove_image": "❌ Таңдалғанды жою",
        "templates": "⚡ Үлгілер:", "draft": "Жоба", "under_review": "Қаралуда",
        "approved": "Бекітілді", "archived": "Мұрағат", "publish": "🌐 Жариялау",
        "public_rules": "📢 Басқа ережелер", "settings": "⚙️ Параметрлер",
        "community_rules": "🌍 Қоғамдық", "authors_rules": "✍️ Авторлар",
        "community_rules_title": "🌍 Қоғамдық ережелер", "authors_rules_title": "✍️ Авторлар ережелері",
        "theme_dark": "Қараңғы тема", "theme_light": "Жарық тема", "language": "Тіл",
        "copy_link": "Сілтемені көшіру", "share_msg": "Жариялау коды алмасу буферіне көшірілді:",
        "confirm_publish": "Ережені жариялау? Ортақ код жасалады.",
        "published": "Жарияланды", "public_rules_title": "📢 Ашық ережелер",
        "publish_to": "Жариялау:", "publish_community": "Қоғамдық", "publish_authors": "Авторлар",
        "banned_message": "Сізге ережелерді жариялауға тыйым салынған.", "admin_panel": "🛡️ Админ",
        "admin_title": "🛡️ Әкімші панелі", "admin_users": "Тіркелген пайдаланушылар", "ban": "Бұғаттау", "unban": "Бұғатты ашу",
        "user_banned": "Бұғатталған", "user_active": "Белсенді",
        "save_to_my": "Менің ережелеріме сақтау", "select_rule_warn": "Алдымен ережені таңдаңыз немесе жасаңыз.",
        "translate_wait": "Аудару...", "translate_done": "Аударма аяқталды.",
        "ok": "OK", "cancel": "Бас тарту", "rules_list": "📁 Ережелер репозиторийі",
        "choose_theme": "Тема", "choose_lang": "Тіл", "apply": "Қолдану",
        "restart_needed": "Параметрлер қолданылды. Тема жаңартылды.", "status_ready": "Дайын",
        "saved": "Сақталды", "deleted": "Жойылды", "published_rules": "PrivacyHub жарияланған ережелері",
        "login": "🚪 Кіру", "logout": "🚪 Шығу", "register": "📝 Тіркелу",
        "email": "Email", "password": "Құпия сөз", "confirm_password": "Құпия сөзді растаңыз",
        "login_btn": "Кіру", "register_btn": "Тіркелу",
        "logged_in": "Кіру сәтті!", "logged_out": "Сіз шықтыңыз.",
        "invalid_credentials": "Қате email немесе құпия сөз.", "email_exists": "Email бұрын тіркелген.",
        "password_mismatch": "Құпия сөздер сәйкес келмейді.", "password_short": "Құпия сөз тым қысқа (мин 4).",
        "invalid_email": "Қате email.", "auth": "Кіру",
        "enter_code": "Растау кодын енгізіңіз", "code": "Код", "verify": "Растау", "back": "Артқа",
        "invalid_code": "Қате код", "attempts_left": "тырлық қалды",
        "too_many_attempts": "Тым көп тырлық. Бұғаттау мерзімі", "locked": "Бұғатталды. Қайтадан қол жеткізу",
        "seconds": "секундтан кейін", "minutes": "минуттан кейін",
        "verify_prompt": "Растау коды электрондық поштаңызға жіберілді. Төменде енгізіңіз.", "demo_code": "Код",
        "login_required_publish": "Ережелерді жариялау үшін жүйеге кіріңіз.", "only_admin_community": "Тек әкімші қоғамдыққа жариялай алады.", "delete_public": "🗑️ Ашықтан жою", "delete_from_public_confirm": "Бұл ашық ережені жоясыз ба?", "cannot_delete_builtin": "Кіріктірілген үлгілерді жоюға болмайды.",
        "comments": "💬 Пікірлер", "comments_title": "💬 Пікірлер", "add_comment": "➕ Пікір қосу", "comment_author": "Автор", "comment_text": "Пікір", "comment_date": "Күні", "no_comments": "Әлі пікірлер жоқ.", "comment_placeholder": "Пікіріңізді енгізіңіз...", "comment_added": "Пікір қосылды.",
    },
}

PUBLIC_RULES = [
    {
        "id": "ph1", "title": "PrivacyHub Privacy Policy", "version": "1.0", "status": "Approved",
        "content": "1. Introduction\n\nPrivacyHub (\"we\", \"our\", or \"us\") is committed to protecting your privacy...\n\n2. Information We Collect\n\nWe may collect personal information that you voluntarily provide...\n\n3. Use of Your Information\n\nWe use the information we collect to: provide and maintain our services...\n\n4. Sharing Your Information\n\nWe do not sell, trade, or otherwise transfer your personal information...\n\n5. Data Security\n\nWe implement a variety of security measures...\n\n6. Your Rights\n\nDepending on your location, you may have rights including...\n\n7. Changes to This Policy\n\nWe may update this Privacy Policy from time to time...\n\n8. Contact Us\n\nIf you have questions about this Privacy Policy, please contact us...",
        "lang": "en", "author": "PrivacyHub", "date": "2026-08-29",
    },
    {
        "id": "ph2", "title": "PrivacyHub Условия использования", "version": "1.0", "status": "Approved",
        "content": "1. Общие положения\n\nНастоящие Условия использования регулируют отношения...\n\n2. Принятие условий\n\nРегистрируясь или используя наше приложение...\n\n3. Права и обязанности пользователя\n\nПользователь обязуется: предоставлять достоверную информацию...\n\n4. Интеллектуальная собственность\n\nВсе материалы, доступные через приложение...\n\n5. Ограничение ответственности\n\nPrivacyHub не несёт ответственности...\n\n6. Изменение условий\n\nМы оставляем за собой право в любое время изменять...\n\n7. Прекращение действия\n\nМы можем приостановить или прекратить ваш доступ...\n\n8. Контакты\n\nПо всем вопросам обращайтесь через форму обратной связи...",
        "lang": "ru", "author": "PrivacyHub", "date": "2026-08-29",
    },
    {
        "id": "ph3", "title": "PrivacyHub Cookie саясаты", "version": "1.0", "status": "Approved",
        "content": "1. Кіріспе\n\nБұл Cookie саясаты PrivacyHub қолданбасында cookie файлдары...\n\n2. Cookie деген не?\n\nCookie — бұл веб-сайт сіздің құрылғыңызға сақтайтын шағын деректер файлы...\n\n3. Қандай cookie қолданамыз?\n\nҚажетті cookie, Аналитикалық cookie, Функционалдық cookie...\n\n4. Cookie басқару\n\nСіз браузеріңіздің баптаулары арқылы cookie-лерді өшіре аласыз...\n\n5. Үшінші тараптар\n\nБіз үшінші тараптардың cookie-лерін қолданбауға тырысамыз...\n\n6. Саясатқа өзгерістер\n\nБұл саясатты кез келген уақытта жаңарта аламыз...\n\n7. Байланыс\n\nCookie саясаты бойынша сұрақтар болса...",
        "lang": "kk", "author": "PrivacyHub", "date": "2026-08-29",
    },
]

DEFAULT_TEMPLATES = {
    "Общие положения": "1.1. Настоящие Правила конфиденциальности определяют порядок обработки и защиты персональных данных пользователей.\n\n1.2. Используя сервис, вы выражаете согласие с условиями настоящих Правил.",
    "Сбор данных": "2.1. Мы собираем только те данные, которые необходимы для предоставления услуг.\n\n2.2. К категориям собираемых данных относятся: имя, адрес электронной почты, технические данные устройства.",
    "Хранение и защита": "3.1. Данные хранятся на защищённых серверах.\n\n3.2. Доступ к данным имеют только уполномоченные сотрудники.\n\n3.3. Мы применяем шифрование и другие меры защиты.",
    "Передача третьим лицам": "4.1. Персональные данные не передаются третьим лицам без согласия пользователя.\n\n4.2. Исключение составляют случаи, предусмотренные законодательством.",
    "Права пользователя": "5.1. Пользователь имеет право на доступ к своим данным.\n\n5.2. Пользователь может требовать исправления, удаления или ограничения обработки данных.",
}


def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)


def load_database():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_database(data):
    ensure_dirs()
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def migrate_db(db):
    changed = False
    if "rules" not in db:
        db["rules"] = {}
        for k in list(db.keys()):
            if not k.startswith("_") and k not in ("downloads", "rules") and isinstance(db[k], dict) and "title" in db[k]:
                db["rules"][k] = db.pop(k)
                changed = True
    if "downloads" not in db:
        db["downloads"] = []
        changed = True
    if "_settings" not in db:
        db["_settings"] = {"theme": "dark", "lang": "en"}
        changed = True
    if "_users" not in db:
        db["_users"] = []
        changed = True
    if "_current_user" not in db:
        db["_current_user"] = None
        changed = True
    if "_email_codes" not in db:
        db["_email_codes"] = {}
        changed = True
    if "_public_community" not in db:
        db["_public_community"] = []
        changed = True
    if "_public_authors" not in db:
        db["_public_authors"] = []
        changed = True
    # Seed demo account and migrate banned flag
    users = db.get("_users", [])
    for u in users:
        if "banned" not in u:
            u["banned"] = False
            changed = True
    if not any(u.get("email", "").lower() == "testers@example.ru" for u in users):
        users.append({"email": "testers@example.ru", "password_hash": base64.b64encode(b"testers").decode(), "name": "Tester", "banned": False})
        db["_users"] = users
        changed = True
    # Migrate public lists to include unique pub_id for old entries
    import random
    for key in ("_public_community", "_public_authors"):
        if key in db:
            for r in db[key]:
                if "pub_id" not in r:
                    r["pub_id"] = f"legacy_{r.get('id', 'unknown')}_{random.randint(10000,99999)}"
                    changed = True
    return changed


class PrivacyHubApp:
    def __init__(self, root):
        self.root = root
        self.db = load_database()
        if migrate_db(self.db):
            save_database(self.db)
        self.current_rule_id = None
        self.settings = self.db.setdefault("_settings", {"theme": "dark", "lang": "en"})
        self.lang = self.settings.get("lang", "en")
        self.theme = self.settings.get("theme", "dark")
        self._tk_images = []
        self._thumb_size = (120, 120)
        self.style = ttk.Style()
        self.root.title(f"{self._t('app_title')} v{APP_VERSION}")
        self.root.geometry("1600x950")
        self._build_ui()
        self._refresh_list()

    def _t(self, key):
        return I18N.get(self.lang, I18N["en"]).get(key, key)

    def _apply_widget_colors(self):
        if self.theme == "dark":
            bg, fg, select_bg = "#1e1e1e", "#e0e0e0", "#0d6efd"
        else:
            bg, fg, select_bg = "#ffffff", "#212529", "#0d6efd"
        self.rule_list.config(bg=bg, fg=fg, selectbackground=select_bg)
        self.text_editor.config(bg=bg, fg=fg, insertbackground=fg)
        self.images_listbox.config(bg=bg, fg=fg, selectbackground=select_bg)

    def _build_ui(self):
        toolbar = ttk.Frame(self.root, padding=5)
        toolbar.pack(fill=X, side=TOP)
        ttk.Label(toolbar, text=f"🛡️ {self._t('app_title')}", font=("Segoe UI", 16, "bold")).pack(side=LEFT, padx=10)
        ttk.Button(toolbar, text=self._t("new_rule"), bootstyle=SUCCESS, command=self._create_new_rule).pack(side=LEFT, padx=5)
        ttk.Button(toolbar, text=self._t("delete"), bootstyle=DANGER, command=self._delete_current_rule).pack(side=LEFT, padx=5)
        ttk.Button(toolbar, text=self._t("save"), bootstyle=PRIMARY, command=self._save_current_rule).pack(side=LEFT, padx=5)
        ttk.Button(toolbar, text=self._t("preview"), bootstyle=WARNING, command=self._show_preview).pack(side=LEFT, padx=5)
        ttk.Button(toolbar, text=self._t("print_pdf"), bootstyle=INFO, command=self._export_pdf).pack(side=LEFT, padx=5)
        ttk.Button(toolbar, text=self._t("publish"), bootstyle=PRIMARY, command=self._do_publish).pack(side=LEFT, padx=5)
        ttk.Button(toolbar, text=self._t("community_rules"), bootstyle=INFO, command=self._show_community_rules).pack(side=LEFT, padx=5)
        ttk.Button(toolbar, text=self._t("authors_rules"), bootstyle=INFO, command=self._show_authors_rules).pack(side=LEFT, padx=5)
        ttk.Button(toolbar, text=self._t("comments"), bootstyle=INFO, command=self._show_comments).pack(side=LEFT, padx=5)
        self.admin_btn = ttk.Button(toolbar, text=self._t("admin_panel"), bootstyle=DANGER, command=self._show_admin_panel)
        ttk.Button(toolbar, text=self._t("downloads"), bootstyle=SECONDARY, command=self._show_downloads).pack(side=LEFT, padx=5)
        ttk.Button(toolbar, text=self._t("settings"), bootstyle=SECONDARY, command=self._show_settings).pack(side=LEFT, padx=5)
        ttk.Button(toolbar, text=self._t("open_exports"), bootstyle=SECONDARY, command=self._open_exports_folder).pack(side=LEFT, padx=5)

        self.auth_btn = ttk.Button(toolbar, text=self._t("login"), bootstyle=SECONDARY, command=self._show_auth)
        self.auth_btn.pack(side=LEFT, padx=5)
        self._update_auth_ui()

        search_frame = ttk.Frame(toolbar)
        search_frame.pack(side=RIGHT, padx=10)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self._refresh_list())
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=25)
        self.search_entry.pack(side=LEFT)
        ttk.Button(search_frame, text="🔍", bootstyle=SECONDARY, command=self._refresh_list).pack(side=LEFT)

        paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg="#222222" if self.theme == "dark" else "#cccccc")
        paned.pack(fill=BOTH, expand=True, padx=5, pady=5)
        left_frame = ttk.Frame(paned, width=340)
        paned.add(left_frame, minsize=280)
        ttk.Label(left_frame, text=self._t("rules_list"), font=("Segoe UI", 12, "bold")).pack(anchor=W, padx=10, pady=(10, 5))
        self.rule_list = tk.Listbox(left_frame, bg="#1e1e1e", fg="#e0e0e0", selectbackground="#0d6efd",
                                    font=("Consolas", 11), borderwidth=0, highlightthickness=0)
        self.rule_list.pack(fill=BOTH, expand=True, padx=10, pady=5)
        self.rule_list.bind("<<ListboxSelect>>", self._on_select_rule)
        ttk.Scrollbar(self.rule_list, command=self.rule_list.yview, bootstyle="round")
        self.stats_label = ttk.Label(left_frame, text=f"{self._t('rules_list')}: 0", font=("Segoe UI", 10))
        self.stats_label.pack(anchor=W, padx=10, pady=5)

        right_frame = ttk.Frame(paned)
        paned.add(right_frame)
        meta_frame = ttk.Frame(right_frame, padding=10)
        meta_frame.pack(fill=X)
        ttk.Label(meta_frame, text=self._t("rule_name"), font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky=W, pady=5)
        self.title_var = tk.StringVar()
        self.title_entry = ttk.Entry(meta_frame, textvariable=self.title_var, font=("Segoe UI", 12))
        self.title_entry.grid(row=0, column=1, sticky=EW, pady=5, padx=10)
        ttk.Label(meta_frame, text=self._t("version"), font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky=W, pady=5)
        self.version_var = tk.StringVar(value="1.0")
        ttk.Entry(meta_frame, textvariable=self.version_var, font=("Segoe UI", 11), width=10).grid(row=1, column=1, sticky=W, pady=5, padx=10)
        ttk.Label(meta_frame, text=self._t("status"), font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky=W, pady=5)
        statuses = [self._t("draft"), self._t("under_review"), self._t("approved"), self._t("archived")]
        self.status_var = tk.StringVar(value=self._t("draft"))
        self.status_combo = ttk.Combobox(meta_frame, values=statuses, textvariable=self.status_var, width=20)
        self.status_combo.grid(row=2, column=1, sticky=W, pady=5, padx=10)
        meta_frame.columnconfigure(1, weight=1)
        ttk.Separator(right_frame, orient=HORIZONTAL).pack(fill=X, padx=10)

        editor_frame = ttk.Frame(right_frame, padding=10)
        editor_frame.pack(fill=BOTH, expand=True)
        ttk.Label(editor_frame, text=self._t("content"), font=("Segoe UI", 11, "bold")).pack(anchor=W)
        self.text_editor = ScrolledText(editor_frame, wrap=tk.WORD, font=("Consolas", 12),
                                        bg="#1e1e1e", fg="#e0e0e0", insertbackground="white", height=18)
        self.text_editor.pack(fill=BOTH, expand=True, pady=5)

        img_frame_outer = ttk.Frame(right_frame, padding=10)
        img_frame_outer.pack(fill=X, side=BOTTOM)
        img_header = ttk.Frame(img_frame_outer)
        img_header.pack(fill=X)
        ttk.Label(img_header, text=self._t("images"), font=("Segoe UI", 10, "bold")).pack(side=LEFT)
        ttk.Button(img_header, text=self._t("add_image"), bootstyle=SUCCESS, command=self._add_image).pack(side=LEFT, padx=10)
        ttk.Button(img_header, text=self._t("remove_image"), bootstyle=DANGER, command=self._remove_image).pack(side=LEFT)
        self.images_listbox = tk.Listbox(img_frame_outer, bg="#1e1e1e", fg="#e0e0e0", selectbackground="#0d6efd",
                                         font=("Consolas", 10), borderwidth=0, highlightthickness=0, height=6)
        self.images_listbox.pack(fill=X, pady=5)
        self.images_listbox.bind("<<ListboxSelect>>", self._on_image_select)
        self.thumb_label = ttk.Label(img_frame_outer, text="(preview)")
        self.thumb_label.pack(anchor=W)

        template_frame = ttk.Frame(right_frame, padding=10)
        template_frame.pack(fill=X, side=BOTTOM)
        ttk.Label(template_frame, text=self._t("templates"), font=("Segoe UI", 10, "bold")).pack(side=LEFT)
        for name in DEFAULT_TEMPLATES:
            ttk.Button(template_frame, text=name, bootstyle=SECONDARY, command=lambda n=name: self._insert_template(n)).pack(side=LEFT, padx=3)

        self.status_bar = ttk.Label(self.root, text=self._t("status_ready"), relief=SUNKEN, anchor=W, padding=5)
        self.status_bar.pack(fill=X, side=BOTTOM)
        self._apply_widget_colors()
        self._setup_shortcuts()

    def _setup_shortcuts(self):
        self.root.bind('<Control-n>', lambda e: self._create_new_rule())
        self.root.bind('<Control-f>', lambda e: self._focus_search())
        self.root.bind('<Control-s>', lambda e: self._save_current_rule())
        self.root.bind('<Control-a>', lambda e: self._open_admin_shortcut())
        self.root.bind('<Control-Alt-s>', lambda e: self._show_settings())
        self.root.bind('<Control-d>', lambda e: self._show_downloads())

    def _focus_search(self):
        self.search_entry.focus_set()
        self.search_entry.select_range(0, tk.END)

    def _open_admin_shortcut(self):
        user = self.db.get("_current_user")
        if user and user.lower() == "testers@example.ru":
            self._show_admin_panel()
        else:
            self.status_bar.config(text="Admin only.")

    def _update_auth_ui(self):
        user = self.db.get("_current_user")
        if user:
            self.auth_btn.config(text=f"👤 {user} | {self._t('logout')}", command=self._do_logout)
            if user.lower() == "testers@example.ru":
                self.admin_btn.pack(side=LEFT, padx=5)
            else:
                self.admin_btn.pack_forget()
        else:
            self.auth_btn.config(text=self._t("login"), command=self._show_auth)
            self.admin_btn.pack_forget()

    CODE_MAX_ATTEMPTS = 3
    CODE_LOCK_MINUTES = 5
    CODE_TTL_MS = 10 * 60 * 1000

    def _get_email_codes(self):
        return self.db.get("_email_codes", {})

    def _save_email_codes(self, codes):
        self.db["_email_codes"] = codes
        save_database(self.db)

    def _generate_email_code(self, email):
        import random
        code = str(random.randint(100000, 999999))
        codes = self._get_email_codes()
        codes[email.lower()] = {"code": code, "attempts": 0, "lockUntil": 0, "created": datetime.now().isoformat()}
        self._save_email_codes(codes)
        return code

    def _is_email_locked(self, email):
        codes = self._get_email_codes()
        rec = codes.get(email.lower())
        if not rec:
            return False
        lock = rec.get("lockUntil", 0)
        if isinstance(lock, str):
            try:
                from datetime import datetime
                lock = datetime.fromisoformat(lock).timestamp() * 1000
            except Exception:
                lock = 0
        return lock > datetime.now().timestamp() * 1000

    def _get_lock_remaining_sec(self, email):
        codes = self._get_email_codes()
        rec = codes.get(email.lower())
        if not rec:
            return 0
        lock = rec.get("lockUntil", 0)
        if isinstance(lock, str):
            try:
                lock = datetime.fromisoformat(lock).timestamp() * 1000
            except Exception:
                lock = 0
        remaining = lock - datetime.now().timestamp() * 1000
        return max(0, int(remaining / 1000))

    def _show_auth(self):
        win = Toplevel(self.root)
        win.title(self._t("auth"))
        win.geometry("420x420")
        win.transient(self.root)
        win.grab_set()

        container = ttk.Frame(win, padding=10)
        container.pack(fill=BOTH, expand=True)

        # Shared verify frame (created on demand)
        verify_frame = None
        code_label = None
        code_var = None
        verify_email = None
        verify_mode = None  # 'login' or 'register'

        # Login frame
        login_frame = ttk.Frame(container, padding=10)
        login_frame.pack(fill=BOTH, expand=True)
        ttk.Label(login_frame, text=self._t("email")).pack(anchor=W, pady=(8, 2))
        email_var = tk.StringVar()
        ttk.Entry(login_frame, textvariable=email_var).pack(fill=X, pady=2)
        ttk.Label(login_frame, text=self._t("password")).pack(anchor=W, pady=(8, 2))
        pwd_var = tk.StringVar()
        ttk.Entry(login_frame, textvariable=pwd_var, show="*").pack(fill=X, pady=2)

        def show_verify(email, code, mode):
            nonlocal verify_frame, code_label, code_var, verify_email, verify_mode
            verify_email = email
            verify_mode = mode
            login_frame.pack_forget()
            reg_frame.pack_forget()
            if verify_frame is None:
                verify_frame = ttk.Frame(container, padding=10)
                ttk.Label(verify_frame, text=self._t("verify_prompt"), wraplength=350).pack(anchor=W, pady=(8, 2))
                ttk.Label(verify_frame, text=f"{self._t('email')}: {email}", font=("Segoe UI", 10, "bold")).pack(anchor=W, pady=2)
                ttk.Label(verify_frame, text=self._t("code")).pack(anchor=W, pady=(8, 2))
                code_var = tk.StringVar()
                ttk.Entry(verify_frame, textvariable=code_var).pack(fill=X, pady=2)
                code_label = ttk.Label(verify_frame, foreground="#0d6efd", font=("Consolas", 10))
                code_label.pack(anchor=W, pady=(4, 8))
                ttk.Button(verify_frame, text=self._t("verify"), bootstyle=PRIMARY, command=submit_verify).pack(pady=10)
                ttk.Button(verify_frame, text=self._t("back"), bootstyle=SECONDARY, command=back_from_verify).pack(pady=2)
            verify_frame.pack(fill=BOTH, expand=True)
            code_label.config(text=f"{self._t('demo_code')}: {code}")
            code_var.set("")
            win.update_idletasks()

        def back_from_verify():
            verify_frame.pack_forget()
            if verify_mode == "register":
                reg_frame.pack(fill=BOTH, expand=True)
            else:
                login_frame.pack(fill=BOTH, expand=True)

        def submit_verify():
            input_code = code_var.get().strip()
            email = verify_email
            if self._is_email_locked(email):
                sec = self._get_lock_remaining_sec(email)
                messagebox.showwarning(self._t("app_title"), f"{self._t('locked')} {sec} {self._t('seconds')}")
                return
            codes = self._get_email_codes()
            rec = codes.get(email.lower())
            if not rec or rec.get("code") != input_code:
                if not rec:
                    messagebox.showerror(self._t("app_title"), self._t("invalid_code"))
                    return
                rec["attempts"] = rec.get("attempts", 0) + 1
                if rec["attempts"] >= self.CODE_MAX_ATTEMPTS:
                    rec["lockUntil"] = (datetime.now().timestamp() * 1000) + self.CODE_LOCK_MINUTES * 60 * 1000
                    self._save_email_codes(codes)
                    messagebox.showwarning(self._t("app_title"), f"{self._t('too_many_attempts')} {self.CODE_LOCK_MINUTES} {self._t('minutes')}")
                    win.destroy()
                    return
                self._save_email_codes(codes)
                left = self.CODE_MAX_ATTEMPTS - rec["attempts"]
                messagebox.showerror(self._t("app_title"), f"{self._t('invalid_code')} ({left} {self._t('attempts_left')})")
                return
            # correct
            if email.lower() in codes:
                del codes[email.lower()]
                self._save_email_codes(codes)
            if verify_mode == "login":
                found = None
                for u in self.db.get("_users", []):
                    if u["email"] == email and u.get("password_hash") == base64.b64encode(pwd_var.get().encode()).decode():
                        found = u
                        break
                if found:
                    self.db["_current_user"] = found["email"]
                else:
                    messagebox.showerror(self._t("app_title"), self._t("invalid_credentials"))
                    return
            else:
                pwd = reg_pwd.get()
                self.db.setdefault("_users", []).append({"email": email, "password_hash": base64.b64encode(pwd.encode()).decode(), "name": email.split("@")[0]})
                self.db["_current_user"] = email
            save_database(self.db)
            self._update_auth_ui()
            win.destroy()
            if verify_mode == "login":
                messagebox.showinfo(self._t("app_title"), self._t("logged_in"))
            else:
                messagebox.showinfo(self._t("app_title"), "Registered successfully!")

        def do_login():
            email = email_var.get().strip()
            pwd = pwd_var.get()
            found = None
            for u in self.db.get("_users", []):
                if u["email"] == email and u.get("password_hash") == base64.b64encode(pwd.encode()).decode():
                    found = u
                    break
            if not found:
                messagebox.showerror(self._t("app_title"), self._t("invalid_credentials"))
                return
            if self._is_email_locked(email):
                sec = self._get_lock_remaining_sec(email)
                messagebox.showwarning(self._t("app_title"), f"{self._t('locked')} {sec} {self._t('seconds')}")
                return
            code = self._generate_email_code(email)
            show_verify(email, code, "login")

        ttk.Button(login_frame, text=self._t("login_btn"), bootstyle=PRIMARY, command=do_login).pack(pady=14)
        ttk.Button(login_frame, text=self._t("register"), bootstyle=SECONDARY, command=lambda: [login_frame.pack_forget(), reg_frame.pack(fill=BOTH, expand=True)]).pack(pady=2)

        # Register frame
        reg_frame = ttk.Frame(container, padding=10)
        ttk.Label(reg_frame, text=self._t("email")).pack(anchor=W, pady=(8, 2))
        reg_email = tk.StringVar()
        ttk.Entry(reg_frame, textvariable=reg_email).pack(fill=X, pady=2)
        ttk.Label(reg_frame, text=self._t("password")).pack(anchor=W, pady=(8, 2))
        reg_pwd = tk.StringVar()
        ttk.Entry(reg_frame, textvariable=reg_pwd, show="*").pack(fill=X, pady=2)
        ttk.Label(reg_frame, text=self._t("confirm_password")).pack(anchor=W, pady=(8, 2))
        reg_pwd2 = tk.StringVar()
        ttk.Entry(reg_frame, textvariable=reg_pwd2, show="*").pack(fill=X, pady=2)

        def do_register():
            email = reg_email.get().strip()
            pwd = reg_pwd.get()
            pwd2 = reg_pwd2.get()
            if "@" not in email or "." not in email.split("@")[-1]:
                messagebox.showwarning(self._t("app_title"), self._t("invalid_email"))
                return
            if len(pwd) < 4:
                messagebox.showwarning(self._t("app_title"), self._t("password_short"))
                return
            if pwd != pwd2:
                messagebox.showwarning(self._t("app_title"), self._t("password_mismatch"))
                return
            users = self.db.setdefault("_users", [])
            if any(u["email"] == email for u in users):
                messagebox.showwarning(self._t("app_title"), self._t("email_exists"))
                return
            if self._is_email_locked(email):
                sec = self._get_lock_remaining_sec(email)
                messagebox.showwarning(self._t("app_title"), f"{self._t('locked')} {sec} {self._t('seconds')}")
                return
            code = self._generate_email_code(email)
            show_verify(email, code, "register")

        ttk.Button(reg_frame, text=self._t("register_btn"), bootstyle=PRIMARY, command=do_register).pack(pady=14)
        ttk.Button(reg_frame, text=self._t("login"), bootstyle=SECONDARY, command=lambda: [reg_frame.pack_forget(), login_frame.pack(fill=BOTH, expand=True)]).pack(pady=2)

    def _is_banned(self, email):
        if not email:
            return False
        for u in self.db.get("_users", []):
            if u.get("email", "").lower() == email.lower():
                return u.get("banned", False)
        return False

    def _do_logout(self):
        self.db["_current_user"] = None
        save_database(self.db)
        self._update_auth_ui()
        self.status_bar.config(text=self._t("logged_out"))

    def _refresh_list(self):
        self.rule_list.delete(0, tk.END)
        query = self.search_var.get().lower()
        count = 0
        rules = self.db.get("rules", {})
        for rid, rule in rules.items():
            if not isinstance(rule, dict):
                continue
            title = rule.get("title", "Untitled")
            content = rule.get("content", "")
            if query in title.lower() or query in content.lower() or not query:
                status = rule.get("status", self._t("draft"))
                emoji_map = {self._t("draft"): "📝", self._t("under_review"): "👀", self._t("approved"): "✅", self._t("archived"): "📦"}
                emoji = emoji_map.get(status, "📝")
                img_count = len(rule.get("images", []))
                img_indicator = f" 🖼️{img_count}" if img_count else ""
                self.rule_list.insert(tk.END, f"{emoji} {title}{img_indicator}")
                count += 1
        self.stats_label.config(text=f"{self._t('rules_list')}: {count}")

    def _on_select_rule(self, event):
        selection = self.rule_list.curselection()
        if not selection:
            return
        index = selection[0]
        query = self.search_var.get().lower()
        matched = [(rid, r) for rid, r in self.db.get("rules", {}).items() if isinstance(r, dict) and (not query or query in r.get("title", "").lower())]
        if index < len(matched):
            rid, rule = matched[index]
            self.current_rule_id = rid
            self.title_var.set(rule.get("title", ""))
            self.version_var.set(rule.get("version", "1.0"))
            self.status_var.set(rule.get("status", self._t("draft")))
            self.text_editor.delete("1.0", tk.END)
            self.text_editor.insert(tk.END, rule.get("content", ""))
            self._refresh_images_list()
            self.status_bar.config(text=f"{rule.get('title', '')} | {self._t('status')}: {rule.get('status', '')}")

    def _refresh_images_list(self):
        self.images_listbox.delete(0, tk.END)
        self.thumb_label.config(image="", text="(preview)")
        if not self.current_rule_id:
            return
        rules = self.db.get("rules", {})
        if self.current_rule_id not in rules:
            return
        images = rules[self.current_rule_id].get("images", [])
        for img_path in images:
            self.images_listbox.insert(tk.END, os.path.basename(img_path))

    def _on_image_select(self, event):
        selection = self.images_listbox.curselection()
        if not selection:
            return
        idx = selection[0]
        images = self.db.get("rules", {}).get(self.current_rule_id, {}).get("images", [])
        if idx < len(images):
            self._show_thumbnail(images[idx])

    def _show_thumbnail(self, path):
        if not os.path.exists(path):
            self.thumb_label.config(image="", text=f"❌ Not found: {path}")
            return
        try:
            img = Image.open(path)
            img.thumbnail(self._thumb_size)
            tk_img = ImageTk.PhotoImage(img)
            self._tk_images.clear()
            self._tk_images.append(tk_img)
            self.thumb_label.config(image=tk_img, text="")
        except Exception as e:
            self.thumb_label.config(image="", text=f"❌ Error: {e}")

    def _add_image(self):
        if not self.current_rule_id or self.current_rule_id not in self.db.get("rules", {}):
            messagebox.showwarning(self._t("app_title"), self._t("select_rule_warn"))
            return
        filepaths = filedialog.askopenfilenames(title="Select images", filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*")])
        if not filepaths:
            return
        ensure_dirs()
        for fp in filepaths:
            new_name = f"{self.current_rule_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.path.basename(fp)}"
            dest = os.path.join(IMAGES_DIR, new_name)
            try:
                shutil.copy2(fp, dest)
                self.db["rules"][self.current_rule_id].setdefault("images", []).append(dest)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy {fp}:\n{e}")
        save_database(self.db)
        self._refresh_images_list()
        self._refresh_list()
        self.status_bar.config(text=f"Images added: {len(filepaths)}")

    def _remove_image(self):
        if not self.current_rule_id or self.current_rule_id not in self.db.get("rules", {}):
            return
        selection = self.images_listbox.curselection()
        if not selection:
            messagebox.showwarning(self._t("app_title"), "Select an image to remove.")
            return
        idx = selection[0]
        images = self.db["rules"][self.current_rule_id].get("images", [])
        if idx < len(images):
            path = images[idx]
            if messagebox.askyesno("Confirm", f"Remove image?\n{os.path.basename(path)}"):
                images.pop(idx)
                try:
                    if os.path.exists(path):
                        os.remove(path)
                except Exception:
                    pass
                save_database(self.db)
                self._refresh_images_list()
                self._refresh_list()
                self.thumb_label.config(image="", text="(preview)")

    def _create_new_rule(self):
        title = simpledialog.askstring(self._t("new_rule"), "Enter rule name:", parent=self.root)
        if not title:
            return
        rid = f"rule_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.db.setdefault("rules", {})[rid] = {
            "title": title, "version": "1.0", "status": self._t("draft"),
            "content": "", "images": [],
            "created": datetime.now().isoformat(), "updated": datetime.now().isoformat(),
        }
        save_database(self.db)
        self._refresh_list()
        self._select_by_title(title)
        messagebox.showinfo(self._t("app_title"), f'Rule "{title}" created!')

    def _select_by_title(self, title):
        query = self.search_var.get().lower()
        matched = [(rid, r) for rid, r in self.db.get("rules", {}).items() if isinstance(r, dict) and (not query or query in r.get("title", "").lower())]
        for i, (rid, r) in enumerate(matched):
            if r.get("title") == title:
                self.rule_list.selection_clear(0, tk.END)
                self.rule_list.selection_set(i)
                self.rule_list.see(i)
                self._on_select_rule(None)
                break

    def _save_current_rule(self):
        if not self.current_rule_id or self.current_rule_id not in self.db.get("rules", {}):
            messagebox.showwarning(self._t("app_title"), self._t("select_rule_warn"))
            return
        self.db["rules"][self.current_rule_id]["title"] = self.title_var.get()
        self.db["rules"][self.current_rule_id]["version"] = self.version_var.get()
        self.db["rules"][self.current_rule_id]["status"] = self.status_var.get()
        self.db["rules"][self.current_rule_id]["content"] = self.text_editor.get("1.0", tk.END).strip()
        self.db["rules"][self.current_rule_id]["updated"] = datetime.now().isoformat()
        save_database(self.db)
        self._refresh_list()
        self.status_bar.config(text=self._t("saved"))

    def _delete_current_rule(self):
        if not self.current_rule_id or self.current_rule_id not in self.db.get("rules", {}):
            messagebox.showwarning(self._t("app_title"), self._t("select_rule_warn"))
            return
        title = self.db["rules"][self.current_rule_id].get("title", "")
        if messagebox.askyesno("Confirm", f'Delete rule "{title}"?'):
            for img_path in self.db["rules"][self.current_rule_id].get("images", []):
                try:
                    if os.path.exists(img_path):
                        os.remove(img_path)
                except Exception:
                    pass
            del self.db["rules"][self.current_rule_id]
            save_database(self.db)
            self.current_rule_id = None
            self.title_var.set("")
            self.version_var.set("1.0")
            self.status_var.set(self._t("draft"))
            self.text_editor.delete("1.0", tk.END)
            self.images_listbox.delete(0, tk.END)
            self.thumb_label.config(image="", text="(preview)")
            self._refresh_list()
            self.status_bar.config(text=self._t("deleted"))

    def _insert_template(self, name):
        content = DEFAULT_TEMPLATES.get(name, "")
        self.text_editor.insert(tk.INSERT, f"\n\n{content}\n")

    def _show_preview(self):
        if not self.current_rule_id or self.current_rule_id not in self.db.get("rules", {}):
            messagebox.showwarning(self._t("app_title"), self._t("select_rule_warn"))
            return
        rule = self.db["rules"][self.current_rule_id]
        preview = Toplevel(self.root)
        preview.title(f"{self._t('preview')}: {rule.get('title', 'Untitled')}")
        preview.geometry("900x750")
        preview.configure(bg="#1e1e1e" if self.theme == "dark" else "#ffffff")
        header = ttk.Frame(preview, padding=15)
        header.pack(fill=X)
        ttk.Label(header, text=rule.get("title", ""), font=("Segoe UI", 16, "bold")).pack(anchor=W)
        ttk.Label(header, text=f"{self._t('version')}: {rule.get('version', '1.0')} | {self._t('status')}: {rule.get('status', self._t('draft'))}", font=("Segoe UI", 11)).pack(anchor=W, pady=5)
        ttk.Separator(preview, orient=HORIZONTAL).pack(fill=X, padx=15)
        content_frame = ttk.Frame(preview, padding=15)
        content_frame.pack(fill=BOTH, expand=True)
        bg = "#1e1e1e" if self.theme == "dark" else "#ffffff"
        fg = "#e0e0e0" if self.theme == "dark" else "#212529"
        text_widget = tk.Text(content_frame, wrap=tk.WORD, font=("Consolas", 12), bg=bg, fg=fg, borderwidth=0, highlightthickness=0, state=tk.DISABLED, padx=10, pady=10)
        text_widget.pack(fill=BOTH, expand=True)
        sb = ttk.Scrollbar(content_frame, command=text_widget.yview)
        text_widget.config(yscrollcommand=sb.set)
        text_widget.config(state=tk.NORMAL)
        text_widget.delete("1.0", tk.END)
        text_widget.insert(tk.END, rule.get("content", ""))
        text_widget.config(state=tk.DISABLED)
        if rule.get("images"):
            img_frame = ttk.Frame(preview, padding=15)
            img_frame.pack(fill=X)
            ttk.Label(img_frame, text=self._t("images"), font=("Segoe UI", 11, "bold")).pack(anchor=W)
            img_container = ttk.Frame(img_frame)
            img_container.pack(fill=X, pady=5)
            for img_path in rule["images"]:
                if os.path.exists(img_path):
                    try:
                        img = Image.open(img_path)
                        img.thumbnail((200, 200))
                        tk_img = ImageTk.PhotoImage(img)
                        lbl = ttk.Label(img_container, image=tk_img)
                        lbl.image = tk_img
                        lbl.pack(side=LEFT, padx=5)
                    except Exception:
                        ttk.Label(img_container, text=f"⚠️ {os.path.basename(img_path)}").pack(side=LEFT, padx=5)
        btn_frame = ttk.Frame(preview, padding=15)
        btn_frame.pack(fill=X)
        ttk.Button(btn_frame, text="📤 Export .txt", bootstyle=INFO, command=lambda: [preview.destroy(), self._export_txt()]).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="📤 Export .md", bootstyle=INFO, command=lambda: [preview.destroy(), self._export_md()]).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="📄 Export .pdf", bootstyle=PRIMARY, command=lambda: [preview.destroy(), self._export_pdf()]).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Close", bootstyle=SECONDARY, command=preview.destroy).pack(side=RIGHT, padx=5)

    def _add_download_record(self, filepath, fmt):
        if "downloads" not in self.db:
            self.db["downloads"] = []
        rule_title = ""
        if self.current_rule_id and self.current_rule_id in self.db.get("rules", {}) and isinstance(self.db["rules"][self.current_rule_id], dict):
            rule_title = self.db["rules"][self.current_rule_id].get("title", "")
        self.db["downloads"].insert(0, {"rule_name": rule_title, "format": fmt, "filepath": filepath, "filename": os.path.basename(filepath), "timestamp": datetime.now().isoformat()})
        save_database(self.db)

    def _open_exports_folder(self):
        ensure_dirs()
        os.startfile(EXPORTS_DIR)

    def _open_file_folder(self, filepath):
        if os.path.exists(filepath):
            os.startfile(os.path.dirname(filepath))
        else:
            messagebox.showwarning("File not found", "File has been moved or deleted.")

    def _show_downloads(self):
        win = Toplevel(self.root)
        win.title(self._t("downloads"))
        win.geometry("900x550")
        ttk.Label(win, text=self._t("downloads"), font=("Segoe UI", 14, "bold")).pack(anchor=W, padx=15, pady=10)
        tv_frame = ttk.Frame(win, padding=10)
        tv_frame.pack(fill=BOTH, expand=True)
        cols = ("rule_name", "format", "filename", "timestamp")
        tree = ttk.Treeview(tv_frame, columns=cols, show="headings", bootstyle="dark")
        tree.heading("rule_name", text="Rule")
        tree.heading("format", text="Fmt")
        tree.heading("filename", text="File")
        tree.heading("timestamp", text="Date")
        tree.column("rule_name", width=250)
        tree.column("format", width=80, anchor="center")
        tree.column("filename", width=250)
        tree.column("timestamp", width=200)
        vsb = ttk.Scrollbar(tv_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side=LEFT, fill=BOTH, expand=True)
        vsb.pack(side=RIGHT, fill=Y)
        for item in self.db.get("downloads", []):
            tree.insert("", tk.END, values=(item.get("rule_name", ""), item.get("format", "").upper(), item.get("filename", ""), item.get("timestamp", "")[:19].replace("T", " ")), tags=(item.get("filepath", ""),))
        def on_double_click(event):
            sel = tree.selection()
            if sel:
                self._open_file_folder(tree.item(sel[0], "tags")[0])
        tree.bind("<Double-1>", on_double_click)
        btn_frame = ttk.Frame(win, padding=10)
        btn_frame.pack(fill=X)
        ttk.Button(btn_frame, text="📂 Open file folder", bootstyle=PRIMARY, command=lambda: on_double_click(None)).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ Clear history", bootstyle=DANGER, command=lambda: [self.db.update({"downloads": []}), save_database(self.db), win.destroy(), self._show_downloads()]).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Close", bootstyle=SECONDARY, command=win.destroy).pack(side=RIGHT, padx=5)

    def _do_publish(self):
        if not self.current_rule_id or self.current_rule_id not in self.db.get("rules", {}):
            messagebox.showwarning(self._t("app_title"), self._t("select_rule_warn"))
            return
        user = self.db.get("_current_user")
        if not user:
            messagebox.showwarning(self._t("app_title"), self._t("login_required_publish"))
            return
        if self._is_banned(user):
            messagebox.showwarning(self._t("app_title"), self._t("banned_message"))
            return
        if not messagebox.askyesno(self._t("publish"), self._t("confirm_publish")):
            return
        # Ask target feed (only admin can choose community; regular users default to authors)
        is_admin = user.lower() == "testers@example.ru"
        target = "authors"
        if is_admin:
            win_ask = Toplevel(self.root)
            win_ask.title(self._t("publish"))
            win_ask.geometry("350x150")
            win_ask.transient(self.root)
            ttk.Label(win_ask, text=self._t("publish_to"), font=("Segoe UI", 11)).pack(pady=10)
            target_var = tk.StringVar(value="community")
            ttk.Combobox(win_ask, values=[self._t("publish_community"), self._t("publish_authors")], textvariable=target_var, state="readonly", width=20).pack(pady=5)
            def confirm_target():
                nonlocal target
                val = target_var.get()
                target = "authors" if self._t("publish_authors") in val else "community"
                win_ask.destroy()
            ttk.Button(win_ask, text="OK", command=confirm_target).pack(pady=10)
            self.root.wait_window(win_ask)
        if not is_admin and target == "community":
            messagebox.showwarning(self._t("app_title"), self._t("only_admin_community"))
            return
        rule = self.db["rules"][self.current_rule_id]
        import random
        pub_id = f"pub_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000,9999)}"
        share_obj = {"pub_id": pub_id, "id": self.current_rule_id, "title": rule.get("title", ""), "version": rule.get("version", "1.0"), "status": rule.get("status", self._t("draft")), "content": rule.get("content", ""), "lang": self.lang, "author": user or "Guest", "date": datetime.now().isoformat()[:10], "feed": target}
        json_str = json.dumps(share_obj, ensure_ascii=False)
        b64 = base64.b64encode(json_str.encode('utf-8')).decode('ascii')
        # Save to appropriate public list
        key = "_public_authors" if target == "authors" else "_public_community"
        pub_list = self.db.setdefault(key, [])
        # Always insert as new so old versions stay intact
        pub_list.insert(0, share_obj)
        save_database(self.db)
        self.root.clipboard_clear()
        self.root.clipboard_append(b64)
        win = Toplevel(self.root)
        win.title(self._t("published"))
        win.geometry("700x200")
        ttk.Label(win, text=self._t("share_msg"), font=("Segoe UI", 11)).pack(pady=10)
        entry = ttk.Entry(win, font=("Consolas", 10))
        entry.insert(0, b64)
        entry.pack(fill=X, padx=20, pady=5)
        entry.select_range(0, tk.END)
        entry.focus()
        ttk.Button(win, text=self._t("copy_link"), command=lambda: [self.root.clipboard_clear(), self.root.clipboard_append(b64)]).pack(pady=10)

    def _show_public_browser(self, feed):
        title_key = "community_rules_title" if feed == "community" else "authors_rules_title"
        win = Toplevel(self.root)
        win.title(self._t(title_key))
        win.geometry("900x600")
        ttk.Label(win, text=self._t(title_key), font=("Segoe UI", 14, "bold")).pack(anchor=W, padx=15, pady=10)
        tv_frame = ttk.Frame(win, padding=10)
        tv_frame.pack(fill=BOTH, expand=True)
        cols = ("title", "lang", "author", "date")
        tree = ttk.Treeview(tv_frame, columns=cols, show="headings", bootstyle="dark")
        tree.heading("title", text="Title")
        tree.heading("lang", text="Lang")
        tree.heading("author", text="Author")
        tree.heading("date", text="Date")
        tree.column("title", width=400)
        tree.column("lang", width=60, anchor="center")
        tree.column("author", width=120)
        tree.column("date", width=100)
        vsb = ttk.Scrollbar(tv_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side=LEFT, fill=BOTH, expand=True)
        vsb.pack(side=RIGHT, fill=Y)
        items = []
        if feed == "community":
            items = PUBLIC_RULES + self.db.get("_public_community", [])
        else:
            items = self.db.get("_public_authors", [])
        for pr in items:
            tree.insert("", tk.END, values=(pr.get("title", ""), pr.get("lang", ""), pr.get("author", ""), pr.get("date", "")), tags=(json.dumps(pr),))
        def get_selected_pr():
            sel = tree.selection()
            if not sel:
                return None
            raw = tree.item(sel[0], "tags")[0]
            try:
                return json.loads(raw)
            except Exception:
                return None

        def on_double_click(event):
            pr = get_selected_pr()
            if pr:
                self._show_public_detail(win, pr)
        tree.bind("<Double-1>", on_double_click)
        btn_frame = ttk.Frame(win, padding=10)
        btn_frame.pack(fill=X)
        ttk.Button(btn_frame, text=self._t("save_to_my"), bootstyle=PRIMARY, command=lambda: on_double_click(None)).pack(side=LEFT, padx=5)

        user = self.db.get("_current_user")
        if user and user.lower() == "testers@example.ru":
            def do_delete_public():
                pr = get_selected_pr()
                if not pr:
                    messagebox.showwarning(self._t("app_title"), self._t("select_rule_warn"))
                    return
                if any(pr.get("id") == p.get("id") for p in PUBLIC_RULES):
                    messagebox.showwarning(self._t("app_title"), self._t("cannot_delete_builtin"))
                    return
                if not messagebox.askyesno(self._t("app_title"), self._t("delete_from_public_confirm")):
                    return
                pid = pr.get("pub_id", pr.get("id"))
                key = "_public_community" if feed == "community" else "_public_authors"
                pub_list = self.db.get(key, [])
                new_list = [r for r in pub_list if r.get("pub_id", r.get("id")) != pid]
                if len(new_list) == len(pub_list):
                    messagebox.showwarning(self._t("app_title"), self._t("select_rule_warn"))
                    return
                self.db[key] = new_list
                save_database(self.db)
                for item in tree.get_children():
                    tree.delete(item)
                items = PUBLIC_RULES + self.db.get("_public_community", []) if feed == "community" else self.db.get("_public_authors", [])
                for p in items:
                    tree.insert("", tk.END, values=(p.get("title", ""), p.get("lang", ""), p.get("author", ""), p.get("date", "")), tags=(json.dumps(p),))
            ttk.Button(btn_frame, text=self._t("delete_public"), bootstyle=DANGER, command=do_delete_public).pack(side=LEFT, padx=5)

        ttk.Button(btn_frame, text="❌ Close", bootstyle=SECONDARY, command=win.destroy).pack(side=RIGHT, padx=5)

    def _show_community_rules(self):
        self._show_public_browser("community")

    def _show_authors_rules(self):
        self._show_public_browser("authors")

    def _show_public_detail(self, parent_win, pr):
        if not pr or not isinstance(pr, dict):
            return
        detail = Toplevel(parent_win)
        detail.title(pr.get("title", "Public Rule"))
        detail.geometry("800x600")
        ttk.Label(detail, text=pr.get("title", ""), font=("Segoe UI", 16, "bold")).pack(anchor=W, padx=15, pady=10)
        ttk.Label(detail, text=f"Version: {pr.get('version', '1.0')} | Status: {pr.get('status', 'Draft')} | Lang: {pr.get('lang', 'en')}", font=("Segoe UI", 11)).pack(anchor=W, padx=15)
        ttk.Label(detail, text=f"Author: {pr.get('author', '')} | Date: {pr.get('date', '')}", font=("Segoe UI", 10)).pack(anchor=W, padx=15, pady=5)
        ttk.Separator(detail, orient=HORIZONTAL).pack(fill=X, padx=15, pady=5)
        bg = "#1e1e1e" if self.theme == "dark" else "#ffffff"
        fg = "#e0e0e0" if self.theme == "dark" else "#212529"
        text_widget = tk.Text(detail, wrap=tk.WORD, font=("Consolas", 12), bg=bg, fg=fg, padx=10, pady=10)
        text_widget.pack(fill=BOTH, expand=True, padx=15, pady=5)
        text_widget.insert(tk.END, pr.get("content", ""))
        text_widget.config(state=tk.DISABLED)
        def save_public():
            rid = f"rule_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.db.setdefault("rules", {})[rid] = {"title": pr.get("title", "Imported Rule"), "version": pr.get("version", "1.0"), "status": pr.get("status", "Draft"), "content": pr.get("content", ""), "images": [], "created": datetime.now().isoformat(), "updated": datetime.now().isoformat()}
            save_database(self.db)
            self._refresh_list()
            messagebox.showinfo(self._t("app_title"), "Saved to My Rules!")
            detail.destroy()
        btn_frame = ttk.Frame(detail, padding=10)
        btn_frame.pack(fill=X)
        ttk.Button(btn_frame, text=self._t("save_to_my"), bootstyle=PRIMARY, command=save_public).pack(side=LEFT, padx=5)
        user = self.db.get("_current_user")
        if user and user.lower() == "testers@example.ru":
            def delete_this_public():
                if any(pr.get("id") == p.get("id") for p in PUBLIC_RULES):
                    messagebox.showwarning(self._t("app_title"), self._t("cannot_delete_builtin"))
                    return
                if not messagebox.askyesno(self._t("app_title"), self._t("delete_from_public_confirm")):
                    return
                pid = pr.get("pub_id", pr.get("id"))
                feed = pr.get("feed", "community")
                key = "_public_community" if feed == "community" else "_public_authors"
                pub_list = self.db.get(key, [])
                new_list = [r for r in pub_list if r.get("pub_id", r.get("id")) != pid]
                if len(new_list) == len(pub_list):
                    messagebox.showwarning(self._t("app_title"), self._t("select_rule_warn"))
                    return
                self.db[key] = new_list
                save_database(self.db)
                messagebox.showinfo(self._t("app_title"), "Deleted from public.")
                detail.destroy()
            ttk.Button(btn_frame, text=self._t("delete_public"), bootstyle=DANGER, command=delete_this_public).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Close", bootstyle=SECONDARY, command=detail.destroy).pack(side=RIGHT, padx=5)

    def _show_settings(self):
        win = Toplevel(self.root)
        win.title(self._t("settings"))
        win.geometry("400x280")
        ttk.Label(win, text=self._t("settings"), font=("Segoe UI", 14, "bold")).pack(anchor=W, padx=15, pady=15)
        frame = ttk.Frame(win, padding=10)
        frame.pack(fill=X, padx=15)
        ttk.Label(frame, text=self._t("choose_theme")).grid(row=0, column=0, sticky=W, pady=5)
        theme_var = tk.StringVar(value=self.theme)
        ttk.Combobox(frame, values=["dark", "light"], textvariable=theme_var, width=15, state="readonly").grid(row=0, column=1, sticky=W, padx=10)
        ttk.Label(frame, text=self._t("choose_lang")).grid(row=1, column=0, sticky=W, pady=5)
        lang_var = tk.StringVar(value=self.lang)
        ttk.Combobox(frame, values=list(LANGS.keys()), textvariable=lang_var, width=15, state="readonly").grid(row=1, column=1, sticky=W, padx=10)
        def apply_settings():
            new_theme = theme_var.get()
            new_lang = lang_var.get()
            old_lang = self.lang
            old_theme = self.theme
            changed = (new_theme != old_theme) or (new_lang != old_lang)
            self.theme = new_theme
            self.lang = new_lang
            self.settings["theme"] = new_theme
            self.settings["lang"] = new_lang
            save_database(self.db)
            win.destroy()
            if changed:
                if new_lang != old_lang and self.current_rule_id and self.current_rule_id in self.db.get("rules", {}) and isinstance(self.db["rules"][self.current_rule_id], dict):
                    self._translate_rule_async(old_lang, new_lang)
                if new_theme != old_theme:
                    self._apply_theme_on_the_fly()
                messagebox.showinfo(self._t("app_title"), self._t("restart_needed"))
        ttk.Button(win, text=self._t("apply"), command=apply_settings).pack(pady=15)

    def _show_comments(self):
        if not self.current_rule_id or self.current_rule_id not in self.db.get("rules", {}):
            messagebox.showwarning(self._t("app_title"), self._t("select_rule_warn"))
            return
        win = Toplevel(self.root)
        win.title(self._t("comments_title"))
        win.geometry("700x500")
        ttk.Label(win, text=self._t("comments_title"), font=("Segoe UI", 14, "bold")).pack(anchor=W, padx=15, pady=10)
        tv_frame = ttk.Frame(win, padding=10)
        tv_frame.pack(fill=BOTH, expand=True)
        cols = ("author", "text", "date")
        tree = ttk.Treeview(tv_frame, columns=cols, show="headings", bootstyle="dark")
        tree.heading("author", text=self._t("comment_author"))
        tree.heading("text", text=self._t("comment_text"))
        tree.heading("date", text=self._t("comment_date"))
        tree.column("author", width=150)
        tree.column("text", width=400)
        tree.column("date", width=120)
        vsb = ttk.Scrollbar(tv_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side=LEFT, fill=BOTH, expand=True)
        vsb.pack(side=RIGHT, fill=Y)
        rule = self.db["rules"][self.current_rule_id]
        comments = rule.get("comments", [])
        if not comments:
            tree.insert("", tk.END, values=("", self._t("no_comments"), ""))
        else:
            for c in comments:
                tree.insert("", tk.END, values=(c.get("author", ""), c.get("text", ""), c.get("date", "")[:19].replace("T", " ")))
        input_frame = ttk.Frame(win, padding=10)
        input_frame.pack(fill=X)
        ttk.Label(input_frame, text=self._t("comment_placeholder")).pack(anchor=W)
        comment_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=comment_var).pack(fill=X, pady=5)
        def add_comment():
            text = comment_var.get().strip()
            if not text:
                return
            user = self.db.get("_current_user") or "Guest"
            rule.setdefault("comments", []).append({"author": user, "text": text, "date": datetime.now().isoformat()})
            save_database(self.db)
            comment_var.set("")
            for item in tree.get_children():
                tree.delete(item)
            comments = rule.get("comments", [])
            if not comments:
                tree.insert("", tk.END, values=("", self._t("no_comments"), ""))
            else:
                for c in comments:
                    tree.insert("", tk.END, values=(c.get("author", ""), c.get("text", ""), c.get("date", "")[:19].replace("T", " ")))
            self.status_bar.config(text=self._t("comment_added"))
        ttk.Button(input_frame, text=self._t("add_comment"), bootstyle=PRIMARY, command=add_comment).pack(side=LEFT, padx=5)
        ttk.Button(input_frame, text="❌ Close", bootstyle=SECONDARY, command=win.destroy).pack(side=RIGHT, padx=5)

    def _show_admin_panel(self):
        win = Toplevel(self.root)
        win.title(self._t("admin_title"))
        win.geometry("700x500")
        ttk.Label(win, text=self._t("admin_title"), font=("Segoe UI", 14, "bold")).pack(anchor=W, padx=15, pady=10)
        ttk.Label(win, text=self._t("admin_users"), font=("Segoe UI", 11)).pack(anchor=W, padx=15, pady=5)
        tv_frame = ttk.Frame(win, padding=10)
        tv_frame.pack(fill=BOTH, expand=True)
        cols = ("email", "name", "status")
        tree = ttk.Treeview(tv_frame, columns=cols, show="headings", bootstyle="dark")
        tree.heading("email", text="Email")
        tree.heading("name", text="Name")
        tree.heading("status", text="Status")
        tree.column("email", width=300)
        tree.column("name", width=150)
        tree.column("status", width=100, anchor="center")
        vsb = ttk.Scrollbar(tv_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side=LEFT, fill=BOTH, expand=True)
        vsb.pack(side=RIGHT, fill=Y)
        def refresh_users():
            for item in tree.get_children():
                tree.delete(item)
            for u in self.db.get("_users", []):
                banned = u.get("banned", False)
                status = self._t("user_banned") if banned else self._t("user_active")
                tree.insert("", tk.END, values=(u.get("email", ""), u.get("name", ""), status), tags=(u.get("email", ""),))
        refresh_users()
        def on_double_click(event):
            sel = tree.selection()
            if not sel:
                return
            email = tree.item(sel[0], "tags")[0]
            users = self.db.get("_users", [])
            for u in users:
                if u.get("email") == email:
                    u["banned"] = not u.get("banned", False)
                    break
            save_database(self.db)
            refresh_users()
        tree.bind("<Double-1>", on_double_click)
        btn_frame = ttk.Frame(win, padding=10)
        btn_frame.pack(fill=X)
        ttk.Label(btn_frame, text="Double-click a user to toggle ban/unban.", font=("Segoe UI", 9), foreground="#888").pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Close", bootstyle=SECONDARY, command=win.destroy).pack(side=RIGHT, padx=5)

    def _apply_theme_on_the_fly(self):
        ttk_theme = THEMES.get(self.theme, "darkly")
        self.style.theme_use(ttk_theme)
        self._apply_widget_colors()
        self.root.update()

    def _translate_rule_async(self, from_lang, to_lang):
        if not self.current_rule_id or self.current_rule_id not in self.db.get("rules", {}):
            return
        self.status_bar.config(text=self._t("translate_wait"))
        def task():
            rule = self.db["rules"][self.current_rule_id]
            new_title = self._translate_text(rule.get("title", ""), from_lang, to_lang)
            new_content = self._translate_text(rule.get("content", ""), from_lang, to_lang)
            self.root.after(0, lambda: self._apply_translation(new_title, new_content))
        threading.Thread(target=task, daemon=True).start()

    def _translate_text(self, text, from_lang, to_lang):
        if from_lang == to_lang or not text:
            return text
        try:
            chunks = text.split("\n\n")
            translated = []
            for chunk in chunks:
                if not chunk.strip():
                    translated.append(chunk)
                    continue
                if len(chunk) > 450:
                    subchunks = chunk.split("\n")
                    sub_trans = []
                    for sc in subchunks:
                        if not sc.strip():
                            sub_trans.append(sc)
                            continue
                        url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(sc)}&langpair={from_lang}|{to_lang}"
                        with urllib.request.urlopen(url, timeout=15) as resp:
                            data = json.loads(resp.read().decode('utf-8'))
                            sub_trans.append(data['responseData']['translatedText'] if data.get('responseData') and data['responseData'].get('translatedText') else sc)
                    translated.append("\n".join(sub_trans))
                else:
                    url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(chunk)}&langpair={from_lang}|{to_lang}"
                    with urllib.request.urlopen(url, timeout=15) as resp:
                        data = json.loads(resp.read().decode('utf-8'))
                        translated.append(data['responseData']['translatedText'] if data.get('responseData') and data['responseData'].get('translatedText') else chunk)
            return "\n\n".join(translated)
        except Exception:
            pass
        return text

    def _apply_translation(self, new_title, new_content):
        if self.current_rule_id and self.current_rule_id in self.db.get("rules", {}) and isinstance(self.db["rules"][self.current_rule_id], dict):
            self.db["rules"][self.current_rule_id]["title"] = new_title
            self.db["rules"][self.current_rule_id]["content"] = new_content
            self.db["rules"][self.current_rule_id]["updated"] = datetime.now().isoformat()
            self.title_var.set(new_title)
            self.text_editor.delete("1.0", tk.END)
            self.text_editor.insert(tk.END, new_content)
            save_database(self.db)
            self._refresh_list()
            self.status_bar.config(text=self._t("translate_done"))

    def _export_txt(self):
        if not self.current_rule_id or self.current_rule_id not in self.db.get("rules", {}):
            messagebox.showwarning(self._t("app_title"), self._t("select_rule_warn"))
            return
        rule = self.db["rules"][self.current_rule_id]
        filepath = filedialog.asksaveasfilename(initialdir=EXPORTS_DIR, initialfilename=f"{rule['title']}.txt", defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"{'='*60}\n")
                f.write(f"  {self._t('app_title').upper()}\n")
                f.write(f"{'='*60}\n\n")
                f.write(f"{self._t('rule_name')} {rule['title']}\n")
                f.write(f"{self._t('version')} {rule['version']}\n")
                f.write(f"{self._t('status')} {rule['status']}\n")
                f.write(f"Created: {rule['created']}\n")
                f.write(f"Updated: {rule['updated']}\n")
                f.write(f"\n{'-'*60}\n\n")
                f.write(rule['content'])
                if rule.get("images"):
                    f.write(f"\n\n{'-'*60}\n")
                    f.write("Images:\n")
                    for p in rule["images"]:
                        f.write(f" - {os.path.basename(p)}\n")
            self._add_download_record(filepath, "txt")
            messagebox.showinfo("Export", f"Exported to:\n{filepath}")

    def _export_md(self):
        if not self.current_rule_id or self.current_rule_id not in self.db.get("rules", {}):
            messagebox.showwarning(self._t("app_title"), self._t("select_rule_warn"))
            return
        rule = self.db["rules"][self.current_rule_id]
        filepath = filedialog.asksaveasfilename(initialdir=EXPORTS_DIR, initialfilename=f"{rule['title']}.md", defaultextension=".md", filetypes=[("Markdown files", "*.md"), ("All files", "*.*")])
        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# {rule['title']}\n\n")
                f.write(f"> **{self._t('version')}** {rule['version']}  \n")
                f.write(f"> **{self._t('status')}** {rule['status']}  \n")
                f.write(f"> **Created:** {rule['created']}  \n")
                f.write(f"> **Updated:** {rule['updated']}  \n\n")
                f.write(f"---\n\n")
                f.write(rule['content'])
                if rule.get("images"):
                    f.write(f"\n\n---\n\n")
                    f.write("## Images\n\n")
                    for p in rule["images"]:
                        f.write(f"- `{os.path.basename(p)}`\n")
            self._add_download_record(filepath, "md")
            messagebox.showinfo("Export", f"Exported to:\n{filepath}")

    def _export_pdf(self):
        if not self.current_rule_id or self.current_rule_id not in self.db.get("rules", {}):
            messagebox.showwarning(self._t("app_title"), self._t("select_rule_warn"))
            return
        rule = self.db["rules"][self.current_rule_id]
        filepath = filedialog.asksaveasfilename(initialdir=EXPORTS_DIR, initialfilename=f"{rule['title']}.pdf", defaultextension=".pdf", filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
        if not filepath:
            return
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            font_regular = r"C:\Windows\Fonts\arial.ttf"
            font_bold = r"C:\Windows\Fonts\arialbd.ttf"
            if not os.path.exists(font_bold):
                font_bold = font_regular
            pdf.add_font("ArialCustom", "", font_regular)
            pdf.add_font("ArialCustom", "B", font_bold)
            pdf.set_font("ArialCustom", "B", 16)
            pdf.cell(0, 10, rule.get("title", "Untitled"), ln=True, align="C")
            pdf.ln(5)
            pdf.set_font("ArialCustom", "", 11)
            pdf.cell(0, 8, f"{self._t('version')} {rule.get('version', '1.0')}", ln=True)
            pdf.cell(0, 8, f"{self._t('status')} {rule.get('status', self._t('draft'))}", ln=True)
            pdf.cell(0, 8, f"Created: {rule.get('created', '')}", ln=True)
            pdf.cell(0, 8, f"Updated: {rule.get('updated', '')}", ln=True)
            pdf.ln(5)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(5)
            pdf.set_font("ArialCustom", "", 12)
            for line in rule.get("content", "").split("\n"):
                pdf.multi_cell(0, 8, line)
            if rule.get("images"):
                pdf.add_page()
                pdf.set_font("ArialCustom", "B", 14)
                pdf.cell(0, 10, "Images", ln=True, align="C")
                pdf.ln(5)
                for img_path in rule["images"]:
                    if os.path.exists(img_path):
                        try:
                            ext = os.path.splitext(img_path)[1].lower()
                            if ext in (".png", ".jpg", ".jpeg", ".gif", ".bmp"):
                                with Image.open(img_path) as im:
                                    w, h = im.size
                                    max_w = 180
                                    ratio = min(max_w / w, 200 / h)
                                    new_w = w * ratio
                                pdf.image(img_path, x=15, w=new_w)
                                pdf.ln(5)
                        except Exception:
                            pdf.set_font("ArialCustom", "", 10)
                            pdf.cell(0, 6, f"Image error: {os.path.basename(img_path)}", ln=True)
            pdf.output(filepath)
            self._add_download_record(filepath, "pdf")
            messagebox.showinfo("Export", f"PDF created:\n{filepath}")
        except Exception as e:
            messagebox.showerror("PDF Error", f"Failed to create PDF:\n{e}")


def main():
    ensure_dirs()
    db = load_database()
    migrate_db(db)
    save_database(db)
    settings = db.get("_settings", {"theme": "dark", "lang": "en"})
    theme_name = THEMES.get(settings.get("theme", "dark"), "darkly")
    root = ttk.Window(themename=theme_name)
    app = PrivacyHubApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
