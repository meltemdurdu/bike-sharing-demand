# Bike Sharing Demand Prediction Model

################################################################

# This script is part of the Kaggle "Bike Sharing Demand" competition.
# The goal is to predict the total count of bike rentals for a given hour based on historical usage patterns,
# weather conditions, and temporal information (e.g., time of day, day of the week).
# The script applies machine learning models such as Random Forest and Gradient Boosting to predict demand.
# It includes data preprocessing, feature engineering, model training with hyperparameter tuning,
# and blending of multiple models for better performance.

################################################################

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.metrics import make_scorer, mean_squared_log_error, mean_squared_error
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from xgboost import XGBRegressor
matplotlib.use('TkAgg')

# Load Data
train_path = "datasets/train_bike.csv"
test_path = "datasets/test_bike.csv"

train_df = pd.read_csv(train_path)
test_df = pd.read_csv(test_path)

train_df['data_set'] = 'train'
test_df['data_set'] = 'test'

test_df['registered'] = 0
test_df['casual'] = 0
test_df['count'] = 0

all_df = pd.concat([train_df, test_df])


train_df.info()
test_df.info()

train_df.describe().T

# Understand the distribution of numerical variables and generate a frequency table for numeric variables
def plot_histograms(dataframe):
    """
        Plots histograms for key numerical columns in the dataframe, such as season, weather, humidity, etc.

        Parameters:
        dataframe (pandas.DataFrame): The dataframe containing the data to plot.

        Returns:
        None: Displays the histograms using matplotlib.
        """
    plt.figure(figsize=(20, 15))

    plt.subplot(421)
    dataframe['season'].plot.hist(bins=10, color='blue', label='Histogram of Season', edgecolor='black')
    plt.legend(loc='best')

    plt.subplot(422)
    dataframe['weather'].plot.hist(bins=10, color='green', label='Histogram of Weather', edgecolor='black')
    plt.legend(loc='best')

    plt.subplot(423)
    dataframe['humidity'].plot.hist(bins=10, color='orange', label='Histogram of Humidity', edgecolor='black')
    plt.legend(loc='best')

    plt.subplot(424)
    dataframe['holiday'].plot.hist(bins=10, color='pink', label='Histogram of Holiday', edgecolor='black')
    plt.legend(loc='best')

    plt.subplot(425)
    dataframe['workingday'].plot.hist(bins=10, color='red', label='Histogram of Working Day', edgecolor='black')
    plt.legend(loc='best')

    plt.subplot(426)
    dataframe['temp'].plot.hist(bins=10, color='yellow', label='Histogram of Temperature', edgecolor='black')
    plt.legend(loc='best')

    plt.subplot(427)
    dataframe['atemp'].plot.hist(bins=10, color='cyan', label='Histogram of Feels Like Temp', edgecolor='black')
    plt.legend(loc='best')

    plt.subplot(428)
    dataframe['windspeed'].plot.hist(bins=10, color='purple', label='Histogram of Windspeed', edgecolor='black')
    plt.legend(loc='best')

    plt.tight_layout()
    plt.show()


plot_histograms(all_df)


all_df.isnull().sum() # check how many columns have null variables


# Feature Engineering

# This section performs various transformations to create additional features for the model.
# It includes extracting datetime features (hour, day, month, year), applying log transformations to
# stabilize variance, and handling missing values through interpolation.
# Additional features like weather categories, interaction terms, and rolling means are also created to
# capture important patterns for the model.

dt = pd.DatetimeIndex(all_df['datetime']) #set the column to a DateTime index object
all_df['datetime'] = dt # update datetime column with the object
all_df.set_index(dt, inplace=True) # set it as index

# Log transformation to stabilize variance
for col in ['casual', 'registered', 'count']:
    all_df['%s_log' % col] = np.log(all_df[col] + 1)

# Datetime feature extraction
all_df['hour'] = all_df.index.hour
all_df['day'] = all_df.index.day
all_df['month'] = all_df.index.month
all_df['year'] = all_df.index.year
all_df['dow'] = all_df.index.dayofweek

