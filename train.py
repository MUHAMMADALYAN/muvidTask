from model import Employee
from app import app
import pandas as pd
from sklearn.linear_model import LinearRegression
from joblib import dump
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from datetime import datetime
import pickle

with app.app_context():
    employees = Employee.query.all()
    # converting emp db data to dataframe
    df = pd.DataFrame([e.__dict__ for e in employees])
    # geting total number of days since hired
    df['hire_date'] = df['hire_date'].apply(lambda x: (datetime.now() - x).days)
    # one hot encoding of categorical data
    X = pd.get_dummies(df[['department', 'hire_date']])
    y = df['salary']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    model = LinearRegression().fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f'MSE on test set: {mse:.2f}')
    # saving model to be used in the app
    dump(model, 'model.joblib')
    # saving departments to be used for prediction
    training_departments = [c for c in X.columns if c != 'hire_date']
    print(training_departments)
    with open('training_departments.pkl', 'wb') as f:
        pickle.dump(training_departments, f)
