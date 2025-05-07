#!/usr/bin/env python3

import sys
import os

# Try to import PyQt5, install if not available
try:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                QHBoxLayout, QListWidget, QPushButton, QLabel, 
                                QLineEdit, QTextEdit, QDialog, QMessageBox,
                                QListWidgetItem, QFrame, QSplitter)
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont, QColor
except ImportError:
    import subprocess
    print("PyQt5 not found. Attempting to install...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt5"])
        from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                    QHBoxLayout, QListWidget, QPushButton, QLabel, 
                                    QLineEdit, QTextEdit, QDialog, QMessageBox,
                                    QListWidgetItem, QFrame, QSplitter)
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont, QColor
        print("PyQt5 installed successfully.")
    except Exception as e:
        print(f"Error installing PyQt5: {e}")
        print("Please install PyQt5 manually with: pip install PyQt5")
        sys.exit(1)

from todo import TodoList

# Set application icon
ICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "todo_icon.ico")

class TaskDialog(QDialog):
    def __init__(self, parent=None, task=None):
        super().__init__(parent)
        self.task = task
        self.setWindowTitle("Add Task" if not task else "Edit Task")
        self.setMinimumWidth(400)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Title:")
        self.title_input = QLineEdit()
        if self.task:
            self.title_input.setText(self.task["title"])
        layout.addWidget(title_label)
        layout.addWidget(self.title_input)
        
        # Description
        desc_label = QLabel("Description:")
        self.desc_input = QTextEdit()
        if self.task:
            self.desc_input.setText(self.task["description"])
        layout.addWidget(desc_label)
        layout.addWidget(self.desc_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.cancel_btn = QPushButton("Cancel")
        self.save_btn = QPushButton("Save")
        self.save_btn.setDefault(True)
        
        self.cancel_btn.clicked.connect(self.reject)
        self.save_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def get_task_data(self):
        return {
            "title": self.title_input.text(),
            "description": self.desc_input.toPlainText()
        }


class TaskDetailsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        self.title_label = QLabel("Title:")
        self.title_text = QLabel()
        self.title_text.setWordWrap(True)
        self.title_text.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        # Description
        self.desc_label = QLabel("Description:")
        self.desc_text = QLabel()
        self.desc_text.setWordWrap(True)
        
        # Status
        self.status_label = QLabel("Status:")
        self.status_text = QLabel()
        
        # Created at
        self.created_label = QLabel("Created:")
        self.created_text = QLabel()
        
        # Edit button
        self.edit_btn = QPushButton("Edit Task")
        self.edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        # Add widgets to layout
        layout.addWidget(self.title_label)
        layout.addWidget(self.title_text)
        layout.addSpacing(10)
        layout.addWidget(self.desc_label)
        layout.addWidget(self.desc_text)
        layout.addSpacing(10)
        layout.addWidget(self.status_label)
        layout.addWidget(self.status_text)
        layout.addSpacing(10)
        layout.addWidget(self.created_label)
        layout.addWidget(self.created_text)
        layout.addSpacing(20)
        layout.addWidget(self.edit_btn)
        layout.addStretch()
        
        self.setLayout(layout)
        
    def update_task(self, task):
        """Update the details widget with task information"""
        if task:
            self.title_text.setText(task["title"])
            self.desc_text.setText(task["description"] if task["description"] else "No description")
            self.status_text.setText("Completed" if task["completed"] else "Pending")
            self.created_text.setText(task["created_at"])
            
            # Set status color
            self.status_text.setStyleSheet(
                "color: green; font-weight: bold;" if task["completed"] else "color: orange; font-weight: bold;"
            )
            
            self.setVisible(True)
        else:
            self.setVisible(False)


class TodoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.todo_list = TodoList()
        self.current_task = None
        self.init_ui()
        self.load_tasks()
        
    def init_ui(self):
        self.setWindowTitle("Todo List Manager")
        self.setMinimumSize(1000, 600)
        
        # Set application icon if exists
        if os.path.exists(ICON_PATH):
            from PyQt5.QtGui import QIcon
            self.setWindowIcon(QIcon(ICON_PATH))
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        
        # Title
        title_label = QLabel("Todo List Manager")
        title_font = title_label.font()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Create splitter for task list and details
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Task list
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        
        self.task_list = QListWidget()
        self.task_list.setAlternatingRowColors(True)
        self.task_list.itemClicked.connect(self.show_task_details)
        self.task_list.itemDoubleClicked.connect(self.edit_task)
        
        left_layout.addWidget(QLabel("Tasks (double-click to edit):"))
        left_layout.addWidget(self.task_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Add Task")
        self.edit_btn = QPushButton("Edit Task")
        self.complete_btn = QPushButton("Mark Completed")
        self.delete_btn = QPushButton("Delete Task")
        
        self.add_btn.clicked.connect(self.add_task)
        self.edit_btn.clicked.connect(self.edit_current_task)
        self.complete_btn.clicked.connect(self.mark_completed)
        self.delete_btn.clicked.connect(self.delete_task)
        
        # Set minimum width for buttons
        min_button_width = 150
        self.add_btn.setMinimumWidth(min_button_width)
        self.edit_btn.setMinimumWidth(min_button_width)
        self.complete_btn.setMinimumWidth(min_button_width)
        self.delete_btn.setMinimumWidth(min_button_width)
        
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.complete_btn)
        button_layout.addWidget(self.delete_btn)
        
        left_layout.addLayout(button_layout)
        left_widget.setLayout(left_layout)
        
        # Right side - Task details
        self.details_widget = TaskDetailsWidget()
        self.details_widget.edit_btn.clicked.connect(self.edit_current_task)
        self.details_widget.setVisible(False)
        
        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(self.details_widget)
        
        # Set initial splitter sizes (60% list, 40% details)
        splitter.setSizes([600, 400])
        
        layout.addWidget(splitter)
        
        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QListWidget {
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QLabel {
                font-size: 13px;
            }
        """)
    
    def load_tasks(self):
        """Load tasks from TodoList into the GUI"""
        self.task_list.clear()
        for task in self.todo_list.get_tasks():        
            item = QListWidgetItem()
            self.set_task_item(item, task)
            self.task_list.addItem(item)
    
    def set_task_item(self, item, task):
        """Format the list item to display task info"""
        status = "✓" if task["completed"] else "❒"
        item.setText(f"{status} {task['id']}. {task['title']}")
        item.setData(Qt.UserRole, task["id"])
        
        if task["completed"]:
            item.setForeground(QColor("green"))
        
        if task["description"]:
            item.setToolTip(task["description"])
    
    def show_task_details(self, item):
        """Show task details when a task is selected"""
        task_id = item.data(Qt.UserRole)
        task = self.todo_list.get_task(task_id)
        if task:
            self.current_task = task
            self.details_widget.update_task(task)
    
    def edit_current_task(self):
        """Edit the currently displayed task"""
        if self.current_task:
            self.edit_task(self.task_list.currentItem())
    
    def edit_task(self, item):
        """Edit the selected task"""
        task_id = item.data(Qt.UserRole)
        task = self.todo_list.get_task(task_id)
        if task:
            dialog = TaskDialog(self, task)
            if dialog.exec_() == QDialog.Accepted:
                task_data = dialog.get_task_data()
                if task_data["title"].strip():
                    # Update task in the list
                    task["title"] = task_data["title"]
                    task["description"] = task_data["description"]
                    self.todo_list.save_tasks()
                    
                    # Update UI
                    self.set_task_item(item, task)
                    self.show_task_details(item)
                    QMessageBox.information(self, "Success", "Task updated successfully!")
                else:
                    QMessageBox.warning(self, "Error", "Task title cannot be empty!")
    
    def add_task(self):
        """Open dialog to add a new task"""
        dialog = TaskDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            task_data = dialog.get_task_data()
            if task_data["title"].strip():
                task = self.todo_list.add_task(task_data["title"], task_data["description"])
                item = QListWidgetItem()
                self.set_task_item(item, task)
                self.task_list.addItem(item)
                
                # Select the new task
                self.task_list.setCurrentItem(item)
                self.show_task_details(item)
                
                QMessageBox.information(self, "Success", "Task added successfully!")
            else:
                QMessageBox.warning(self, "Error", "Task title cannot be empty!")
    
    def mark_completed(self):
        """Mark the selected task as completed"""
        current_item = self.task_list.currentItem()
        if current_item:
            task_id = current_item.data(Qt.UserRole)
            if self.todo_list.mark_completed(task_id):
                task = self.todo_list.get_task_by_id(task_id)
                self.set_task_item(current_item, task)
                self.show_task_details(current_item)
                QMessageBox.information(self, "Success", "Task marked as completed!")
            else:
                QMessageBox.warning(self, "Error", "Could not mark task as completed!")
        else:
            QMessageBox.warning(self, "Error", "Please select a task first!")
    
    def delete_task(self):
        """Delete the selected task"""
        current_item = self.task_list.currentItem()
        if current_item:
            task_id = current_item.data(Qt.UserRole)
            task = self.todo_list.get_task_by_id(task_id)
            
            reply = QMessageBox.question(
                self,
                "Confirm Deletion",
                f"Are you sure you want to delete task '{task['title']}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if self.todo_list.delete_task(task_id):
                    self.load_tasks()
                    self.details_widget.setVisible(False)
                    self.current_task = None
                    QMessageBox.information(self, "Success", "Task deleted successfully!")
                else:
                    QMessageBox.warning(self, "Error", "Could not delete task!")
        else:
            QMessageBox.warning(self, "Error", "Please select a task first!")


def main():
    app = QApplication(sys.argv)
    window = TodoApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main() 