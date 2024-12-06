from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QWidget, QDialog, QFormLayout, QLineEdit,
    QDateEdit, QMessageBox, QHeaderView, QComboBox, QSpinBox, QCheckBox
)
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import black
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QDate
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from user_class import Connect, Employee, EmployeeEducation, Education, EmployeePosition, Position, EmployeeTraining, Training
import sys


class EmployeeForm(QDialog):
    def __init__(self, session, employee=None):
        super().__init__()
        self.session = session
        self.employee = employee
        self.setWindowTitle("Добавление/Редактирование сотрудника")
        self.setWindowIcon(QIcon('add.png'))
        self.layout = QFormLayout(self)

        # Поля ввода
        self.last_name = QLineEdit()
        self.first_name = QLineEdit()
        self.middle_name = QLineEdit()
        self.phone_number = QLineEdit()
        self.birth_date = QDateEdit(calendarPopup=True)
        self.birth_date.setDate(QDate.currentDate())
        self.snils = QLineEdit()
        self.inn = QLineEdit()
        self.passport_id = QLineEdit()
        self.work_experience_years = QSpinBox()
        self.work_experience_years.setRange(0, 50)
        self.marital_status = QComboBox()
        self.marital_status.addItems(['Холост/Не замужем', 'Женат/За мужем', 'Разведён/Разведена', 'Вдова/Вдовец'])
        self.employment_date = QDateEdit(calendarPopup=True)
        self.employment_date.setDate(QDate.currentDate())
        self.education = QComboBox()
        self.position = QComboBox()
        self.department = QComboBox()
        self.department.addItems(['Отдел продаж', 'Бухгалтерия', 'IT отдел'])

        # Добавление полей
        self.layout.addRow("Фамилия", self.last_name)
        self.layout.addRow("Имя", self.first_name)
        self.layout.addRow("Отчество", self.middle_name)
        self.layout.addRow("Телефон", self.phone_number)
        self.layout.addRow("Дата рождения", self.birth_date)
        self.layout.addRow("СНИЛС", self.snils)
        self.layout.addRow("ИНН", self.inn)
        self.layout.addRow("Паспорт ID", self.passport_id)
        self.layout.addRow("Стаж (лет)", self.work_experience_years)
        self.layout.addRow("Семейное положение", self.marital_status)
        self.layout.addRow("Дата трудоустройства", self.employment_date)
        self.layout.addRow("Образование", self.education)
        self.layout.addRow("Должность", self.position)
        self.layout.addRow("Отдел", self.department)

        
        self.btn_save = QPushButton("Сохранить")
        self.btn_save.clicked.connect(self.save_employee)
        self.layout.addWidget(self.btn_save)

        
        self.load_options()

        if self.employee:
            self.load_employee_data()

    def load_options(self):
        education_records = self.session.query(Education).all()
        for education in education_records:
            self.education.addItem(f"{education.level} - {education.specialty.full_name}", education.id)

        position_records = self.session.query(Position).all()
        for position in position_records:
            self.position.addItem(position.name, position.id)

    def load_employee_data(self):
        self.last_name.setText(self.employee.last_name)
        self.first_name.setText(self.employee.first_name)
        self.middle_name.setText(self.employee.middle_name or "")
        self.phone_number.setText(self.employee.phone_number or "")
        self.birth_date.setDate(QDate(self.employee.birth_date.year, self.employee.birth_date.month, self.employee.birth_date.day))
        self.snils.setText(self.employee.snils)
        self.inn.setText(self.employee.inn)
        self.passport_id.setText(str(self.employee.passport_id) if self.employee.passport_id else "")
        self.work_experience_years.setValue(self.employee.work_experience_years)
        self.marital_status.setCurrentText(self.employee.marital_status)
        self.employment_date.setDate(QDate(self.employee.employment_date.year, self.employee.employment_date.month, self.employee.employment_date.day))

    
        empl_education = self.session.query(EmployeeEducation).filter_by(employee_id=self.employee.id).first()
        if empl_education:
            self.education.setCurrentIndex(self.education.findData(empl_education.education_id))

        empl_position = self.session.query(EmployeePosition).filter_by(employee_id=self.employee.id).first()
        if empl_position:
            self.position.setCurrentIndex(self.position.findData(empl_position.position_id))
            self.department.setCurrentText(empl_position.department)

    def save_employee(self):
        """Сохранение данных о сотрудниках в базу данных."""
        try:
            if not self.employee:
                self.employee = Employee()
                self.session.add(self.employee)

            self.employee.last_name = self.last_name.text()
            self.employee.first_name = self.first_name.text()
            self.employee.middle_name = self.middle_name.text() or None
            self.employee.phone_number = self.phone_number.text() or None
            self.employee.birth_date = self.birth_date.date().toPython()
            self.employee.snils = self.snils.text()
            self.employee.inn = self.inn.text()
            self.employee.passport_id = int(self.passport_id.text()) if self.passport_id.text() else None
            self.employee.work_experience_years = self.work_experience_years.value()
            self.employee.marital_status = self.marital_status.currentText()
            self.employee.employment_date = self.employment_date.date().toPython()
            self.employee.delete = False

            self.session.commit()

            
            empl_education = self.session.query(EmployeeEducation).filter_by(employee_id=self.employee.id).first()
            if not empl_education:
                empl_education = EmployeeEducation(employee_id=self.employee.id)
                self.session.add(empl_education)
            empl_education.education_id = self.education.currentData()

            empl_position = self.session.query(EmployeePosition).filter_by(employee_id=self.employee.id).first()
            if not empl_position:
                empl_position = EmployeePosition(employee_id=self.employee.id)
                self.session.add(empl_position)
            empl_position.position_id = self.position.currentData()
            empl_position.department = self.department.currentText()

            self.session.commit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения данных: {e}")
            
            
