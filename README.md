# Bike Sharing Demand Prediction

This project is part of the [Kaggle Bike Sharing Demand Competition](https://www.kaggle.com/c/bike-sharing-demand), which aims to predict the total number of bike rentals for a given hour based on historical usage patterns, weather conditions, and temporal information.

## Table of Contents

- [Project Overview](#project-overview)
- [Technologies and Libraries Used](#technologies-and-libraries-used)
- [Dataset](#dataset)
- [Feature Engineering](#feature-engineering)
- [Modeling Approach](#modeling-approach)
- [Results](#results)
- [Project Structure](#project-structure)
- [How to Run](#how-to-run)

## Project Overview

In this project, machine learning models are built to predict bike-sharing demand. The goal is to forecast the number of bikes rented at a given time using features such as weather conditions, date-time information, and more. The model is evaluated using the Root Mean Squared Logarithmic Error (RMSLE).

The competition dataset consists of hourly rental data spanning two years, including features like weather, holiday, working day, and more.

## Technologies and Libraries Used:

- Python 3.x
- Pandas: Data manipulation
- NumPy: Numerical computing
- Seaborn & Matplotlib: Data visualization
- Scikit-learn: Machine learning algorithms (RandomForest, GradientBoosting)
- Jupyter Notebook: Development environment (optional)

## Dataset:

The dataset used for this project is available from the [Kaggle Bike Sharing Demand Competition](https://www.kaggle.com/c/bike-sharing-demand/data).

After downloading the data, place the `train.csv` and `test.csv` files in the `datasets` directory as follows:

datasets/ ├── train_bike.csv └── test_bike.csv

## Feature Engineering

Key feature engineering steps include:

- **Datetime features**: Extracting hour, day, month, year, and day of the week from the datetime column.
- **Log transformation**: Applied to stabilize the variance in the target variable (`count`).
- **Rolling averages**: Created a rolling mean for the temperature to smooth out short-term fluctuations.
- **Custom features**: New features like `is_weekend`, weather categories, interaction terms between temperature and humidity, etc.
- **Missing value handling**: Missing values were interpolated for weather-related columns.

## Modeling Approach

The following models were used in this project:

1. **Random Forest**: A robust ensemble method for regression.
2. **Gradient Boosting**: Another ensemble method, with hyperparameter tuning using RandomizedSearchCV.
3. **Blending**: A final ensemble approach where we blended the predictions from Random Forest and Gradient Boosting models for better results.

### Hyperparameter Tuning:
We used **RandomizedSearchCV** to tune hyperparameters for both Random Forest and Gradient Boosting models, optimizing for the lowest RMSLE.

## Results

The final blended model achieved the following performance:

- **RMSLE for Random Forest**: 0.4408
- **RMSLE for Gradient Boosting**: 0.3191
- **RMSLE for Blended Model**: 0.2139
- **Kaggle Public Score**: 0.37205

## Project Structure

├── datasets/ │ ├── train_bike.csv │ └── test_bike.csv ├── BIKE_SHARING_DEMAND.py # Python script for the full model pipeline ├── README.md # This file └── submission.csv # Final submission file

## How to Run

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/bike-sharing-demand.git
   cd bike-sharing-demand
2. Install the required libraries:
pip install -r requirements.txt

3. Download the dataset from Kaggle:

Download the dataset from the Kaggle Bike Sharing Demand page.
Place the train_bike.csv and test_bike.csv files inside the datasets/ directory.

4. Run the Python script:

python BIKE_SHARING_DEMAND.py

5. Check the output: The script will output the predictions in submission.csv.

