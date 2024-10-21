# -*- coding: utf-8 -*-
"""Untitled6.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1jzFu-HeLh56Im7W0NmH_Ex612y8G6BSL
"""

# Importing necessary libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import r2_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import SelectKBest, f_regression

# Function for data visualization
def visualize_data(df):
    plt.figure(figsize=(12, 6))

    # Auto-detect the revenue column based on common patterns in column names
    revenue_column = None
    for col in df.columns:
        if "revenue" in col.lower() or "income" in col.lower():
            revenue_column = col
            break

    # If no revenue column is found, prompt the user
    if revenue_column is None:
        print("No 'revenue' or 'income' column found in the dataset.")
        return

    # Auto-detect the date column based on common patterns
    date_column = None
    for col in df.columns:
        if "date" in col.lower():
            date_column = col
            break

    # Show detected columns to the user
    print(f"Detected Revenue Column: {revenue_column}")

    # Visualization 1: Revenue Over Time
    if date_column:
        # Convert 'Date' to datetime format and handle any parsing errors
        df[date_column] = pd.to_datetime(df[date_column], errors='coerce')

        # Remove rows with invalid or missing dates
        df = df.dropna(subset=[date_column])

        # Sort data by 'Date' for proper plotting
        df = df.sort_values(by=date_column)

        # Group by date to sum the revenue column
        revenue_over_time = df.groupby(date_column)[revenue_column].sum().reset_index()

        # Plot if there are valid dates
        if not revenue_over_time.empty:
            plt.subplot(1, 2, 1)
            sns.lineplot(data=revenue_over_time, x=date_column, y=revenue_column)
            plt.title(f'Revenue Over Time ({revenue_column})')
            plt.xlabel(date_column.capitalize())
            plt.ylabel(revenue_column.capitalize())
        else:
            print("No valid dates to plot 'Revenue Over Time'.")

    # Visualization 2: Profit/Loss Comparison (Optional, if columns exist)
    if 'Profit' in df.columns and 'Loss' in df.columns:
        plt.subplot(1, 2, 2)
        profit_loss_data = df[['Profit', 'Loss']].sum().reset_index()
        sns.barplot(data=profit_loss_data, x='index', y=0)
        plt.title('Total Profit and Loss')
        plt.xlabel('Categories')
        plt.ylabel('Amount')
        plt.xticks(ticks=[0, 1], labels=['Profit', 'Loss'])

    plt.tight_layout()
    plt.show()

# Function to automate model selection and return the best model pipeline
def automated_regression_analysis_best_model(data_path, test_size=0.2, k_best_features=5):
    # Load the dataset
    df = pd.read_csv(data_path)

    # Auto-detect the target column based on numeric types
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
    target_column = numeric_columns[-1]  # Automatically pick the last numeric column as target (can be modified)

    # Visualize the data before modeling
    visualize_data(df)

    # Separate features and target
    X = df.drop(target_column, axis=1)  # All columns except the target
    y = df[target_column]  # The target column (to predict)

    # Automatically detect categorical columns
    categorical_cols = X.select_dtypes(include=['object']).columns

    # Automatically detect numerical columns
    numerical_cols = X.select_dtypes(include=['float64', 'int64']).columns

    print(f"Columns used for prediction: {list(X.columns)}")

    # Define preprocessing for numerical data
    numerical_transformer = StandardScaler()

    # Define preprocessing for categorical data
    categorical_transformer = OneHotEncoder(handle_unknown='ignore')

    # Bundle preprocessing for numerical and categorical data
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numerical_transformer, numerical_cols),
            ('cat', categorical_transformer, categorical_cols)
        ])

    # Feature selection: Select K Best features based on regression scores
    feature_selector = SelectKBest(score_func=f_regression, k=k_best_features)

    # Define the models to evaluate
    models = {
        'Linear Regression': LinearRegression(),
        'Ridge Regression': Ridge(),
        'Decision Tree': DecisionTreeRegressor(),
        'Random Forest': RandomForestRegressor(),
        'Gradient Boosting': GradientBoostingRegressor()
    }

    best_model_name = None
    best_model_score = float('-inf')  # Start with negative infinity for R2 comparison
    best_model = None

    # Evaluate each model
    for model_name, model in models.items():
        # Create the pipeline with preprocessing, feature selection, and the model
        pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('feature_selection', feature_selector),
            ('model', model)
        ])

        # Split data into train and test sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

        # Fit the model on the training set
        pipeline.fit(X_train, y_train)

        # Make predictions on the test set
        y_pred = pipeline.predict(X_test)

        # Evaluate the model using R-squared
        r2 = r2_score(y_test, y_pred)

        # Check if this model is better
        if r2 > best_model_score:
            best_model_score = r2
            best_model_name = model_name
            best_model = pipeline

    # Output the best model and its score
    print(f"Best Model: {best_model_name} with R-squared Score: {best_model_score}")

    # Return the best model pipeline for future predictions
    return best_model, df

# Function to take user input for new data and make predictions
def predict_with_best_model(best_model_pipeline, df):
    print("\nProvide input for the following columns:")

    # Drop the target column to get the feature column names
    target_column = df.select_dtypes(include=['float64', 'int64']).columns[-1]
    column_names = df.drop(target_column, axis=1).columns

    # Capture user input
    user_input = {}
    for column in column_names:
        value = input(f"Enter value for {column}: ")

        # Try to cast the input to float or leave as string for categorical values
        try:
            user_input[column] = float(value)
        except ValueError:
            user_input[column] = value

    # Convert input into a DataFrame for prediction
    input_df = pd.DataFrame([user_input])

    # Make prediction using the best model
    prediction = best_model_pipeline.predict(input_df)
    print(f"\nPredicted output: {prediction[0]}")

# Example usage
data_path = '/content/archive (16).zip'  # Provide your dataset path

# Run the automated regression analysis and get the best model
best_model_pipeline, df = automated_regression_analysis_best_model(data_path, test_size=0.2, k_best_features=5)

# Predict with user input after showing the revenue plot
predict_with_best_model(best_model_pipeline, df)