class TrainingForm(QDialog):
    def __init__(self, session):
        super().__init__()
        self.session = session
        self.setWindowTitle("Добавление обучения сотрудника")
        self.setWindowIcon(QIcon('add.png'))
        self.layout = QFormLayout(self)

        # Список сотрудников
        self.employee_combo = QComboBox()
        self.load_employees()  # Заполнение комбобокса сотрудников
        self.layout.addRow("Сотрудник", self.employee_combo)

        # Список обучения
        self.training_combo = QComboBox()
        self.load_trainings()  # Заполнение комбобокса обучения
        self.layout.addRow("Обучение", self.training_combo)

        # Статус завершенности обучения
        self.training_completed = QCheckBox("Обучение завершено")
        self.layout.addRow(self.training_completed)

        # Номер документа
        self.document_number_input = QLineEdit()
        self.layout.addRow("Номер документа", self.document_number_input)

        # Кнопки
        self.btn_save = QPushButton("Сохранить")
        self.btn_save.clicked.connect(self.save_training)
        self.layout.addWidget(self.btn_save)

    def load_employees(self):
        """Загрузка сотрудников в комбобокс."""
        employees = self.session.query(Employee).filter(Employee.delete == False).all()
        for empl in employees:
            self.employee_combo.addItem(f"{empl.last_name} {empl.first_name} {empl.middle_name}", empl.id)

    def load_trainings(self):
        """Загрузка обучения в комбобокс."""
        trainings = self.session.query(Training).all()
        for training in trainings:
            self.training_combo.addItem(training.name, training.id)

    def save_training(self):
        """Сохранение данных об обучении в базе данных."""
        employee_id = self.employee_combo.currentData()  # Получаем ID выбранного сотрудника
        training_id = self.training_combo.currentData()  # Получаем ID выбранного обучения
        training_completed = self.training_completed.isChecked()  # Получаем статус завершенности
        document_number = self.document_number_input.text()  # Получаем номер документа

        new_training = EmployeeTraining(
            employee_id=employee_id,
            training_id=training_id,
            training_completed=training_completed,
            document_number=document_number
        )

        self.session.add(new_training)
        self.session.commit()
        QMessageBox.information(self, "Успех", "Данные об обучении успешно добавлены.")
        self.accept()
        



