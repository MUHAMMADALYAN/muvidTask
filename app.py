from os import path
from joblib import load
from flask import Flask, jsonify, request
from model import db
from model import Employee
from datetime import datetime
import pickle
import pandas as pd

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employees.db'
# bounding our app with sqlAlchemy db object
db.init_app(app)
with app.app_context():
    db.create_all()

# GET all employees data
@app.route('/employees')
def get_employees():
    """
    Returns:
        list: A list containing dictionaries of employees.
    """
    employees = Employee.query.all()
    return jsonify([{'id': e.id, 'name': e.name, 'department': e.department, 'salary': e.salary,
                     'hire_date': e.hire_date.strftime('%Y-%m-%d %H:%M:%S')} for e in employees])


# GET employee data by ID
@app.route('/employees/<int:id>')
def get_employee(id):
    """
    Args:
        id (int): The unique ID of the employee to retrieve
    Returns:
        dict: A dictionary of employee data.
    """
    employee = Employee.query.get(id)
    if not employee:
        return jsonify({'error': 'Employee data not found'}), 404
    return jsonify({'id': employee.id, 'name': employee.name, 'department': employee.department,
                    'salary': employee.salary, 'hire_date': employee.hire_date.strftime('%Y-%m-%d %H:%M:%S')})


# CREATE new employee
@app.route('/employees', methods=['POST'])
def create_employee():
    """
    Request Body:
        JSON object with the following fields:
        - name (str): The name of the employee.
        - department (str): The department of the employee.
        - salary (float): The salary of the employee.
        - hire_date (str): The hire_date of the employee.

    Returns:
        dict: A id of created employee object.
    """
    data = request.get_json()
    name = data.get('name', '')
    department = data.get('department', '')
    salary = data.get('salary', 0.0)
    hire_date = data.get('hire_date', '')

    # Input fields validation
    if not name or len(name) > 50:
        return jsonify({'error': 'Invalid employee name'}), 400
    if not department or len(department) > 50:
        return jsonify({'error': 'Invalid department name'}), 400
    if salary < 0 or salary > 1000000:
        return jsonify({'error': 'Invalid salary amount'}), 400
    try:
        # converting string to datetime object
        hire_date = datetime.strptime(hire_date, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return jsonify({'error': 'Invalid hire_date, Follow format %Y-%m-%d %H:%M:%S'}), 400
    if hire_date < datetime(2020, 1, 1):
        return jsonify({'error': 'hire_date should be after 2020-01-01'}), 400
    if hire_date > datetime.now():
        return jsonify({'error': 'hire_date should be before today'}), 400

    employee = Employee(name=name, department=department, salary=salary, hire_date=hire_date)
    db.session.add(employee)
    db.session.commit()
    return jsonify({'id': employee.id}), 201


# UPDATE employee data by ID
@app.route('/employees/<int:id>', methods=['PUT'])
def update_employee(id):
    """
    Args:
        id (int): The unique ID of the employee to update
    Request Body:
        JSON object with the following fields:
        - name (str): The updated name of the employee.
        - department (str): The updated department of the employee.
        - salary (float): The updated salary of the employee.
        - hire_date (str): The updated hire_date of the employee.
    Returns:
        str: A message stating employee is updated.
    """

    employee = Employee.query.get(id)
    if not employee:
        return jsonify({'error': 'Employee data not found'}), 404
    data = request.get_json()
    name = data.get('name', '')
    department = data.get('department', '')
    salary = data.get('salary', 0.0)
    hire_date = data.get('hire_date', '')

    # Input fields validation
    if name and len(name) > 50:
        return jsonify({'error': 'Invalid employee name'}), 400
    if department and len(department) > 50:
        return jsonify({'error': 'Invalid department name'}), 400
    if salary and (salary < 0 or salary > 1000000):
        return jsonify({'error': 'Invalid salary amount'}), 400
    if hire_date:
        try:
            hire_date = datetime.strptime(hire_date, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return jsonify({'error': 'Invalid hire_date, Follow format %Y-%m-%d %H:%M:%S'}), 400
        if hire_date < datetime(2020, 1, 1):
            return jsonify({'error': 'hire_date should be after 2020-01-01'}), 400
        if hire_date > datetime.now():
            return jsonify({'error': 'hire_date should be before today'}), 400

    if name:
        employee.name = name
    if department:
        employee.department = department
    if salary:
        employee.salary = salary
    if hire_date:
        employee.hire_date = hire_date

    db.session.commit()
    return jsonify({'message': 'Employee data updated successfully'})


# DELETE employee data by ID
@app.route('/employees/<int:id>', methods=['DELETE'])
def delete_employee(id):
    """
    Args:
        id (int): The unique ID of the employee to delete
    Returns:
        str: A message stating employee is deleted.
    """
    employee = Employee.query.get(id)
    if not employee:
        return jsonify({'error': 'Employee data not found'}), 404
    db.session.delete(employee)
    db.session.commit()
    return jsonify({'message': 'Employee data deleted successfully'})


# GET all the unique departments of employees
@app.route('/departments')
def get_departments():
    """
    Returns:
        list: A list containing all unique departments.
    """
    departments = Employee.query.distinct(Employee.department).group_by(Employee.department).all()
    return jsonify([d.department for d in departments])


# GET all employees in a specific department
@app.route('/departments/<string:name>')
def get_department_employees(name):
    """
    Args:
        name (str): The name of the department whose employees data is needed
    Returns:
        list: A list containing dictionaries of employees of specific department.
    """
    employees = Employee.query.filter_by(department=name).all()
    if not employees:
        return jsonify({'error': 'No employees data found for given department'}), 404
    return jsonify([{'id': e.id, 'name': e.name, 'department': e.department, 'salary': e.salary,
                     'hire_date': e.hire_date.strftime('%Y-%m-%d %H:%M:%S')} for e in employees])


# GET average salary of employees in the specific department
@app.route('/average_salary/<string:department>')
def get_department_average_salary(department):
    """
    Args:
        name (str): The name of the department whose average salary has to be calculated.
    Returns:
        dict: A dictionary containing department and its average salary.
    """
    salaries = [e.salary for e in Employee.query.filter_by(department=department).all()]
    if not salaries:
        return jsonify({'error': 'No employees data found for this department'}), 404
    avg_salary = sum(salaries) / len(salaries)
    return jsonify({'department_name': department, 'average_salary': avg_salary})


# GET the top 10 earners of the company
@app.route('/top_earners')
def get_top_earners():
    """
    Returns:
        list: A list containing dictionaries of ten employees with maximum salary.
    """
    employees = Employee.query.order_by(Employee.salary.desc()).limit(10).all()
    return jsonify([{'name': e.name, 'department': e.department, 'salary': e.salary} for e in employees])


# GET 10 most recently hired employees
@app.route('/most_recent_hires')
def get_most_recent_hires():
    """
    Returns:
        list: A list containing dictionaries of employees that are recently hired.
    """
    employees = Employee.query.order_by(Employee.hire_date.desc()).limit(10).all()
    return jsonify([{'name': e.name, 'department': e.department, 'salary': e.salary,
                     'hire_date': e.hire_date.strftime('%Y-%m-%d %H:%M:%S')} for e in employees])


# salary prediction using trained model

if path.exists('model.joblib'):
    model = load('model.joblib')

# get the departments on which the model was trained
# do not use departments except these ones since the model is trained only on these departments
if path.exists('training_departments.pkl'):
    with open('training_departments.pkl', 'rb') as f:
        training_departments = pickle.load(f)
        print('Use the following training departments for prediction: ', [dep.replace("department_", "") for dep in training_departments])
else:
    training_departments = []


# Salary Prediction
@app.route('/predict_salary', methods=['POST'])
def predict_salary():
    """
    Request Body:
        JSON object with the following fields:
        - department (str): The name of department which are included in database.
        - hire_date (str): The hire_date of the employee.
    Returns:
        str: Salary of the employee.
    """
    data = request.get_json()
    # job title was not part of the employee database
    # so I have omited that
    department = data.get('department', '')
    hire_date = data.get('hire_date', '')

    if not department or len(department) > 50:
        return jsonify({'error': 'Invalid department'}), 400
    try:
        hire_date = datetime.strptime(hire_date, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return jsonify({'error': 'Invalid hire_date'}), 400
    if hire_date < datetime(2020, 1, 1):
        return jsonify({'error': 'hire_date must be after 2020-01-01'}), 400
    if hire_date > datetime.now():
        return jsonify({'error': 'hire_date must be before today'}), 400

    # preprocess the data to match with the training data
    # creating dataframe with column hire_date and assigning list of value
    X_new = pd.DataFrame({'hire_date': [(datetime.now() - hire_date).days]})
    # add other training columns
    for col in training_departments:
        X_new[col] = 0
    department_prv = 'department_' + department
    X_new[department_prv] = 1
    try:
        # Predict salary using the trained model
        salary_pred = model.predict(X_new)[0]
    except Exception as e:
        return jsonify({'error': True, 'message': "Department name is not present in the database"})

    return jsonify({'predicted_salary': round(salary_pred, 2)})


if __name__ == '__main__':
    app.run()

