from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# defining employee model

class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    department = db.Column(db.String(50))
    salary = db.Column(db.Float)
    hire_date = db.Column(db.DateTime)

    def __init__(self, name, department, salary, hire_date):
        self.name = name
        self.department = department
        self.salary = salary
        self.hire_date = hire_date
