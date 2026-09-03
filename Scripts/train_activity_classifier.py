import json
from collections import Counter
from pathlib import Path

import joblib
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)
from sklearn.model_selection import train_test_split


# =========================================================
# PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

ML_DIR = (
    PROJECT_ROOT
    / "data"
    / "ml"
)

FEATURES_PATH = (
    ML_DIR
    / "features.npy"
)

LABELS_PATH = (
    ML_DIR
    / "labels.npy"
)

METADATA_PATH = (
    ML_DIR
    / "metadata.json"
)

MODEL_DIR = (
    PROJECT_ROOT
    / "models"
)

MODEL_PATH = (
    MODEL_DIR
    / "activity_classifier.pkl"
)

MODEL_INFO_PATH = (
    MODEL_DIR
    / "activity_classifier_info.json"
)


# =========================================================
# LOAD DATA
# =========================================================

def load_dataset():

    if not FEATURES_PATH.exists():
        raise FileNotFoundError(
            f"Features not found: {FEATURES_PATH}"
        )

    if not LABELS_PATH.exists():
        raise FileNotFoundError(
            f"Labels not found: {LABELS_PATH}"
        )

    X = np.load(
        FEATURES_PATH
    )

    y = np.load(
        LABELS_PATH,
        allow_pickle=True
    )

    return X, y


# =========================================================
# VALIDATE DATA
# =========================================================