class ReportForm(QDialog):
    def __init__(self, session):
        super().__init__()
        self.session = session
        self.setWindowTitle("Формирование отчетов")
        self.setWindowIcon(QIcon('report.png'))
        self.setFixedSize(400, 300)
        
        self.layout = QFormLayout(self)

        # Поля для ввода периода
        self.start_date_edit = QDateEdit()
        self.end_date_edit = QDateEdit()
        self.layout.addRow("Дата начала:", self.start_date_edit)
        self.layout.addRow("Дата окончания:", self.end_date_edit)

        # Кнопка для формирования отчета
        self.btn_generate_reports = QPushButton("Сформировать отчеты")
        self.btn_generate_reports.clicked.connect(self.generate_reports)
        self.layout.addRow(self.btn_generate_reports)

    def generate_reports(self):
        try:
            """Генерация отчетов в PDF."""
            start_date = self.start_date_edit.date().toPython()  # QDate -> datetime.date
            end_date = self.end_date_edit.date().toPython()   

            self.generate_training_report(start_date, end_date)
            self.generate_employee_cards_report()

            QMessageBox.information(self, "Успех", "Отчеты успешно сгенерированы.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))    

    def generate_training_report(self, start_date, end_date):
        """Генерация отчета об обучении сотрудников."""
        file_path = "training_report.pdf"
        c = canvas.Canvas("training_report.pdf", pagesize=A4)
        pdfmetrics.registerFont(TTFont("DejaVuSans", "DejaVuSans.ttf"))
        c.setFont("DejaVuSans", 14)
        c.drawString(100, 750, "Отчет об обучении сотрудников")
        c.setFont("DejaVuSans", 14)
        c.drawString(100, 730, f"Период: {start_date} - {end_date}")

        # Запрос данных об обучении сотрудников
        trainings = self.session.query(EmployeeTraining).join(Training).filter(
            EmployeeTraining.training_completed == True,
            Training.start_date >= start_date,
            Training.end_date <= end_date
        ).all()

        total_completed = len(trainings)
        c.setFont("DejaVuSans", 14)
        c.drawString(100, 690, f"Всего завершено обучений: {total_completed}")


        # Дополнительная информация по каждому обучению
        y_position = 650
        for training in trainings:
            employee = training.employee
            c.setFont("DejaVuSans", 14)
            c.drawString(100, y_position, f"Сотрудник: {employee.last_name} {employee.first_name}")
            y_position -= 20
            c.setFont("DejaVuSans", 14)
            c.drawString(100, y_position, f"Курс: {training.training.name}")
            y_position -= 30  # Сдвиг для следующей строки

        c.save()

    def generate_employee_cards_report(self):
        """Генерация отчета по карточкам сотрудников."""
        file_path = "employee_cards_report.pdf"
        c = canvas.Canvas("employee_cards_report.pdf", pagesize=A4)
        pdfmetrics.registerFont(TTFont("DejaVuSans", "DejaVuSans.ttf"))
        c.setFont("DejaVuSans", 14)
        c.drawString(100, 750, "Карточки сотрудников")

        # Запрос данных о всех сотрудниках
        employees = self.session.query(Employee).filter(Employee.delete == False).all()

        y_position = 730
        for empl in employees:
            c.setFont("DejaVuSans", 14)
            c.drawString(100, y_position, f"Сотрудник: {empl.last_name} {empl.first_name} {empl.middle_name or ''}")
            y_position -= 20
            # Получаем курсы обучения для каждого сотрудника
            trainings = self.session.query(EmployeeTraining).filter(EmployeeTraining.employee_id == empl.id).all()
            training_names = [training.training.name for training in trainings if training.training]
            c.setFont("DejaVuSans", 14)
            c.drawString(100, y_position, f"Курсы: {', '.join(training_names)}")
            y_position -= 30  # Сдвиг для следующей строки

        c.save()



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Мини проект №2")
        self.setWindowIcon(QIcon('profile.png'))
        self.setFixedSize(1500, 650)

        # Основной виджет и компоновка
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # Панель управления (кнопки)
        self.control_panel = QHBoxLayout()
        self.btn_add_employee = QPushButton("Добавить сотрудника")
        self.btn_delete_employee = QPushButton("Удалить сотрудника")
        self.btn_add_training = QPushButton("Добавить обучение")  # Кнопка для добавления обучения
        self.btn_generate_report = QPushButton("Сформировать отчет") 

        # Добавление кнопок в панель управления
        self.control_panel.addWidget(self.btn_add_employee)
        self.control_panel.addWidget(self.btn_add_training)  # Добавляем кнопку для добавления обучения
        self.control_panel.addWidget(self.btn_delete_employee)
        self.control_panel.addWidget(self.btn_generate_report)

        # Подключение кнопок к обработчикам
        self.btn_add_employee.clicked.connect(self.add_employee_form)
        self.btn_delete_employee.clicked.connect(self.delete_employee)
        self.btn_add_training.clicked.connect(self.add_training_form)  # Обработчик для добавления обучения
        self.btn_generate_report.clicked.connect(self.open_report_form) 

        # Таблица для отображения данных сотрудников
        self.table = QTableWidget()
        self.table.setColumnCount(8)  # Увеличиваем количество столбцов
        self.table.setHorizontalHeaderLabels([
            "ID", "Фамилия", "Имя", "Отчество", "Дата трудоустройства", "Образование", "Должность", "Отдел"
        ])
        
        self.table.setColumnHidden(0, True)  # Скрываем столбец ID
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Добавление панели управления и таблицы в основной макет
        main_layout.addLayout(self.control_panel)  # Панель управления
        main_layout.addWidget(self.table)          # Таблица

        # Подключение базы данных
        self.session = Connect.create_connection()
        self.load_employees()

        # Включение редактирования по двойному клику
        self.table.cellDoubleClicked.connect(self.edit_employee)

    def load_employees(self):
        """Загрузка сотрудников из базы данных в таблицу."""
        self.table.setRowCount(0)  # Очистка таблицы

        try:
            employees = self.session.query(Employee).filter(Employee.delete == False).all()
            if not employees:
                print("Нет сотрудников для отображения.")
                return

            print(f"Загружено сотрудников: {len(employees)}")

            for empl in employees:
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)

                # Получение образования сотрудника
                empl_education = self.session.query(EmployeeEducation).filter_by(employee_id=empl.id).first()
                education_text = ""
                if empl_education:
                    education = self.session.query(Education).get(empl_education.education_id)
                    if education:
                        education_text = f"{education.level} - {education.specialty.full_name}"

                # Получение должности сотрудника
                empl_position = self.session.query(EmployeePosition).filter_by(employee_id=empl.id).first()
                position_text = ""
                department_text = ""
                if empl_position:
                    position = self.session.query(Position).get(empl_position.position_id)
                    if position:
                        position_text = position.name
                    department_text = empl_position.department or ""

                # Заполнение строки таблицы
                self.table.setItem(row_position, 0, QTableWidgetItem(str(empl.id)))
                self.table.setItem(row_position, 1, QTableWidgetItem(empl.last_name))
                self.table.setItem(row_position, 2, QTableWidgetItem(empl.first_name))
                self.table.setItem(row_position, 3, QTableWidgetItem(empl.middle_name or ""))
                self.table.setItem(row_position, 4, QTableWidgetItem(empl.employment_date.strftime('%Y-%m-%d')))
                self.table.setItem(row_position, 5, QTableWidgetItem(education_text))
                self.table.setItem(row_position, 6, QTableWidgetItem(position_text))
                self.table.setItem(row_position, 7, QTableWidgetItem(department_text))

            print("Загрузка сотрудников завершена успешно.")
        except Exception as e:
            print(f"Ошибка при загрузке сотрудников: {e}")

            
    def add_employee_form(self):
        """Открытие формы для добавления нового сотрудника."""
        dialog = EmployeeForm(self.session)
        if dialog.exec() == QDialog.Accepted:
            self.load_employees()

    def edit_employee(self, row):
        """Открытие формы редактирования сотрудника."""
        employee_last_name = self.table.item(row, 0).text()
        employee = self.session.query(Employee).filter(Employee.last_name == employee_last_name).first()
        if employee:
            dialog = EmployeeForm(self.session, employee)
            if dialog.exec() == QDialog.Accepted:
                self.load_employees()

    def delete_employee(self):
        """Удаление выбранного сотрудника по ID."""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите сотрудника для удаления.")
            return

        # Получение ID сотрудника из скрытого столбца
        employee_id_item = self.table.item(selected_row, 0)  # Предположим, что ID в первом столбце
        if not employee_id_item or not employee_id_item.text().isdigit():
            QMessageBox.warning(self, "Ошибка", "Не удалось определить ID выбранного сотрудника.")
            return

        employee_id = int(employee_id_item.text())
        employee = self.session.query(Employee).get(employee_id)

        if employee:
            confirm = QMessageBox.question(
                self, "Подтверждение удаления",
                f"Вы уверены, что хотите удалить сотрудника с ID {employee_id} ({employee.last_name} {employee.first_name})?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                employee.delete = True
                self.session.commit()
                QMessageBox.information(self, "Успех", f"Сотрудник с ID {employee_id} успешно удален.")
                self.load_employees()
        else:
            QMessageBox.warning(self, "Ошибка", "Сотрудник не найден.")
            
            
    def add_training_form(self):
        """Открытие формы добавления обучения."""
        form = TrainingForm(self.session)
        if form.exec():
            self.load_employees()
            
    def open_report_form(self):
        """Открытие формы для генерации отчетов."""
        report_form = ReportForm(self.session)
        report_form.exec_()


    def generate_report(self):
        """Показ отчета по сотрудникам."""
        QMessageBox.information(self, "Отчет", "Эта функция еще в разработке.")

