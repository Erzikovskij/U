# Импорт необходимых модулей
import sqlite3  # Для работы с SQLite базой данных
from datetime import datetime  # Для работы с датами
from typing import List, Dict, Optional  # Для аннотации типов

class Student:
    """Класс, представляющий студента с его данными и зачеткой"""
    
    def __init__(self, last_name: str, first_name: str, birth_date: str):
        """
        Инициализация объекта студента
        :param last_name: Фамилия студента
        :param first_name: Имя студента
        :param birth_date: Дата рождения в формате ГГГГ-ММ-ДД
        """
        self.last_name = last_name
        self.first_name = first_name
        self.birth_date = birth_date
        self.record_book: List[Dict] = []  # Зачетка - список словарей с информацией об экзаменах
    
    def add_exam(self, subject: str, exam_date: str, teacher_name: str):
        """
        Добавляет экзамен в зачетку студента
        :param subject: Название предмета
        :param exam_date: Дата экзамена в формате ГГГГ-ММ-ДД
        :param teacher_name: ФИО преподавателя
        """
        self.record_book.append({
            'subject': subject,
            'exam_date': exam_date,
            'teacher_name': teacher_name
        })
    
    def __str__(self):
        """Строковое представление студента (ФИО и дата рождения)"""
        return f"{self.last_name} {self.first_name} ({self.birth_date})"

class Group:
    """Класс, представляющий учебную группу студентов"""
    
    def __init__(self):
        """Инициализация пустой группы"""
        self.students: List[Student] = []  # Список студентов в группе
    
    def add_student(self, student: Student):
        """Добавляет студента в группу"""
        self.students.append(student)
    
    def print_students_table(self):
        """Выводит таблицу с ФИО и датами рождения всех студентов группы"""
        print("\nСписок студентов группы:")
        print("-" * 50)
        # Шапка таблицы
        print(f"{'№':<3} | {'Фамилия':<15} | {'Имя':<15} | {'Дата рождения':<12}")
        print("-" * 50)
        # Данные студентов
        for i, student in enumerate(self.students, 1):
            print(f"{i:<3} | {student.last_name:<15} | {student.first_name:<15} | {student.birth_date:<12}")
        print("-" * 50)
    
    def save_to_db(self, db_name: str = "students.db"):
        """
        Сохраняет данные группы в SQLite базу данных
        :param db_name: Имя файла базы данных (по умолчанию students.db)
        """
        conn = sqlite3.connect(db_name)  # Подключаемся к базе данных
        cursor = conn.cursor()  # Создаем курсор для выполнения SQL-запросов
        
        # Создаем таблицу студентов, если она не существует
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  # Уникальный идентификатор
            last_name TEXT NOT NULL,              # Фамилия
            first_name TEXT NOT NULL,             # Имя
            birth_date TEXT NOT NULL              # Дата рождения
        )
        ''')
        
        # Создаем таблицу экзаменов, если она не существует
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  # Уникальный идентификатор
            student_id INTEGER NOT NULL,           # ID студента (внешний ключ)
            subject TEXT NOT NULL,                 # Название предмета
            exam_date TEXT NOT NULL,               # Дата экзамена
            teacher_name TEXT NOT NULL,            # ФИО преподавателя
            FOREIGN KEY (student_id) REFERENCES students (id)  # Связь с таблицей студентов
        )
        ''')
        
        # Очищаем таблицы перед добавлением новых данных (чтобы избежать дублирования)
        cursor.execute("DELETE FROM exams")
        cursor.execute("DELETE FROM students")
        
        