# Interpolation of missing values
all_df["weather"] = all_df["weather"].interpolate(method='time').apply(np.round)
all_df["temp"] = all_df["temp"].interpolate(method='time')
all_df["atemp"] = all_df["atemp"].interpolate(method='time')
all_df["humidity"] = all_df["humidity"].interpolate(method='time').apply(np.round)
all_df["windspeed"] = all_df["windspeed"].interpolate(method='time')

# Correlations
plt.figure(figsize=(20, 12))
heatmap = sns.heatmap(train_df.corr(), annot=True, annot_kws={"size": 12}, cmap='coolwarm', linewidths=.5)
heatmap.set_xticklabels(heatmap.get_xticklabels(), rotation=45, horizontalalignment='right')
heatmap.set_yticklabels(heatmap.get_yticklabels(), rotation=0)
plt.show()

plt.figure(figsize=(16,8))
sns.pairplot(train_df)

# Aggregation and custom features
by_season = all_df[all_df['data_set'] == 'train'].copy().groupby(['season'])[['count']].agg(sum)
by_season.columns = ['count_season']
all_df = all_df.join(by_season, on='season')

# Analyse target variable
def target_summary(dataframe, target, categorical_col):
    """
       Prints the mean target variable grouped by the specified categorical column.

       Parameters:
       dataframe (pandas.DataFrame): The dataframe containing the data.
       target (str): The target variable to summarize.
       categorical_col (str): The categorical column to group by.

       Returns:
       None: Prints the grouped target mean summary.
       """
    print(pd.DataFrame({"TARGET_MEAN": dataframe.groupby(categorical_col)[target].mean()}), end="\n\n\n")
for col in train_df.columns:
    target_summary(train_df,"count",col)
train_df["count"].hist(bins=100)
plt.show() # Histogram ("count" is divided to 100 equal parts)
# Positively(right) skewed data

by_hour = all_df[all_df['data_set'] == 'train'].copy().groupby(['hour', 'workingday'])['count'].agg('sum').unstack()
by_hour.head(10)
# rentals by hour, split by working day (or not)
by_hour.plot(kind='bar', figsize=(15,5), width=0.8);
plt.grid(True)
plt.tight_layout()

train_df = all_df[all_df['data_set'] == 'train'].copy()
#train_df.boxplot(column='count', by='hour', figsize=(15,5))
#plt.ylabel('Count of Users')
#plt.title("Boxplot of Count grouped by hour")
#plt.suptitle("") # get rid of the pandas autogenerated title

fig, ax = plt.subplots(figsize=(18, 5))
sns.boxplot(x=train_df['hour'], y=train_df['count'], ax=ax)
ax.set_ylabel('Count of Users')
ax.set_title("Boxplot of Count grouped by hour");
plt.suptitle("") # get rid of the pandas autogenerated title

season_map = {1:'Spring', 2:'Summer', 3:'Fall', 4:'Winter'}
good_weather = all_df[all_df['weather'] == 1][['hour', 'season']].copy()
data = pd.DataFrame({'count' : good_weather.groupby(["hour","season"]).size()}).reset_index()
data['season'] = data['season'].map(lambda d : season_map[d])

fig, ax = plt.subplots(figsize=(18, 5))
sns.pointplot(x=data["hour"], y=data["count"], hue=data["season"], ax=ax)
ax.set(xlabel='Hour Of The Day', ylabel='Good Weather Count', title="Good Weather By Hour Of The Day Across Season")

fig, ax = plt.subplots(figsize=(12, 5))
data.plot.area(stacked=False, ax=ax)
ax.set(xlabel='Hour Of The Day', ylabel='Normal Weather Count', title="Normal Weather By Hour Of The Day Across Season")

weather_map = {1:'Good', 2:'Normal', 3:'Bad', 4:'Worse'}
data = pd.DataFrame(train_df.groupby(["hour","weather"], sort=True)["count"].mean()).reset_index()
data['weather'] = data['weather'].map(lambda d : weather_map[d])
fig, ax = plt.subplots(figsize=(18, 5))
sns.pointplot(x=data["hour"], y=data["count"], hue=data["weather"], ax=ax)
ax.set(xlabel='Hour Of The Day', ylabel='Users Count', title="Average Users Count By Hour Of The Day Across Weather")

