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
        
        # Добавляем студентов в базу данных
        for student in self.students:
            cursor.execute(
                "INSERT INTO students (last_name, first_name, birth_date) VALUES (?, ?, ?)",
                (student.last_name, student.first_name, student.birth_date)
            )
            student_id = cursor.lastrowid  # Получаем ID только что добавленного студента
            
            # Добавляем экзамены этого студента
            for exam in student.record_book:
                cursor.execute(
                    "INSERT INTO exams (student_id, subject, exam_date, teacher_name) VALUES (?, ?, ?, ?)",
                    (student_id, exam['subject'], exam['exam_date'], exam['teacher_name'])
                )
        
        conn.commit()  # Сохраняем изменения
        conn.close()   # Закрываем соединение
        print(f"\nДанные сохранены в базу данных {db_name}")
    
    @classmethod
    def load_from_db(cls, db_name: str = "students.db") -> Optional['Group']:
        """
        Загружает данные группы из SQLite базы данных
        :param db_name: Имя файла базы данных (по умолчанию students.db)
        :return: Объект Group с загруженными данными или None, если произошла ошибка
        """
        try:
            conn = sqlite3.connect(db_name)  # Подключаемся к базе данных
            cursor = conn.cursor()          # Создаем курсор
            
            # Получаем всех студентов из базы
            cursor.execute("SELECT id, last_name, first_name, birth_date FROM students")
            students_data = cursor.fetchall()
            
            # Если нет данных, возвращаем None
            if not students_data:
                return None
            
            # Создаем новую группу
            group = cls()
            
            # Обрабатываем каждого студента
            for student_id, last_name, first_name, birth_date in students_data:
                student = Student(last_name, first_name, birth_date)
                
                # Получаем все экзамены этого студента
                cursor.execute(
                    "SELECT subject, exam_date, teacher_name FROM exams WHERE student_id = ?",
                    (student_id,)
                )
                exams_data = cursor.fetchall()
                
                # Добавляем экзамены в зачетку студента
                for subject, exam_date, teacher_name in exams_data:
                    student.add_exam(subject, exam_date, teacher_name)
                
                # Добавляем студента в группу
                group.add_student(student)
            
            conn.close()  # Закрываем соединение
            return group
        
        except sqlite3.Error:  # Если произошла ошибка при работе с базой
            return None

def input_student_data() -> Student:
    """Функция для ввода данных о студенте с клавиатуры"""
    print("\nВведите данные студента:")
    last_name = input("Фамилия: ")
    first_name = input("Имя: ")
    birth_date = input("Дата рождения (ГГГГ-ММ-ДД): ")
    
    # Создаем объект студента
    student = Student(last_name, first_name, birth_date)
    
    # Добавляем экзамены (от 3 до 5)
    print("\nДобавьте экзамены в зачетку (от 3 до 5):")
    exam_count = 0
    while exam_count < 5:
        # После 3 экзаменов спрашиваем, нужно ли добавить еще
        if exam_count >= 3:
            more = input(f"Добавлено {exam_count} экзаменов. Добавить еще? (y/n): ")
            if more.lower() != 'y':
                break
        
        # Ввод данных об экзамене
        subject = input("Предмет: ")
        exam_date = input("Дата экзамена (ГГГГ-ММ-ДД): ")
        teacher_name = input("ФИО преподавателя: ")
        
        # Добавляем экзамен в зачетку
        student.add_exam(subject, exam_date, teacher_name)
        exam_count += 1
    
    return student

def main():
    """Основная функция программы"""
    group = Group()  # Создаем пустую группу
    
    # Выбор способа загрузки данных
    print("1. Ввести данные студентов вручную")
    print("2. Загрузить данные из базы данных")
    choice = input("Выберите вариант: ")
    
    if choice == "1":
        # Ручной ввод данных
        try:
            num_students = int(input("Введите количество студентов в группе: "))
            for _ in range(num_students):
                student = input_student_data()  # Ввод данных студента
                group.add_student(student)     # Добавление студента в группу
            
            group.save_to_db()  # Сохранение в базу данных
        except ValueError:
            print("Ошибка: введите корректное число")
    elif choice == "2":
        # Загрузка из базы данных
        loaded_group = Group.load_from_db()
        if loaded_group:
            group = loaded_group
            print("Данные успешно загружены из базы данных")
        else:
            print("Не удалось загрузить данные из базы данных или база данных пуста")
            return
    else:
        print("Некорректный выбор")
        return
    
    # Основной цикл программы
    while True:
        print("\nМеню:")
        print("1. Вывести список студентов")
        print("2. Добавить нового студента")
        print("3. Сохранить данные в базу")
        print("4. Выход")
        
        choice = input("Выберите действие: ")
        
        if choice == "1":
            group.print_students_table()  # Вывод таблицы студентов
        elif choice == "2":
            student = input_student_data()  # Добавление нового студента
            group.add_student(student)
        elif choice == "3":
            group.save_to_db()  # Сохранение данных
        elif choice == "4":
            break  # Выход из программы
        else:
            print("Некорректный выбор")

if __name__ == "__main__":
    main()