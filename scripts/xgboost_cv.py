import sys
import numpy as np
import pandas as pd

sys.path.append('..')
from utils.preprocessing import one_hot_encoding
from utils.data_loading import load_users_data
from sklearn.preprocessing import LabelEncoder


print 'START'

print 'Loading data...',

train_users, test_users = load_users_data()
labels = train_users['country_destination'].values
train_users = train_users.drop(['country_destination'], axis=1)

print '\tDONE'

print 'Preprocessing...',

id_test = test_users['id']
piv_train = train_users.shape[0]
users = pd.concat((train_users, test_users), axis=0, ignore_index=True)
users = users.drop(['id', 'date_first_booking'], axis=1)

# Fill NaN values
users = users.fillna(-1)

users['date_account_created'] = pd.to_datetime(users['date_account_created'])
users['year_account_created'] = pd.DatetimeIndex(users['date_account_created']).year
users['month_account_created'] = pd.DatetimeIndex(users['date_account_created']).month
users['day_account_created'] = pd.DatetimeIndex(users['date_account_created']).day
users = users.drop(['date_account_created'], axis=1)
users['timestamp_first_active'] = pd.to_datetime(users['timestamp_first_active'], format='%Y%m%d%H%M%S')
users['year_first_active'] = pd.DatetimeIndex(users['timestamp_first_active']).year
users['month_first_active'] = pd.DatetimeIndex(users['timestamp_first_active']).month
users['day_first_active'] = pd.DatetimeIndex(users['timestamp_first_active']).day
users = users.drop(['timestamp_first_active'], axis=1)
age_values = users.age.values
users['age'] = np.where(np.logical_or(age_values < 14, age_values > 100), -1, age_values)

categorical_features = [
    'gender', 'signup_method', 'signup_flow', 'language', 'affiliate_channel',
    'affiliate_provider', 'first_affiliate_tracked', 'signup_app',
    'first_device_type', 'first_browser'
]

users = one_hot_encoding(users, categorical_features)

# Splitting train and test
values = users.values
X = values[:piv_train]
le = LabelEncoder()
y = le.fit_transform(labels)
X_test = values[piv_train:]
print '\tDONE'


from xgboost.sklearn import XGBClassifier
# Classifier
xgb = XGBClassifier(
    max_depth=8,
    learning_rate=0.2,
    n_estimators=50,
    objective="multi:softprob",
    nthread=-1,
    gamma=0,
    min_child_weight=1,
    max_delta_step=0,
    subsample=0.6,
    colsample_bytree=0.6,
    colsample_bylevel=1,
    reg_alpha=0,
    reg_lambda=1,
    scale_pos_weight=1,
    base_score=0.5,
    seed=42
)

import xgboost
# xgb.fit(X, y)
# dtrain = xgboost.DMatrix(X, label=y)
#
# param = {
    # 'max_depth':[4],
    # 'n_estimators':[1000, 100, 200],
    # 'silent':1, 'objective':'multi:softprob',
    # 'num_class':8,
    # 'learning_rates':[0.2,0.3,0.1,0.4]
         # }
# num_round = 30
#
# print xgboost.cv(param, dtrain, num_round, nfold=5, metrics={'mlogloss'})


from sklearn.grid_search import GridSearchCV

xgb_model = xgboost.XGBClassifier(nthread=-1, max_depth=1)

clf = GridSearchCV(
    xgb_model,
    {
        'n_estimators': [1,2,3,4]
    },
    cv=2,
    verbose=1,
    n_jobs=-1,
    scoring='log_loss'
    )

clf.fit(X,y)

print(clf.best_score_)
print(clf.best_params_)