season_map = {1:'Spring', 2:'Summer', 3:'Fall', 4:'Winter'}
data = pd.DataFrame({'mean':train_df.groupby(["hour","season"], sort=True)["count"].mean()}).reset_index()
data['season'] = data['season'].map(lambda d : season_map[d])
fig, ax = plt.subplots(figsize=(18, 5))
sns.pointplot(x=data["hour"], y=data["mean"], hue=data["season"], ax=ax)
ax.set(xlabel='Hour Of The Day', ylabel='Users Count', title="Average Users Count By Hour Of The Day Across Season")

day_map = {0:'Monday', 1:'Tuesday', 2:'Wednesday', 3:'Thursday', 4:'Friday', 5:'Saturday', 6:'Sunday'}
hueOrder = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
data = pd.DataFrame({'mean':train_df.groupby(["hour","dow"], sort=True)["count"].mean()}).reset_index()
data['dow'] = data['dow'].map(lambda d : day_map[d])
fig, ax = plt.subplots(figsize=(18, 5))
sns.pointplot(x=data["hour"], y=data["mean"], hue=data["dow"], hue_order=hueOrder, ax=ax)
ax.set(xlabel='Hour Of The Day', ylabel='Users Count', title="Average Users Count By Hour Of The Day Across Weekdays")

# Registered and casual user rent difference
fig, axs = plt.subplots(1, 2, figsize=(18,5), sharex=False, sharey=False)

sns.boxplot(x='hour', y='casual', data=train_df, ax=axs[0])
axs[0].set_ylabel('casual users')
axs[0].set_title('')

sns.boxplot(x='hour', y='registered', data=train_df, ax=axs[1])
axs[1].set_ylabel('registered users')
axs[1].set_title('')

fig, ax = plt.subplots(figsize=(18, 5))
train_df_melt = pd.melt(train_df[["hour","casual","registered"]], id_vars=['hour'], value_vars=['casual', 'registered'], var_name='usertype', value_name='count')
data = pd.DataFrame(train_df_melt.groupby(["hour", "usertype"], sort=True)["count"].mean()).reset_index()
sns.pointplot(x=data["hour"], y=data["count"], hue=data["usertype"], hue_order=["casual","registered"], ax=ax)
ax.set(xlabel='Hour Of The Day', ylabel='Users Count', title='Average Users Count By Hour Of The Day Across User Type')

import matplotlib.colors as mcolors

# Function to add jitter to the hour value
def hour_jitter(hour):
    return hour + np.random.uniform(-0.4, 0.4)

# Function to format the hour value as a string
def hour_format(hour):
    return f"{hour:02d}:00 AM" if hour <= 12 else f"{hour % 12:02d}:00 PM"

# Set up a color map for the scatter plot
color_map = mcolors.ListedColormap([
    "#5e4fa2", "#3288bd", "#66c2a5", "#abdda4",
    "#e6f598", "#fee08b", "#fdae61", "#f46d43",
    "#d53e4f", "#9e0142"
])

# Apply jitter to the 'hour' column
train_df['hour_jitter'] = train_df['hour'].map(hour_jitter)

# Create a scatter plot for working days with temperature as the color
train_df[train_df['workingday'] == 1].plot(
    kind="scatter",
    x='hour_jitter',
    y='count',
    figsize=(18, 6),
    c='temp',
    cmap=color_map,
    colorbar=True,
    sharex=False
)

# Format the x-axis labels to show the hours
hours = np.unique(train_df['hour'])
hour_labels = [hour_format(h) for h in hours]
plt.xticks(hours, hour_labels, rotation='vertical')

plt.show()
train_df.drop('hour_jitter', axis=1, inplace=True)

# Daily trend
dayOfWeek={0:'Monday', 1:'Tuesday', 2:'Wednesday', 3:'Thursday', 4:'Friday', 5:'Saturday', 6:'Sunday'}
all_df['weekday'] = all_df['dow'].map(dayOfWeek)

