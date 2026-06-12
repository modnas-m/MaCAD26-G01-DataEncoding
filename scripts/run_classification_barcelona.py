import os
import json
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import accuracy_score, classification_report
import joblib


ROOT = os.path.dirname(os.path.dirname(__file__))
CSV_DIR = os.path.join(ROOT, 'csv')
MODELS_DIR = os.path.join(ROOT, 'models')
os.makedirs(MODELS_DIR, exist_ok=True)

FEATURE_COLS = [
    'lighting_norm', 'visibility_norm', 'connectivity_norm',
    'enclosure_norm', 'dominant_land_use_score_norm', 'public_transport_proximity_m_norm',
    'pedestrian_priority_score_norm'
]


def load_feature_norm_stats(path=None):
    if path is None:
        path = os.path.join(MODELS_DIR, 'feature_norm_stats.json')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf8') as fh:
            return json.load(fh)
    return None


def ensure_normalized_columns(df, stats=None):
    # stats: dict of {feature: {min,max}}. If missing, compute min/max from df
    raw_map = {
        'lighting_norm': 'lighting',
        'visibility_norm': 'visibility',
        'connectivity_norm': 'connectivity',
        'enclosure_norm': 'enclosure',
        'dominant_land_use_score_norm': 'dominant_land_use_score',
        'public_transport_proximity_m_norm': 'public_transport_proximity_m',
        'pedestrian_priority_score_norm': 'pedestrian_priority_score'
    }

    for norm_col, raw_col in raw_map.items():
        if norm_col in df.columns:
            continue
        if raw_col not in df.columns:
            df[norm_col] = np.nan
            continue
        if stats and raw_col in stats and stats[raw_col]['max'] != stats[raw_col]['min']:
            mn = stats[raw_col]['min']
            mx = stats[raw_col]['max']
        else:
            mn = float(df[raw_col].min())
            mx = float(df[raw_col].max())
        # avoid division by zero
        if mx == mn:
            df[norm_col] = 0.0
        else:
            df[norm_col] = (df[raw_col] - mn) / (mx - mn)
    return df


def produce_kmeans_labels(df):
    # expect normalized columns
    X = df[FEATURE_COLS].dropna()
    if X.shape[0] == 0:
        raise ValueError('No rows with complete normalized features to cluster')

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # PCA projection
    pca = PCA(random_state=42)
    X_pca = pca.fit_transform(X_scaled)

    kmeans = KMeans(n_clusters=3, random_state=42, n_init=20)
    labels = kmeans.fit_predict(X_pca)

    result_idx = X.index
    result_df = df.loc[result_idx].copy().reset_index(drop=True)
    result_df['cluster_id'] = labels
    result_df['pc1_score'] = X_pca[:, 0]

    # order clusters by mean pc1
    pc1_means = result_df.groupby('cluster_id')['pc1_score'].mean()
    ordered = pc1_means.sort_values().index.tolist()
    risk_map = {ordered[0]: 'low', ordered[1]: 'medium', ordered[2]: 'high'}
    result_df['risk_class'] = result_df['cluster_id'].map(risk_map)

    return result_df, scaler


def train_and_save_models(df):
    # df must contain FEATURE_COLS and 'risk_class'
    X = df[FEATURE_COLS].values
    y = df['risk_class'].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    lr = LogisticRegression(solver='lbfgs', max_iter=1000, random_state=42)
    lr.fit(X_train_s, y_train)

    rf = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1)
    rf.fit(X_train_s, y_train)

    # metrics
    y_pred_lr = lr.predict(X_test_s)
    y_pred_rf = rf.predict(X_test_s)
    print('Logistic acc:', accuracy_score(y_test, y_pred_lr))
    print(classification_report(y_test, y_pred_lr))
    print('RandomForest acc:', accuracy_score(y_test, y_pred_rf))
    print(classification_report(y_test, y_pred_rf))

    # cross-val
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    print('LR CV mean acc:', cross_val_score(lr, scaler.transform(X), y, cv=cv, scoring='accuracy').mean())
    print('RF CV mean acc:', cross_val_score(rf, scaler.transform(X), y, cv=cv, scoring='accuracy').mean())

    # save
    joblib.dump(lr, os.path.join(MODELS_DIR, 'logistic_regression.pkl'))
    joblib.dump(rf, os.path.join(MODELS_DIR, 'random_forest.pkl'))
    joblib.dump(scaler, os.path.join(MODELS_DIR, 'scaler.pkl'))
    print('Saved models to', MODELS_DIR)


def main():
    # Prefer already classified segments
    classified_path = os.path.join(CSV_DIR, 'segment_risk_classified.csv')
    scores_path = os.path.join(CSV_DIR, 'segment_risk_scores_w-id.csv')
    fallback_path = os.path.join(CSV_DIR, 'features_barcelona_with_location_id_augmented.csv')

    if os.path.exists(classified_path):
        print('Loading existing classified segments:', classified_path)
        df = pd.read_csv(classified_path)
    elif os.path.exists(scores_path):
        print('Loading segment risk scores:', scores_path)
        df = pd.read_csv(scores_path)
    elif os.path.exists(fallback_path):
        print('Loading raw Barcelona features:', fallback_path)
        df = pd.read_csv(fallback_path)
    else:
        raise FileNotFoundError('No input CSV found in csv/ directory')

    stats = load_feature_norm_stats()
    df = ensure_normalized_columns(df, stats=stats)

    if 'risk_class' not in df.columns or df['risk_class'].isna().all():
        print('No `risk_class` found — running K-Means to create pseudo-labels')
        result_df, scaler_for_save = produce_kmeans_labels(df)
        # merge back classification columns into original df by location_id if present
        if 'location_id' in result_df.columns:
            merged = result_df.set_index('location_id')
            # write out classified CSV
            out_path = os.path.join(CSV_DIR, 'segment_risk_classified.csv')
            result_df.to_csv(out_path, index=False)
            print('Wrote classified segments to', out_path)
            df = result_df
        else:
            df = result_df
    else:
        print('Using existing `risk_class` in dataframe')

    # train models
    train_and_save_models(df)


if __name__ == '__main__':
    main()
