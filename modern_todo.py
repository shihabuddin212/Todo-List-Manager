#!/usr/bin/env python3

import sys
import os
from datetime import datetime, date
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QListWidget, QPushButton, QLabel, 
                            QLineEdit, QTextEdit, QDialog, QMessageBox,
                            QListWidgetItem, QFrame, QSplitter, QStackedWidget,
                            QComboBox, QScrollArea, QToolButton, QMenu, QAction,
                            QButtonGroup, QRadioButton, QCalendarWidget, QDateEdit)
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, pyqtSignal, QDate
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette, QPainter, QPen

from core.todo_manager import TodoManager
from core.settings import Settings

# Constants
ICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "todo_icon.ico")

# Color schemes
LIGHT_THEME = {
    'bg_primary': '#ffffff',
    'bg_secondary': '#f8f9fa',
    'text_primary': '#212529',
    'text_secondary': '#6c757d',
    'accent': '#0d6efd',
    'success': '#198754',
    'warning': '#ffc107',
    'error': '#dc3545',
    'border': '#dee2e6',
    'hover': '#e9ecef'
}

DARK_THEME = {
    'bg_primary': '#212529',
    'bg_secondary': '#343a40',
    'text_primary': '#f8f9fa',
    'text_secondary': '#adb5bd',
    'accent': '#0d6efd',
    'success': '#198754',
    'warning': '#ffc107',
    'error': '#dc3545',
    'border': '#495057',
    'hover': '#1a1d20'
}

PRIORITY_COLORS = {
    'High': '#dc3545',
    'Medium': '#ffc107',
    'Low': '#198754'
}

class SearchBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setContentsMargins(16, 8, 16, 8)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search tasks...")
        self.search_input.setMinimumWidth(300)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 16px;
                border-radius: 20px;
                border: 1px solid #dee2e6;
                background: #f8f9fa;
                font-size: 14px;
            }
        """)
        
        # User profile button
        self.profile_btn = QToolButton()
        self.profile_btn.setIcon(QIcon.fromTheme("user"))
        self.profile_btn.setIconSize(QSize(24, 24))
        self.profile_btn.setStyleSheet("""
            QToolButton {
                border: none;
                padding: 8px;
            }
            QToolButton:hover {
                background: #e9ecef;
                border-radius: 4px;
            }
        """)
        
        layout.addWidget(self.search_input)
        layout.addStretch()
        layout.addWidget(self.profile_btn)
        
        self.setLayout(layout)
        self.setFixedHeight(60)

class SidebarButton(QPushButton):
    def __init__(self, text, icon_name=None, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setFixedHeight(40)
        if icon_name:
            self.setIcon(QIcon.fromTheme(icon_name))
        self.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                margin: 2px 8px;
                font-size: 14px;
            }
            QPushButton:checked {
                background-color: #0d6efd;
                color: white;
            }
            QPushButton:hover:!checked {
                background-color: #e9ecef;
            }
        """)

class Sidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(240)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # App title
        title = QLabel("Todo List")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            padding: 16px;
            color: #0d6efd;
        """)
        layout.addWidget(title)
        
        # Navigation buttons
        self.nav_buttons = {
            'all': SidebarButton("All Tasks", "view-list"),
            'today': SidebarButton("Today", "calendar-today"),
            'upcoming': SidebarButton("Upcoming", "calendar"),
            'completed': SidebarButton("Completed", "checkbox"),
            'categories': SidebarButton("Categories", "folder"),
            'settings': SidebarButton("Settings", "configure")
        }
        
        # Button group for navigation
        self.nav_group = QButtonGroup(self)
        for btn in self.nav_buttons.values():
            layout.addWidget(btn)
            self.nav_group.addButton(btn)
        
        layout.addStretch()
        
        # Theme toggle
        self.theme_toggle = QPushButton("Toggle Theme")
        self.theme_toggle.setIcon(QIcon.fromTheme("weather-clear-night"))
        self.theme_toggle.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                margin: 8px;
                border-radius: 4px;
                background: #f8f9fa;
                border: 1px solid #dee2e6;
            }
            QPushButton:hover {
                background: #e9ecef;
            }
        """)
        layout.addWidget(self.theme_toggle)
        
        self.setLayout(layout)