fig, axs = plt.subplots(1, 2, figsize=(15,5), sharex=False, sharey=False)

sns.boxplot(x='weekday', y='registered', data=all_df, ax=axs[0])
axs[0].set_ylabel('registered users')
axs[0].set_title('')

sns.boxplot(x='weekday', y='casual', data=all_df, ax=axs[1])
axs[1].set_ylabel('casual users')
axs[1].set_title('')

all_df.drop('weekday', axis=1, inplace=True)

# Weather boxplot
fig, axs = plt.subplots(1, 2, figsize=(15,5), sharex=False, sharey=False)

sns.boxplot(x='weather', y='registered', data=all_df, ax=axs[0])
axs[0].set_ylabel('registered users')
axs[0].set_title('')

sns.boxplot(x='weather', y='casual', data=all_df, ax=axs[1])
axs[1].set_ylabel('casual users')
axs[1].set_title('')


# Compare the distribution of train and test data
# Compare seasons
season_map = {1:'Spring', 2:'Summer', 3:'Fall', 4:'Winter'}
data = all_df[['data_set', 'season']].copy()
data['season'] = data['season'].map(lambda d : season_map[d])
sns.countplot(x="data_set", hue="season", data=data)
# compare by year
plt.figure(figsize=(8, 5))
sns.boxplot(x='year', y='count', data=train_df)
plt.ylabel('Count of Users')
plt.title("Boxplot of Count grouped by year")

# Feature Engineering
def get_day(day_start):
    """
       Generates a range of hourly timestamps for a specific day, starting from the provided day.

       Parameters:
       day_start (pandas.Timestamp or datetime-like): The start date of the day to generate timestamps for.

       Returns:
       pandas.DatetimeIndex: A range of hourly timestamps for the specified day.
       """
    day_end = day_start + pd.offsets.DateOffset(hours=23)
    return pd.date_range(day_start, day_end, freq="H")

# Define special days
all_df.loc[get_day(pd.datetime(2011, 4, 15)), "workingday"] = 1 #tax day
all_df.loc[get_day(pd.datetime(2012, 4, 16)), "workingday"] = 1
all_df.loc[get_day(pd.datetime(2011, 11, 25)), "workingday"] = 0
all_df.loc[get_day(pd.datetime(2012, 11, 23)), "workingday"] = 0
all_df.loc[get_day(pd.datetime(2011, 4, 15)), "holiday"] = 0
all_df.loc[get_day(pd.datetime(2012, 4, 16)), "holiday"] = 0
all_df.loc[get_day(pd.datetime(2011, 11, 25)), "holiday"] = 1
all_df.loc[get_day(pd.datetime(2012, 11, 23)), "holiday"] = 1
all_df.loc[get_day(pd.datetime(2012, 5, 21)), "holiday"] = 1
all_df.loc[get_day(pd.datetime(2012, 6, 1)), "holiday"] = 1

# Custom Features:
# Additional features such as 'is_weekend', 'temp_category', 'humidity_category', etc., are created to better
# capture relationships in the data. These features help the model distinguish between weekdays and weekends,
# temperature ranges, and interaction effects between temperature and humidity.

all_df['is_weekend'] = all_df['dow'].apply(lambda x: 1 if x >= 5 else 0)
all_df['temp_category'] = all_df['temp'].apply(lambda x: 'low' if x < 10 else ('medium' if 10 <= x < 20 else 'high'))
all_df['humidity_category'] = all_df['humidity'].apply(lambda x: 'low' if x < 30 else ('medium' if 30 <= x < 70 else 'high'))
all_df['windspeed_category'] = all_df['windspeed'].apply(lambda x: 'low' if x < 10 else ('medium' if 10 <= x < 20 else 'high'))
all_df['hour_category'] = all_df['hour'].apply(lambda x: 'night' if 0 <= x < 6 else ('morning' if 6 <= x < 12 else ('afternoon' if 12 <= x < 18 else 'evening')))
all_df['temp_humidity_interaction'] = all_df['temp'] * all_df['humidity']
all_df['holiday_weekday_interaction'] = all_df['holiday'] * all_df['workingday']
all_df['rolling_mean_temp'] = all_df['temp'].rolling(window=3).mean().fillna(all_df['temp'].mean())
all_df['busy_hour'] = all_df[['hour', 'workingday']].apply(lambda df: 1 if (
            (df['workingday'] == 1 and (df['hour'] == 8 or 17 <= df['hour'] <= 18)) or (
                df['workingday'] == 0 and 10 <= df['workingday'] <= 19)) else 0, axis=1)
