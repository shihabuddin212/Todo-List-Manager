#!/usr/bin/env python3

import os
import json
from datetime import datetime

class TodoList:
    def __init__(self, filename="tasks.json"):
        self.filename = filename
        self.tasks = []
        self.load_tasks()

    def load_tasks(self):
        """Load tasks from JSON file"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    self.tasks = json.load(f)
            except json.JSONDecodeError:
                self.tasks = []
        else:
            self.tasks = []

    def save_tasks(self):
        """Save tasks to JSON file"""
        with open(self.filename, 'w') as f:
            json.dump(self.tasks, f, indent=4)

    def add_task(self, task):
        """Add a new task"""
        task["id"] = self._generate_id()
        task["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.tasks.append(task)
        self.save_tasks()
        return task

    def update_task(self, task_id, updated_data):
        """Update an existing task"""
        for task in self.tasks:
            if task["id"] == task_id:
                task.update(updated_data)
                self.save_tasks()
                return task
        return None

    def delete_task(self, task_id):
        """Delete a task"""
        self.tasks = [task for task in self.tasks if task["id"] != task_id]
        self.save_tasks()

    def get_tasks(self):
        """Get all tasks"""
        return self.tasks

    def get_task(self, task_id):
        """Get a specific task by ID"""
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        return None

    def _generate_id(self):
        """Generate a unique ID for a task"""
        existing_ids = {task["id"] for task in self.tasks}
        new_id = 1
        while new_id in existing_ids:
            new_id += 1
        return new_id

def print_task(task):
    """Format and print a task."""
    status = "✓" if task["completed"] else "✗"
    print(f"[{status}] {task['id']}. {task['title']}")
    if task["description"]:
        print(f"   Description: {task['description']}")
    print(f"   Created: {task['created_at']}")
    if task["completed"]:
        print(f"   Completed: {task['completed_at']}")
    print()

def main():
    todo_list = TodoList()
    
    while True:
        print("\n===== Todo List Manager =====")
        print("1. Add Task")
        print("2. View All Tasks")
        print("3. Mark Task as Completed")
        print("4. Delete Task")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == "1":
            title = input("Enter task title: ")
            description = input("Enter task description (optional): ")
            task = todo_list.add_task({"title": title, "description": description, "completed": False})
            print(f"\nTask added with ID: {task['id']}")
            
        elif choice == "2":
            tasks = todo_list.get_tasks()
            if not tasks:
                print("\nNo tasks found.")
            else:
                print("\n--- Your Tasks ---")
                for task in tasks:
                    print_task(task)
                    
        elif choice == "3":
            task_id = input("Enter task ID to mark as completed: ")
            if task_id.isdigit():
                task = todo_list.get_task(int(task_id))
                if task:
                    task["completed"] = True
                    task["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    todo_list.update_task(int(task_id), task)
                    print(f"\nTask {task_id} marked as completed.")
                else:
                    print(f"\nTask with ID {task_id} not found.")
            else:
                print("\nInvalid task ID.")
                
        elif choice == "4":
            task_id = input("Enter task ID to delete: ")
            if task_id.isdigit():
                if todo_list.delete_task(int(task_id)):
                    print(f"\nTask {task_id} deleted.")
                else:
                    print(f"\nTask with ID {task_id} not found.")
            else:
                print("\nInvalid task ID.")
                
        elif choice == "5":
            print("\nGoodbye!")
            break
            
        else:
            print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    main() 