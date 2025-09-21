import argparse, joblib, numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
from transformer import load_last_30_hours, add_features
def persistence_baseline(df, horizon=24):
    last = df['temp_c'].iloc[-1]
    return np.array([last]*horizon)
def train_rf(df):
    df = add_features(df)
    X = df[['lag_1','lag_24','rolling_24_mean','rolling_72_mean','hour','dayofyear']].values
    y = df['temp_c'].values
    split = int(0.8*len(X))
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    rmse = mean_squared_error(y_test, preds, squared=False)
    mae = mean_absolute_error(y_test, preds)
    print(f"RF test RMSE={rmse:.3f}, MAE={mae:.3f}")
    joblib.dump(model, 'rf_model_vedant.joblib')
    print('Saved rf_model_vedant.joblib')
    return model
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--city', required=True)
    args = parser.parse_args()
    df = load_last_30_hours(args.city)
    if df.empty:
        raise SystemExit('No temperature data for city; run backfill first.')
    print('Running persistence baseline...')
    baseline = persistence_baseline(df)
    print('Persistence baseline (first 5 preds):', baseline[:5])
    print('Training RandomForest baseline...')
    train_rf(df)