all_df['ideal'] = all_df[['temp', 'windspeed']].apply(lambda df: 1 if (df['temp'] > 27 and df['windspeed'] < 30) else 0,
                                                      axis=1)
all_df['sticky'] = all_df[['humidity', 'workingday']].apply(
    lambda df: 1 if (df['workingday'] == 1 and df['humidity'] >= 60) else 0, axis=1)

# Split Data Back:
# After feature engineering, the dataset is split back into the original training and test sets.
# The 'train_df' and 'test_df' dataframes are used in the model training process.

train_df = all_df[all_df['data_set'] == 'train']
test_df = all_df[all_df['data_set'] == 'test']


# Helper functions
def get_rmsle(y_pred, y_actual):
    """
        Calculates the Root Mean Squared Logarithmic Error (RMSLE) between predicted and actual values.

        Parameters:
        y_pred (array-like): Predicted values.
        y_actual (array-like): Actual values.

        Returns:
        float: The calculated RMSLE score.
        """
    diff = np.log(y_pred + 1) - np.log(y_actual + 1)
    mean_error = np.square(diff).mean()
    return np.sqrt(mean_error)


def custom_train_valid_split(data, cutoff_day=15):
    """
        Splits the data into training and validation sets based on a specific day cutoff.

        Parameters:
        data (pandas.DataFrame): The dataframe containing the data.
        cutoff_day (int): The day of the month to split the data.

        Returns:
        tuple: Two dataframes (train, valid) corresponding to the training and validation sets.
        """
    train = data[data['day'] <= cutoff_day]
    valid = data[data['day'] > cutoff_day]
    return train, valid


def prep_train_data(data, input_cols):
    """
        Prepares the input data for training by separating the feature columns and target variables (registered, casual).

        Parameters:
        data (pandas.DataFrame): The dataframe containing the data.
        input_cols (list): The list of columns to use as input features.

        Returns:
        tuple: Arrays containing the feature matrix and the two target arrays (registered_log and casual_log).
        """
    X = data[input_cols].values
    y_r = data['registered_log'].values
    y_c = data['casual_log'].values
    return X, y_r, y_c


def predict_on_validation_set(model, input_cols):
    """
        Predicts on the validation set using the provided model and input columns, then calculates the RMSLE.

        Parameters:
        model (object): The trained model to use for prediction.
        input_cols (list): The list of columns to use as input features.

        Returns:
        float: The RMSLE score for the validation set predictions.
        """
    train, valid = custom_train_valid_split(train_df)
    X_train, y_train_r, y_train_c = prep_train_data(train, input_cols)
    X_valid, y_valid_r, y_valid_c = prep_train_data(valid, input_cols)

    model_r = model.fit(X_train, y_train_r)
    y_pred_r = np.exp(model_r.predict(X_valid)) - 1

    model_c = model.fit(X_train, y_train_c)
    y_pred_c = np.exp(model_c.predict(X_valid)) - 1

    y_pred_comb = np.round(y_pred_r + y_pred_c)
    y_pred_comb[y_pred_comb < 0] = 0

    y_actual_comb = np.exp(y_valid_r) + np.exp(y_valid_c) - 2

    rmsle = get_rmsle(y_pred_comb, y_actual_comb)
    return rmsle


# Define hyperparameter grids
rf_param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [10, 15, 20],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'bootstrap': [True, False]
}

gbm_param_grid = {
    'n_estimators': [100, 150, 200],
    'max_depth': [3, 4, 5],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'learning_rate': [0.01, 0.05, 0.1],
    'subsample': [0.8, 1.0]
}

