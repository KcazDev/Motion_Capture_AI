import json
from collections import Counter
from pathlib import Path

import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)
from sklearn.model_selection import StratifiedKFold


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

RESULTS_DIR = (
    PROJECT_ROOT
    / "results"
)

RESULTS_PATH = (
    RESULTS_DIR
    / "activity_classifier_5fold.json"
)


# =========================================================
# LOAD DATASET
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
# LOAD SAMPLE METADATA
# =========================================================

def load_sample_metadata():

    if not METADATA_PATH.exists():
        return None

    with open(
        METADATA_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        metadata = json.load(file)

    return metadata.get(
        "samples_metadata"
    )


# =========================================================
# CREATE MODEL
# =========================================================

def create_model():

    return RandomForestClassifier(
        n_estimators=500,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        max_features="sqrt",
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )


# =========================================================
# FORMAT ACTIVITY
# =========================================================

def format_activity(activity):

    return (
        activity
        .replace("_", " ")
        .title()
    )


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print("=" * 75)
    print("RCON MOTIONAI")
    print("5-FOLD CONSTRUCTION ACTIVITY EVALUATION")
    print("=" * 75)

    # -----------------------------------------------------
    # LOAD DATA
    # -----------------------------------------------------

    X, y = load_dataset()

    sample_metadata = (
        load_sample_metadata()
    )

    classes = sorted(
        np.unique(y).tolist()
    )

    print()
    print("Dataset:")
    print(
        f"  Samples  : {len(X)}"
    )
    print(
        f"  Features : {X.shape[1]}"
    )
    print(
        f"  Classes  : {len(classes)}"
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
    # VALIDATE FOR 5 FOLDS
    # -----------------------------------------------------

    minimum_class_size = min(
        counts.values()
    )

    if minimum_class_size < 5:

        raise ValueError(
            "5-fold stratified evaluation requires "
            "at least 5 samples in every class."
        )

    # -----------------------------------------------------
    # CREATE CROSS-VALIDATION SPLITS
    # -----------------------------------------------------

    cross_validator = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=42
    )

    fold_accuracies = []

    all_actual = []
    all_predictions = []
    all_confidences = []

    prediction_records = []

    aggregate_confusion = np.zeros(
        (
            len(classes),
            len(classes)
        ),
        dtype=int
    )

    # -----------------------------------------------------
    # RUN FIVE FOLDS
    # -----------------------------------------------------

    for fold_number, (
        train_indices,
        test_indices
    ) in enumerate(
        cross_validator.split(
            X,
            y
        ),
        start=1
    ):

        print()
        print("=" * 75)
        print(
            f"FOLD {fold_number} / 5"
        )
        print("=" * 75)

        X_train = X[
            train_indices
        ]

        X_test = X[
            test_indices
        ]

        y_train = y[
            train_indices
        ]

        y_test = y[
            test_indices
        ]

        print()
        print(
            f"Training samples: {len(X_train)}"
        )

        print(
            f"Testing samples : {len(X_test)}"
        )

        # -------------------------------------------------
        # TRAIN TEMPORARY MODEL
        # -------------------------------------------------

        model = create_model()

        model.fit(
            X_train,
            y_train
        )

        # -------------------------------------------------
        # PREDICT
        # -------------------------------------------------

        predictions = model.predict(
            X_test
        )

        probabilities = (
            model.predict_proba(
                X_test
            )
        )

        fold_accuracy = (
            accuracy_score(
                y_test,
                predictions
            )
        )

        fold_accuracies.append(
            fold_accuracy
        )

        print()
        print(
            f"Fold Accuracy: "
            f"{fold_accuracy * 100:.2f}%"
        )

        print()
        print("Predictions:")
        print()

        # -------------------------------------------------
        # RECORD INDIVIDUAL PREDICTIONS
        # -------------------------------------------------

        for local_index, dataset_index in enumerate(
            test_indices
        ):

            actual = y_test[
                local_index
            ]

            predicted = predictions[
                local_index
            ]

            confidence = float(
                np.max(
                    probabilities[
                        local_index
                    ]
                )
            )

            correct = (
                actual == predicted
            )

            if (
                sample_metadata
                and dataset_index
                < len(sample_metadata)
            ):

                filename = (
                    sample_metadata[
                        dataset_index
                    ].get(
                        "file",
                        f"sample_{dataset_index}"
                    )
                )

            else:

                filename = (
                    f"sample_{dataset_index}"
                )

            result_text = (
                "CORRECT"
                if correct
                else "WRONG"
            )

            print(
                f"{filename}"
            )

            print(
                f"  Actual     : "
                f"{format_activity(actual)}"
            )

            print(
                f"  Predicted  : "
                f"{format_activity(predicted)}"
            )

            print(
                f"  Confidence : "
                f"{confidence * 100:.2f}%"
            )

            print(
                f"  Result     : "
                f"{result_text}"
            )

            print()

            all_actual.append(
                actual
            )

            all_predictions.append(
                predicted
            )

            all_confidences.append(
                confidence
            )

            prediction_records.append(
                {
                    "fold": fold_number,
                    "file": filename,
                    "actual": str(actual),
                    "predicted": str(
                        predicted
                    ),
                    "confidence": confidence,
                    "correct": bool(
                        correct
                    )
                }
            )

        # -------------------------------------------------
        # FOLD CONFUSION MATRIX
        # -------------------------------------------------

        fold_matrix = confusion_matrix(
            y_test,
            predictions,
            labels=classes
        )

        aggregate_confusion += (
            fold_matrix
        )

    # =====================================================
    # OVERALL RESULTS
    # =====================================================

    all_actual = np.array(
        all_actual
    )

    all_predictions = np.array(
        all_predictions
    )

    overall_accuracy = (
        accuracy_score(
            all_actual,
            all_predictions
        )
    )

    mean_fold_accuracy = float(
        np.mean(
            fold_accuracies
        )
    )

    std_fold_accuracy = float(
        np.std(
            fold_accuracies
        )
    )

    average_confidence = float(
        np.mean(
            all_confidences
        )
    )

    print()
    print()
    print("=" * 75)
    print("5-FOLD CROSS-VALIDATION RESULTS")
    print("=" * 75)

    print()
    print("Fold accuracies:")

    for index, accuracy in enumerate(
        fold_accuracies,
        start=1
    ):

        print(
            f"  Fold {index}: "
            f"{accuracy * 100:.2f}%"
        )

    print()
    print(
        f"Mean fold accuracy: "
        f"{mean_fold_accuracy * 100:.2f}%"
    )

    print(
        f"Standard deviation : "
        f"{std_fold_accuracy * 100:.2f}%"
    )

    print()
    print(
        f"Overall out-of-fold accuracy: "
        f"{overall_accuracy * 100:.2f}%"
    )

    print(
        f"Average prediction confidence: "
        f"{average_confidence * 100:.2f}%"
    )

    # -----------------------------------------------------
    # CLASSIFICATION REPORT
    # -----------------------------------------------------

    print()
    print("=" * 75)
    print("OUT-OF-FOLD CLASSIFICATION REPORT")
    print("=" * 75)

    print()

    report_text = (
        classification_report(
            all_actual,
            all_predictions,
            labels=classes,
            zero_division=0
        )
    )

    print(
        report_text
    )

    report_dict = (
        classification_report(
            all_actual,
            all_predictions,
            labels=classes,
            zero_division=0,
            output_dict=True
        )
    )

    # -----------------------------------------------------
    # CONFUSION MATRIX
    # -----------------------------------------------------

    print("=" * 75)
    print("AGGREGATE CONFUSION MATRIX")
    print("=" * 75)

    print()
    print("Class order:")

    for index, activity in enumerate(
        classes
    ):

        print(
            f"  {index}: "
            f"{activity}"
        )

    print()

    print(
        aggregate_confusion
    )

    # -----------------------------------------------------
    # PER-CLASS ACCURACY
    # -----------------------------------------------------

    print()
    print("=" * 75)
    print("PER-CLASS RESULTS")
    print("=" * 75)

    print()

    for activity in classes:

        mask = (
            all_actual
            == activity
        )

        class_actual = (
            all_actual[
                mask
            ]
        )

        class_predictions = (
            all_predictions[
                mask
            ]
        )

        class_accuracy = (
            accuracy_score(
                class_actual,
                class_predictions
            )
        )

        print(
            f"{format_activity(activity):<25} "
            f"{class_accuracy * 100:>6.2f}%"
        )

    # -----------------------------------------------------
    # FIND MISCLASSIFICATIONS
    # -----------------------------------------------------

    errors = [
        record
        for record in prediction_records
        if not record[
            "correct"
        ]
    ]

    print()
    print("=" * 75)
    print("MISCLASSIFICATIONS")
    print("=" * 75)

    if not errors:

        print()
        print(
            "No misclassified recordings."
        )

    else:

        print()

        for record in errors:

            print(
                record["file"]
            )

            print(
                f"  Actual    : "
                f"{format_activity(record['actual'])}"
            )

            print(
                f"  Predicted : "
                f"{format_activity(record['predicted'])}"
            )

            print(
                f"  Confidence: "
                f"{record['confidence'] * 100:.2f}%"
            )

            print()

    # -----------------------------------------------------
    # SAVE RESULTS
    # -----------------------------------------------------

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    results = {
        "evaluation": (
            "5-fold stratified cross-validation"
        ),

        "samples": int(
            len(X)
        ),

        "feature_count": int(
            X.shape[1]
        ),

        "classes": classes,

        "folds": 5,

        "fold_accuracies": [
            float(value)
            for value in fold_accuracies
        ],

        "mean_fold_accuracy": (
            mean_fold_accuracy
        ),

        "std_fold_accuracy": (
            std_fold_accuracy
        ),

        "overall_out_of_fold_accuracy": (
            float(
                overall_accuracy
            )
        ),

        "average_confidence": (
            average_confidence
        ),

        "confusion_matrix": (
            aggregate_confusion.tolist()
        ),

        "classification_report": (
            report_dict
        ),

        "predictions": (
            prediction_records
        )
    }

    with open(
        RESULTS_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            indent=2
        )

    # -----------------------------------------------------
    # COMPLETE
    # -----------------------------------------------------

    print()
    print()
    print("=" * 75)
    print("EVALUATION COMPLETE")
    print("=" * 75)

    print()
    print(
        "Every recording was used as "
        "unseen test data exactly once."
    )

    print()
    print(
        "Results saved to:"
    )

    print(
        RESULTS_PATH
    )

    print()


if __name__ == "__main__":
    main()