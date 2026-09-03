import argparse
import json
from pathlib import Path

import joblib
import numpy as np

from Scripts.build_ml_dataset import extract_features


# =========================================================
# PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "activity_classifier.pkl"
)


# =========================================================
# ARGUMENTS
# =========================================================

def parse_arguments():

    parser = argparse.ArgumentParser(
        description=(
            "Classify a MotionAI construction "
            "activity recording."
        )
    )

    parser.add_argument(
        "motion_file",
        help="Processed MotionAI JSON recording"
    )

    return parser.parse_args()


# =========================================================
# LOAD MOTION
# =========================================================

def load_session(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# =========================================================
# FORMAT LABEL
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

    args = parse_arguments()

    motion_path = Path(
        args.motion_file
    ).resolve()

    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not motion_path.exists():

        print()
        print("ERROR:")
        print("Motion file not found:")
        print(motion_path)
        print()

        return

    if not MODEL_PATH.exists():

        print()
        print("ERROR:")
        print("Trained classifier not found:")
        print(MODEL_PATH)
        print()

        return

    # -----------------------------------------------------
    # LOAD MODEL + MOTION
    # -----------------------------------------------------

    model = joblib.load(
        MODEL_PATH
    )

    session = load_session(
        motion_path
    )

    # -----------------------------------------------------
    # FEATURE EXTRACTION
    # -----------------------------------------------------

    features = extract_features(
        session
    )

    features = np.array(
        [features],
        dtype=np.float32
    )

    # -----------------------------------------------------
    # PREDICTION
    # -----------------------------------------------------

    prediction = model.predict(
        features
    )[0]

    probabilities = (
        model.predict_proba(
            features
        )[0]
    )

    classes = (
        model.classes_
    )

    confidence = float(
        np.max(
            probabilities
        )
    )

    # Sort probabilities highest → lowest
    ranking = sorted(
        zip(
            classes,
            probabilities
        ),
        key=lambda item: item[1],
        reverse=True
    )

    # -----------------------------------------------------
    # DISPLAY
    # -----------------------------------------------------

    print()
    print("=" * 70)
    print("RCON MOTIONAI")
    print("CONSTRUCTION ACTIVITY RECOGNITION")
    print("=" * 70)

    print()
    print("Recording:")
    print(motion_path.name)

    print()
    print("Predicted Activity:")
    print(
        format_activity(
            prediction
        )
    )

    print()
    print(
        f"Confidence: "
        f"{confidence * 100:.2f}%"
    )

    print()
    print("=" * 70)
    print("CLASS PROBABILITIES")
    print("=" * 70)

    print()

    for activity, probability in ranking:

        print(
            f"{format_activity(activity):<25} "
            f"{probability * 100:>6.2f}%"
        )

    print()

    actual_activity = session.get(
        "activity"
    )

    if actual_activity:

        print(
            "Recorded Label:"
        )

        print(
            format_activity(
                actual_activity
            )
        )

        print()

        if actual_activity == prediction:

            print(
                "Result: CORRECT"
            )

        else:

            print(
                "Result: INCORRECT"
            )

    print()


if __name__ == "__main__":
    main()