# Define models
rf_model = RandomForestRegressor(random_state=42)
gbm_model = GradientBoostingRegressor(random_state=42)

# Perform RandomizedSearchCV for hyperparameter tuning
rf_random_search = RandomizedSearchCV(estimator=rf_model,
                                      param_distributions=rf_param_grid,
                                      n_iter=20,
                                      scoring='neg_mean_squared_log_error',
                                      cv=3,
                                      verbose=2,
                                      random_state=42,
                                      n_jobs=-1)

gbm_random_search = RandomizedSearchCV(estimator=gbm_model,
                                       param_distributions=gbm_param_grid,
                                       n_iter=20,
                                       scoring='neg_mean_squared_log_error',
                                       cv=3,
                                       verbose=2,
                                       random_state=42,
                                       n_jobs=-1)

# Define feature columns
rf_cols = [
    'weather', 'temp', 'atemp', 'windspeed',
    'workingday', 'season', 'holiday', 'sticky',
    'hour', 'dow', 'busy_hour'
]

gbm_cols = [
    'weather', 'temp', 'atemp', 'humidity','windspeed',
    'holiday', 'workingday', 'season',
    'hour', 'dow', 'year', 'ideal', 'count_season'
]

# Split data into training and validation sets
X_rf = train_df[rf_cols]
y_rf = train_df['count_log']
X_gbm = train_df[gbm_cols]
y_gbm = train_df['count_log']

X_train_rf, X_valid_rf, y_train_rf, y_valid_rf = train_test_split(X_rf, y_rf, test_size=0.2, random_state=42)
X_train_gbm, X_valid_gbm, y_train_gbm, y_valid_gbm = train_test_split(X_gbm, y_gbm, test_size=0.2, random_state=42)

# Fit the random search models
rf_random_search.fit(X_train_rf, y_train_rf)
gbm_random_search.fit(X_train_gbm, y_train_gbm)

print("Best parameters for RandomForest: ", rf_random_search.best_params_)
print("Best parameters for GradientBoosting: ", gbm_random_search.best_params_)


# Get the best models from the random search
best_rf_model = rf_random_search.best_estimator_
best_gbm_model = gbm_random_search.best_estimator_

# Feature importance for RandomForest
rf_importances = best_rf_model.feature_importances_
rf_importance_df = pd.DataFrame({'feature': rf_cols, 'importance': rf_importances}).sort_values(by='importance',
                                                                                                ascending=False)

plt.figure(figsize=(12, 8))
sns.barplot(x='importance', y='feature', data=rf_importance_df)
plt.title('Random Forest Feature Importance')
plt.show()

# Feature importance for GradientBoosting
gbm_importances = best_gbm_model.feature_importances_
gbm_importance_df = pd.DataFrame({'feature': gbm_cols, 'importance': gbm_importances}).sort_values(by='importance',
                                                                                                   ascending=False)

plt.figure(figsize=(12, 8))
sns.barplot(x='importance', y='feature', data=gbm_importance_df)
plt.title('Gradient Boosting Feature Importance')
plt.show()


"""
Blending Models:
This section combines the predictions from multiple models (Random Forest and Gradient Boosting) 
by blending their outputs. We train each model to predict the 'registered' and 'casual' users, 
sum their predictions to get the total 'count', and apply this to both training and test datasets.
"""
clf_input_cols = [rf_cols, gbm_cols]
clfs = [best_rf_model, best_gbm_model]

blend_train = np.zeros((train_df.shape[0], len(clfs)))
blend_test = np.zeros((test_df.shape[0], len(clfs)))