def validate_dataset(X, y):

    if len(X) != len(y):
        raise ValueError(
            "Feature and label counts do not match."
        )

    if len(X) == 0:
        raise ValueError(
            "Dataset contains no samples."
        )

    if np.isnan(X).any():
        raise ValueError(
            "Feature dataset contains NaN values."
        )

    if np.isinf(X).any():
        raise ValueError(
            "Feature dataset contains infinite values."
        )


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print("=" * 70)
    print("RCON MOTIONAI")
    print("CONSTRUCTION ACTIVITY CLASSIFIER")
    print("=" * 70)

    # -----------------------------------------------------
    # LOAD DATA
    # -----------------------------------------------------

    X, y = load_dataset()

    validate_dataset(
        X,
        y
    )

    classes = sorted(
        np.unique(y).tolist()
    )

    print()
    print("Dataset:")
    print()

    print(
        "Samples:",
        X.shape[0]
    )

    print(
        "Features per sample:",
        X.shape[1]
    )

    print(
        "Classes:",
        len(classes)
    )

    print()
    print("Class distribution:")

    counts = Counter(
        y.tolist()
    )

    for activity, count in sorted(
        counts.items()
    ):
        print(
            f"  {activity:<25} {count}"
        )

    # -----------------------------------------------------
    # TRAIN / TEST SPLIT
    # -----------------------------------------------------
    #
    # With 25 samples and 5 classes,
    # test_size=0.20 gives:
    #
    # 20 training recordings
    # 5 testing recordings
    #
    # Stratification ensures one test recording
    # from each activity class.

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=42,
            stratify=y
        )
    )

    print()
    print("=" * 70)
    print("TRAIN / TEST SPLIT")
    print("=" * 70)

    print()
    print(
        "Training samples:",
        len(X_train)
    )

    print(
        "Testing samples:",
        len(X_test)
    )

    print()
    print("Testing recordings by class:")

    test_counts = Counter(
        y_test.tolist()
    )

    for activity, count in sorted(
        test_counts.items()
    ):

        print(
            f"  {activity:<25} {count}"
        )

    # -----------------------------------------------------
    # CREATE MODEL
    # -----------------------------------------------------

    print()
    print("=" * 70)
    print("TRAINING RANDOM FOREST")
    print("=" * 70)

    model = RandomForestClassifier(
        n_estimators=500,

        max_depth=None,

        min_samples_split=2,

        min_samples_leaf=1,

        max_features="sqrt",

        class_weight="balanced",

        random_state=42,

        n_jobs=-1
    )

    model.fit(
        X_train,
        y_train
    )

    print()
    print("Training complete.")

    # -----------------------------------------------------
    # TEST MODEL
    # -----------------------------------------------------

    predictions = model.predict(
        X_test
    )

    probabilities = (
        model.predict_proba(
            X_test
        )
    )

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    # -----------------------------------------------------
    # RESULTS
    # -----------------------------------------------------

    print()
    print("=" * 70)
    print("MODEL RESULTS")
    print("=" * 70)

    print()
    print(
        f"Accuracy: "
        f"{accuracy * 100:.2f}%"
    )

    print()
    print("Individual test predictions:")
    print()

    for index in range(
        len(y_test)
    ):

        actual = y_test[index]

        predicted = predictions[index]

        confidence = float(
            np.max(
                probabilities[index]
            )
        )

        result = (
            "CORRECT"
            if actual == predicted
            else "WRONG"
        )

        print(
            f"Sample {index + 1}"
        )

        print(
            f"  Actual     : {actual}"
        )

        print(
            f"  Predicted  : {predicted}"
        )

        print(
            f"  Confidence : "
            f"{confidence * 100:.2f}%"
        )

        print(
            f"  Result     : {result}"
        )

        print()

    # -----------------------------------------------------
    # CLASSIFICATION REPORT
    # -----------------------------------------------------

    print("=" * 70)
    print("CLASSIFICATION REPORT")
    print("=" * 70)

    print()

    report = classification_report(
        y_test,
        predictions,
        labels=classes,
        zero_division=0
    )

    print(
        report
    )

    # -----------------------------------------------------
    # CONFUSION MATRIX
    # -----------------------------------------------------

    print("=" * 70)
    print("CONFUSION MATRIX")
    print("=" * 70)

    print()

    matrix = confusion_matrix(
        y_test,
        predictions,
        labels=classes
    )

    print(
        "Class order:"
    )

    for index, activity in enumerate(
        classes
    ):

        print(
            f"  {index}: {activity}"
        )

    print()
    print(matrix)

    # -----------------------------------------------------
    # FEATURE IMPORTANCE
    # -----------------------------------------------------

    feature_importances = (
        model.feature_importances_
    )

    top_indices = np.argsort(
        feature_importances
    )[::-1][:15]

    print()
    print("=" * 70)
    print("TOP MOTION FEATURES")
    print("=" * 70)

    feature_names = None

    if METADATA_PATH.exists():

        with open(
            METADATA_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            metadata = json.load(
                file
            )

        feature_names = (
            metadata.get(
                "feature_names"
            )
        )

    print()

    for rank, feature_index in enumerate(
        top_indices,
        start=1
    ):

        importance = (
            feature_importances[
                feature_index
            ]
        )

        if (
            feature_names
            and feature_index
            < len(feature_names)
        ):

            feature_name = (
                feature_names[
                    feature_index
                ]
            )

        else:

            feature_name = (
                f"feature_{feature_index}"
            )

        print(
            f"{rank:>2}. "
            f"{feature_name:<45} "
            f"{importance:.5f}"
        )

    # -----------------------------------------------------
    # SAVE TRAINED MODEL
    # -----------------------------------------------------

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        model,
        MODEL_PATH
    )

    model_info = {
        "model": (
            "RandomForestClassifier"
        ),

        "version": "0.1",

        "training_samples": (
            len(X_train)
        ),

        "testing_samples": (
            len(X_test)
        ),

        "feature_count": (
            X.shape[1]
        ),

        "classes": classes,

        "accuracy": float(
            accuracy
        ),

        "random_state": 42,

        "n_estimators": 500,
    }

    with open(
        MODEL_INFO_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            model_info,
            file,
            indent=2
        )

    # -----------------------------------------------------
    # COMPLETE
    # -----------------------------------------------------

    print()
    print("=" * 70)
    print("MOTIONAI MODEL SAVED")
    print("=" * 70)

    print()
    print("Classifier:")
    print(
        MODEL_PATH
    )

    print()
    print("Model metadata:")
    print(
        MODEL_INFO_PATH
    )

    print()
    print(
        "MotionAI can now classify "
        "construction activities."
    )

    print()


if __name__ == "__main__":
    main()