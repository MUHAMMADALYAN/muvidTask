from faker import Faker
from model import db, Employee
import random
from app import app
from datetime import datetime

fake = Faker()

# assumption: total departments are 10
departments = []
for _ in range(10):
    departments.append(fake.job())


starting_date = datetime(2020, 1, 1, 0, 0, 0)
ending_date = datetime.today()
with app.app_context():
    counter = 0
    while True:
        # creating name of employee
        name = fake.name()
        department = random.choice(departments)
        salary = random.uniform(0, 1000000)
        if len(name) > 50 or len(department) > 50:
            continue
        hiring_date = fake.date_between_dates(starting_date, ending_date)
        # saving data
        employee = Employee(name=name, department=department, salary=salary, hire_date=hiring_date)
        db.session.add(employee)
        counter += 1
        if counter >= 10000:
            break
    db.session.commit()