for clf_index, (input_cols, clf) in enumerate(zip(clf_input_cols, clfs)):
    # Prepare the training and test data for blending
    X_train, y_train_r, y_train_c = prep_train_data(train_df, input_cols)
    X_test = test_df[input_cols].values

    # Predict for both registered and casual users, blend the predictions
    model_r = clf.fit(X_train, y_train_r)
    y_pred_train_r = np.exp(model_r.predict(X_train)) - 1
    y_pred_test_r = np.exp(model_r.predict(X_test)) - 1

    model_c = clf.fit(X_train, y_train_c)
    y_pred_train_c = np.exp(model_c.predict(X_train)) - 1
    y_pred_test_c = np.exp(model_c.predict(X_test)) - 1

    # Combine predictions and ensure non-negative predictions
    y_pred_train_comb = np.round(y_pred_train_r + y_pred_train_c)
    y_pred_train_comb[y_pred_train_comb < 0] = 0

    y_pred_test_comb = np.round(y_pred_test_r + y_pred_test_c)
    y_pred_test_comb[y_pred_test_comb < 0] = 0

    # Store the blended predictions
    blend_train[:, clf_index] = y_pred_train_comb
    blend_test[:, clf_index] = y_pred_test_comb

# Final blending model
bclf = LinearRegression(fit_intercept=False)
bclf.fit(blend_train, train_df['count'])

# Final prediction
y_pred_blend = np.round(bclf.predict(blend_test)).astype(int)

# Prepare submission
submit_stack_blend_df = test_df[['datetime', 'count']].copy()
submit_stack_blend_df['count'] = y_pred_blend

submit_stack_blend_df.to_csv('submission.csv', index=False)

# Calculate RMSLE for RandomForest
rf_rmsle = predict_on_validation_set(best_rf_model, rf_cols)
print(f"RMSLE Score for RandomForest: {rf_rmsle}")

# Calculate RMSLE for GradientBoosting
gbm_rmsle = predict_on_validation_set(best_gbm_model, gbm_cols)
print(f"RMSLE Score for GradientBoosting: {gbm_rmsle}")


# Model Performances Comparison
performance_data = {
    'Model': ['Random Forest', 'Gradient Boosting'],
    'RMSLE': [rf_rmsle, gbm_rmsle]
}
performance_df = pd.DataFrame(performance_data)

plt.figure(figsize=(10, 6))
sns.barplot(x='Model', y='RMSLE', data=performance_df)
plt.title('Model Performances Comparison')
plt.ylabel('RMSLE Score')
plt.savefig('model_performance_comparison.png')
plt.show()

# Calculate RMSLE for Blended Model
train, valid = custom_train_valid_split(train_df)
blend_valid = np.zeros((valid.shape[0], len(clfs)))

for clf_index, (input_cols, clf) in enumerate(zip(clf_input_cols, clfs)):
    X_train, y_train_r, y_train_c = prep_train_data(train_df, input_cols)
    X_valid, y_valid_r, y_valid_c = prep_train_data(valid, input_cols)

    model_r = clf.fit(X_train, y_train_r)
    y_pred_valid_r = np.exp(model_r.predict(X_valid)) - 1

    model_c = clf.fit(X_train, y_train_c)
    y_pred_valid_c = np.exp(model_c.predict(X_valid)) - 1

    y_pred_valid_comb = np.round(y_pred_valid_r + y_pred_valid_c)
    y_pred_valid_comb[y_pred_valid_comb < 0] = 0

    blend_valid[:, clf_index] = y_pred_valid_comb

y_pred_blend_valid = np.round(bclf.predict(blend_valid)).astype(int)
y_actual_valid_comb = np.exp(y_valid_r) + np.exp(y_valid_c) - 2

blend_rmsle = get_rmsle(y_pred_blend_valid, y_actual_valid_comb)
print(f"RMSLE Score for Blended Model: {blend_rmsle}")

#Best parameters for RandomForest:  {'n_estimators': 100, 'min_samples_split': 5, 'min_samples_leaf': 2, 'max_depth': 20, 'bootstrap': True}
#Best parameters for GradientBoosting:  {'subsample': 0.8, 'n_estimators': 200, 'min_samples_split': 10, 'min_samples_leaf': 1, 'max_depth': 5, 'learning_rate': 0.1}
#RMSLE Score for RandomForest: 0.4408788410629949
#RMSLE Score for GradientBoosting: 0.319124145464365
#RMSLE Score for Blended Model: 0.2138674283325667
#Kaggle score: 0.37205