class TaskCard(QFrame):
    taskChanged = pyqtSignal(int)  # Signal to emit when task is modified
    
    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.task = task
        self.setFrameStyle(QFrame.StyledPanel)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Header with checkbox and title
        header = QHBoxLayout()
        
        # Checkbox
        self.checkbox = QToolButton()
        self.checkbox.setCheckable(True)
        self.checkbox.setChecked(self.task.get("completed", False))
        self.checkbox.clicked.connect(self.toggle_completed)
        self.checkbox.setStyleSheet("""
            QToolButton {
                border: 2px solid #dee2e6;
                border-radius: 12px;
                padding: 4px;
                background: white;
            }
            QToolButton:checked {
                background: #198754;
                border-color: #198754;
            }
        """)
        
        # Title
        title = QLabel(self.task["title"])
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        
        header.addWidget(self.checkbox)
        header.addWidget(title)
        header.addStretch()
        
        # Priority tag
        priority = self.task.get("priority", "Medium")
        priority_label = QLabel(priority)
        priority_label.setStyleSheet(f"""
            background: {PRIORITY_COLORS[priority]};
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
        """)
        header.addWidget(priority_label)
        
        # Edit and delete buttons
        edit_btn = QToolButton()
        edit_btn.setIcon(QIcon.fromTheme("document-edit"))
        edit_btn.clicked.connect(self.edit_task)
        delete_btn = QToolButton()
        delete_btn.setIcon(QIcon.fromTheme("edit-delete"))
        delete_btn.clicked.connect(self.delete_task)
        
        for btn in [edit_btn, delete_btn]:
            btn.setStyleSheet("""
                QToolButton {
                    border: none;
                    padding: 4px;
                }
                QToolButton:hover {
                    background: #e9ecef;
                    border-radius: 4px;
                }
            """)
            header.addWidget(btn)
        
        layout.addLayout(header)
        
        # Description
        if self.task.get("description"):
            desc = QLabel(self.task["description"])
            desc.setWordWrap(True)
            desc.setStyleSheet("color: #6c757d; margin-top: 8px;")
            layout.addWidget(desc)
        
        # Footer with due date and category
        footer = QHBoxLayout()
        
        if self.task.get("due_date"):
            due_label = QLabel(f"Due: {self.task['due_date']}")
            due_label.setStyleSheet("color: #6c757d; font-size: 12px;")
            footer.addWidget(due_label)
        
        if self.task.get("category"):
            category_label = QLabel(self.task["category"])
            category_label.setStyleSheet("""
                background: #e9ecef;
                color: #212529;
                padding: 2px 6px;
                border-radius: 3px;
                font-size: 12px;
            """)
            footer.addWidget(category_label)
        
        footer.addStretch()
        layout.addLayout(footer)
        
        self.setLayout(layout)
    
    def toggle_completed(self):
        self.task["completed"] = self.checkbox.isChecked()
        self.task["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if self.task["completed"] else None
        self.taskChanged.emit(self.task["id"])
    
    def edit_task(self):
        dialog = TaskEditDialog(self, self.task)
        if dialog.exec_():
            self.task.update(dialog.get_task_data())
            self.taskChanged.emit(self.task["id"])
    
    def delete_task(self):
        reply = QMessageBox.question(
            self, "Delete Task",
            f"Are you sure you want to delete '{self.task['title']}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.taskChanged.emit(self.task["id"])

class TaskEditDialog(QDialog):
    def __init__(self, parent=None, task=None):
        super().__init__(parent)
        self.task = task
        self.setWindowTitle("Add Task" if not task else "Edit Task")
        self.setMinimumWidth(500)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(16)
        
        # Title
        title_label = QLabel("Title:")
        self.title_input = QLineEdit()
        if self.task:
            self.title_input.setText(self.task["title"])
        
        # Description
        desc_label = QLabel("Description:")
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(100)
        if self.task:
            self.desc_input.setText(self.task.get("description", ""))
        
        # Due Date
        due_label = QLabel("Due Date:")
        self.due_input = QDateEdit()
        self.due_input.setCalendarPopup(True)
        if self.task and self.task.get("due_date"):
            self.due_input.setDate(QDate.fromString(self.task["due_date"], "yyyy-MM-dd"))
        else:
            self.due_input.setDate(QDate.currentDate())
        
        # Priority
        priority_label = QLabel("Priority:")
        self.priority_input = QComboBox()
        self.priority_input.addItems(["Low", "Medium", "High"])
        if self.task:
            self.priority_input.setCurrentText(self.task.get("priority", "Medium"))
        
        # Category
        category_label = QLabel("Category:")
        self.category_input = QComboBox()
        self.category_input.setEditable(True)
        self.category_input.addItems(["Personal", "Work", "Shopping", "Health"])
        if self.task:
            self.category_input.setCurrentText(self.task.get("category", ""))
        
        # Add all widgets
        for label, widget in [
            (title_label, self.title_input),
            (desc_label, self.desc_input),
            (due_label, self.due_input),
            (priority_label, self.priority_input),
            (category_label, self.category_input)
        ]:
            layout.addWidget(label)
            layout.addWidget(widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.cancel_btn = QPushButton("Cancel")
        self.save_btn = QPushButton("Save")
        self.save_btn.setDefault(True)
        
        for btn, primary in [(self.cancel_btn, False), (self.save_btn, True)]:
            btn.setStyleSheet(f"""
                QPushButton {{
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-size: 14px;
                    background: {('#0d6efd' if primary else '#f8f9fa')};
                    color: {('white' if primary else '#212529')};
                    border: {('none' if primary else '1px solid #dee2e6')};
                }}
                QPushButton:hover {{
                    background: {('#0b5ed7' if primary else '#e9ecef')};
                }}
            """)
        
        self.cancel_btn.clicked.connect(self.reject)
        self.save_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def get_task_data(self):
        return {
            "title": self.title_input.text(),
            "description": self.desc_input.toPlainText(),
            "due_date": self.due_input.date().toString("yyyy-MM-dd"),
            "priority": self.priority_input.currentText(),
            "category": self.category_input.currentText()
        }

def get_icon(name):
    """Helper function to get icons with fallback to system theme"""
    icon_path = os.path.join("icons", f"{name}.png")
    if os.path.exists(icon_path):
        return QIcon(icon_path)
    return QIcon.fromTheme(name, QIcon.fromTheme("application-x-executable"))

class ModernTodoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.todo_list = TodoManager()
        self.settings = Settings()
        self.current_theme = self.settings.get_theme()
        self.current_view = self.settings.get_view()
        self.current_filter = "all"
        self.init_ui()
        self.load_tasks()
        
    def init_ui(self):
        self.setWindowTitle("Todo List Manager")
        self.setMinimumSize(1200, 800)
        
        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))
        
        # Main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout()
        main_widget.setLayout(layout)
        
        # Sidebar
        self.sidebar = Sidebar()
        self.sidebar.theme_toggle.clicked.connect(self.toggle_theme)
        self.sidebar.nav_group.buttonClicked.connect(self.handle_navigation)
        layout.addWidget(self.sidebar)
        
        # Main content area
        content_layout = QVBoxLayout()
        
        # Search bar
        self.search_bar = SearchBar()
        self.search_bar.search_input.textChanged.connect(self.filter_tasks)
        content_layout.addWidget(self.search_bar)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        
        # View toggle
        self.view_toggle = QButtonGroup()
        list_view_btn = QRadioButton("List View")
        card_view_btn = QRadioButton("Card View")
        card_view_btn.setChecked(True)
        self.view_toggle.addButton(list_view_btn)
        self.view_toggle.addButton(card_view_btn)
        
        # Sort options
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Due Date", "Priority", "Title"])
        self.sort_combo.currentTextChanged.connect(self.sort_tasks)
        
        for widget in [list_view_btn, card_view_btn, QLabel("Sort by:"), self.sort_combo]:
            toolbar_layout.addWidget(widget)
        
        toolbar_layout.addStretch()
        content_layout.addLayout(toolbar_layout)
        
        # Task container
        self.stack_widget = QStackedWidget()
        
        # List view
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                border: none;
                background: transparent;
            }
            QListWidget::item {
                padding: 8px;
                margin: 2px 0;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background: #e9ecef;
            }
        """)
        
        # Card view
        self.card_scroll = QScrollArea()
        self.card_container = QWidget()
        self.card_layout = QVBoxLayout()
        self.card_container.setLayout(self.card_layout)
        self.card_scroll.setWidget(self.card_container)
        self.card_scroll.setWidgetResizable(True)
        self.card_scroll.setStyleSheet("QScrollArea { border: none; }")
        
        self.stack_widget.addWidget(self.list_widget)
        self.stack_widget.addWidget(self.card_scroll)
        content_layout.addWidget(self.stack_widget)
        
        # Connect view toggle
        list_view_btn.toggled.connect(lambda: self.switch_view("list"))
        card_view_btn.toggled.connect(lambda: self.switch_view("card"))
        
        # Floating add button
        self.add_button = QToolButton(self)
        self.add_button.setText("+")
        self.add_button.setFixedSize(56, 56)
        self.add_button.clicked.connect(self.add_task)
        self.add_button.setStyleSheet("""
            QToolButton {
                background-color: #0d6efd;
                color: white;
                border-radius: 28px;
                font-size: 24px;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #0b5ed7;
            }
        """)
        
        layout.addLayout(content_layout)
        
        # Position floating button
        self.add_button.move(self.width() - 76, self.height() - 76)
        
        # Apply initial theme
        self.apply_theme()
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Update floating button position
        self.add_button.move(self.width() - 76, self.height() - 76)
    
    def switch_view(self, view_type):
        self.current_view = view_type
        self.stack_widget.setCurrentIndex(0 if view_type == "list" else 1)
        self.load_tasks()
    
    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme()
    
    def apply_theme(self):
        theme = DARK_THEME if self.current_theme == "dark" else LIGHT_THEME
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {theme['bg_primary']};
                color: {theme['text_primary']};
            }}
            QListWidget, QScrollArea, QFrame {{
                background-color: {theme['bg_secondary']};
                border: 1px solid {theme['border']};
                border-radius: 8px;
            }}
            QLineEdit, QTextEdit, QComboBox, QDateEdit {{
                background-color: {theme['bg_secondary']};
                color: {theme['text_primary']};
                border: 1px solid {theme['border']};
                padding: 8px;
                border-radius: 4px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }}
        """)
    
    def handle_navigation(self, button):
        for name, btn in self.sidebar.nav_buttons.items():
            if btn == button:
                self.current_filter = name
                break
        self.load_tasks()
    
    def filter_tasks(self):
        search_text = self.search_bar.search_input.text().lower()
        tasks = self.todo_list.get_tasks()
        
        filtered_tasks = []
        for task in tasks:
            if (search_text in task["title"].lower() or 
                search_text in task.get("description", "").lower()):
                if self.current_filter == "today":
                    if task["due_date"] == date.today().strftime("%Y-%m-%d"):
                        filtered_tasks.append(task)
                elif self.current_filter == "upcoming":
                    if task["due_date"] > date.today().strftime("%Y-%m-%d"):
                        filtered_tasks.append(task)
                elif self.current_filter == "completed":
                    if task.get("completed", False):
                        filtered_tasks.append(task)
                else:
                    filtered_tasks.append(task)
        
        self.display_tasks(filtered_tasks)
    
    def sort_tasks(self):
        sort_key = self.sort_combo.currentText()
        tasks = self.todo_list.get_tasks()
        
        if sort_key == "Due Date":
            tasks.sort(key=lambda x: x.get("due_date", ""))
        elif sort_key == "Priority":
            priority_order = {"High": 0, "Medium": 1, "Low": 2}
            tasks.sort(key=lambda x: priority_order.get(x.get("priority", "Medium"), 1))
        else:  # Title
            tasks.sort(key=lambda x: x["title"].lower())
        
        self.display_tasks(tasks)
    
    def display_tasks(self, tasks):
        if self.current_view == "list":
            self.list_widget.clear()
            for task in tasks:
                item = QListWidgetItem()
                self.set_task_item(item, task)
                self.list_widget.addItem(item)
        else:
            # Clear existing cards
            while self.card_layout.count():
                child = self.card_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            
            # Add new cards
            for task in tasks:
                card = TaskCard(task)
                card.taskChanged.connect(self.handle_task_change)
                self.card_layout.addWidget(card)
            self.card_layout.addStretch()
    
    def handle_task_change(self, task_id):
        task = self.todo_list.get_task(task_id)
        if task:
            self.todo_list.update_task(task_id, task)
            self.load_tasks()
    
    def load_tasks(self):
        tasks = self.todo_list.get_tasks()
        self.display_tasks(tasks)
    
    def set_task_item(self, item, task):
        title = task["title"]
        if task["completed"]:
            title = "✓ " + title
        item.setText(title)
        item.setData(Qt.UserRole, task)
        
        if task["completed"]:
            item.setForeground(QColor(LIGHT_THEME["success"]))
    
    def add_task(self):
        dialog = TaskEditDialog(self)
        if dialog.exec_():
            task_data = dialog.get_task_data()
            task_data["completed"] = False
            task_data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.todo_list.add_task(task_data)
            self.load_tasks()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = ModernTodoApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 