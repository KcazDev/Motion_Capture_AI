import json
from collections import Counter
from pathlib import Path

import numpy as np


# =========================================================
# PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROCESSED_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)

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


# =========================================================
# JOINTS USED FOR FIRST AI MODEL
# =========================================================

SELECTED_JOINTS = [
    "pelvis",
    "spine",
    "chest",
    "neck",
    "head",

    "left_shoulder",
    "left_elbow",
    "left_wrist",

    "right_shoulder",
    "right_elbow",
    "right_wrist",

    "left_hip",
    "left_knee",
    "left_ankle",

    "right_hip",
    "right_knee",
    "right_ankle",
]


# =========================================================
# FEATURE STATISTICS
# =========================================================

POSITION_STATS = [
    "mean",
    "std",
    "min",
    "max",
    "range",
]

VELOCITY_STATS = [
    "mean_abs_velocity",
    "max_abs_velocity",
    "std_velocity",
]


# =========================================================
# LOAD MOTION SESSION
# =========================================================

def load_session(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# =========================================================
# GET BODY SCALE
# =========================================================

def estimate_body_scale(frames):
    """
    Estimate body height so that recordings are less
    dependent on the actor's physical size.

    Uses head-to-ankle distance from the first few frames.
    """

    scales = []

    sample_frames = frames[
        :min(
            15,
            len(frames)
        )
    ]

    for frame in sample_frames:

        joints = frame.get(
            "joints",
            {}
        )

        if (
            "head" not in joints
            or "left_ankle" not in joints
            or "right_ankle" not in joints
        ):
            continue

        head = np.array(
            joints["head"]["position"],
            dtype=np.float32
        )

        left_ankle = np.array(
            joints["left_ankle"]["position"],
            dtype=np.float32
        )

        right_ankle = np.array(
            joints["right_ankle"]["position"],
            dtype=np.float32
        )

        ankle_center = (
            left_ankle
            + right_ankle
        ) / 2.0

        height = np.linalg.norm(
            head - ankle_center
        )

        if height > 0.01:

            scales.append(
                height
            )

    if not scales:
        return 1.0

    return float(
        np.median(
            scales
        )
    )


# =========================================================
# EXTRACT ROOT-CENTERED SEQUENCE
# =========================================================

def extract_joint_sequence(
    frames,
    joint_name,
    body_scale
):

    sequence = []

    for frame in frames:

        joints = frame.get(
            "joints",
            {}
        )

        # Skip frame if pelvis does not exist
        if "pelvis" not in joints:
            continue

        pelvis = np.array(
            joints["pelvis"]["position"],
            dtype=np.float32
        )

        if joint_name in joints:

            joint = np.array(
                joints[joint_name]["position"],
                dtype=np.float32
            )

        else:

            # Missing joint fallback
            joint = pelvis.copy()

        # ---------------------------------------------
        # ROOT CENTERING
        # ---------------------------------------------
        #
        # Removes absolute room position.
        #
        # We care about:
        #
        # "How did the body move?"
        #
        # rather than:
        #
        # "Where in the room was the actor?"

        relative_position = (
            joint - pelvis
        )

        # ---------------------------------------------
        # BODY-SIZE NORMALIZATION
        # ---------------------------------------------

        if body_scale > 0:

            relative_position = (
                relative_position
                / body_scale
            )

        sequence.append(
            relative_position
        )

    return np.array(
        sequence,
        dtype=np.float32
    )


# =========================================================
# POSITION FEATURES
# =========================================================

def calculate_position_features(sequence):

    if len(sequence) == 0:

        return np.zeros(
            15,
            dtype=np.float32
        )

    features = []

    # Calculate statistics separately
    # for X, Y and Z.

    for axis in range(3):

        values = sequence[
            :,
            axis
        ]

        minimum = float(
            np.min(values)
        )

        maximum = float(
            np.max(values)
        )

        features.extend(
            [
                float(
                    np.mean(values)
                ),

                float(
                    np.std(values)
                ),

                minimum,

                maximum,

                maximum - minimum,
            ]
        )

    return np.array(
        features,
        dtype=np.float32
    )


# =========================================================
# VELOCITY FEATURES
# =========================================================

def calculate_velocity_features(
    sequence,
    fps
):

    # Need at least two frames
    if len(sequence) < 2:

        return np.zeros(
            9,
            dtype=np.float32
        )

    velocity = (
        np.diff(
            sequence,
            axis=0
        )
        * fps
    )

    features = []

    for axis in range(3):

        values = velocity[
            :,
            axis
        ]

        features.extend(
            [
                float(
                    np.mean(
                        np.abs(values)
                    )
                ),

                float(
                    np.max(
                        np.abs(values)
                    )
                ),

                float(
                    np.std(values)
                ),
            ]
        )

    return np.array(
        features,
        dtype=np.float32
    )


# =========================================================
# GLOBAL MOVEMENT FEATURES
# =========================================================

def calculate_global_features(
    frames,
    fps,
    body_scale
):

    if not frames:

        return np.zeros(
            7,
            dtype=np.float32
        )

    pelvis_positions = []

    for frame in frames:

        joints = frame.get(
            "joints",
            {}
        )

        if "pelvis" not in joints:
            continue

        pelvis_positions.append(
            np.array(
                joints[
                    "pelvis"
                ][
                    "position"
                ],
                dtype=np.float32
            )
        )

    if not pelvis_positions:

        return np.zeros(
            7,
            dtype=np.float32
        )

    pelvis_positions = np.array(
        pelvis_positions
    )

    if body_scale > 0:

        normalized = (
            pelvis_positions
            / body_scale
        )

    else:

        normalized = pelvis_positions

    duration = (
        len(frames)
        / fps
        if fps > 0
        else 0.0
    )

    displacement = (
        normalized[-1]
        - normalized[0]
    )

    movement_range = (
        np.max(
            normalized,
            axis=0
        )
        -
        np.min(
            normalized,
            axis=0
        )
    )

    return np.array(
        [
            duration,

            float(
                displacement[0]
            ),

            float(
                displacement[1]
            ),

            float(
                displacement[2]
            ),

            float(
                movement_range[0]
            ),

            float(
                movement_range[1]
            ),

            float(
                movement_range[2]
            ),
        ],
        dtype=np.float32
    )


# =========================================================
# EXTRACT FEATURES FROM ONE SESSION
# =========================================================

def extract_features(session):

    frames = session.get(
        "frames",
        []
    )

    fps = float(
        session.get(
            "fps",
            30
        )
    )

    if not frames:

        raise ValueError(
            "Session contains no frames."
        )

    body_scale = estimate_body_scale(
        frames
    )

    feature_parts = []

    # -----------------------------------------------------
    # JOINT MOTION FEATURES
    # -----------------------------------------------------

    for joint_name in SELECTED_JOINTS:

        sequence = extract_joint_sequence(
            frames,
            joint_name,
            body_scale
        )

        position_features = (
            calculate_position_features(
                sequence
            )
        )

        velocity_features = (
            calculate_velocity_features(
                sequence,
                fps
            )
        )

        feature_parts.append(
            position_features
        )

        feature_parts.append(
            velocity_features
        )

    # -----------------------------------------------------
    # GLOBAL MOVEMENT FEATURES
    # -----------------------------------------------------

    global_features = (
        calculate_global_features(
            frames,
            fps,
            body_scale
        )
    )

    feature_parts.append(
        global_features
    )

    return np.concatenate(
        feature_parts
    )


# =========================================================
# BUILD FEATURE NAMES
# =========================================================

def build_feature_names():

    names = []

    axes = [
        "x",
        "y",
        "z"
    ]

    for joint in SELECTED_JOINTS:

        for axis in axes:

            for stat in POSITION_STATS:

                names.append(
                    f"{joint}_"
                    f"{axis}_"
                    f"{stat}"
                )

        for axis in axes:

            for stat in VELOCITY_STATS:

                names.append(
                    f"{joint}_"
                    f"{axis}_"
                    f"{stat}"
                )

    names.extend(
        [
            "duration",
            "pelvis_displacement_x",
            "pelvis_displacement_y",
            "pelvis_displacement_z",
            "pelvis_range_x",
            "pelvis_range_y",
            "pelvis_range_z",
        ]
    )

    return names


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print("=" * 70)
    print("RCON MOTIONAI")
    print("AI DATASET BUILDER")
    print("=" * 70)

    json_files = sorted(
        PROCESSED_DIR.glob(
            "*.json"
        )
    )

    if not json_files:

        print()
        print(
            "ERROR: No processed "
            "MotionAI recordings found."
        )

        return

    # -----------------------------------------------------
    # CHECK ACTIVITY DISTRIBUTION
    # -----------------------------------------------------

    sessions = []

    for path in json_files:

        try:

            session = load_session(
                path
            )

            sessions.append(
                (
                    path,
                    session
                )
            )

        except Exception as error:

            print()
            print(
                "Skipping invalid file:"
            )

            print(
                path.name
            )

            print(
                error
            )

    activity_counts = Counter(
        session.get(
            "activity",
            "unknown"
        )
        for _, session in sessions
    )

    print()
    print("Activity counts:")

    for activity, count in sorted(
        activity_counts.items()
    ):

        print(
            f"  {activity:<25} "
            f"{count}"
        )

    # -----------------------------------------------------
    # ONLY TRAINABLE CLASSES
    # -----------------------------------------------------
    #
    # Classes with only one recording cannot be
    # meaningfully split between training/testing.
    #
    # neutral_standing_001 and walking_001 can remain
    # useful as baseline recordings without being part
    # of this first classifier.

    trainable_activities = {
        activity
        for activity, count
        in activity_counts.items()
        if count >= 2
    }

    print()
    print(
        "Classes included in first AI dataset:"
    )

    for activity in sorted(
        trainable_activities
    ):

        print(
            f"  + {activity}"
        )

    excluded = (
        set(activity_counts.keys())
        - trainable_activities
    )

    if excluded:

        print()
        print(
            "Excluded classes "
            "(fewer than 2 recordings):"
        )

        for activity in sorted(
            excluded
        ):

            print(
                f"  - {activity}"
            )

    # -----------------------------------------------------
    # EXTRACT FEATURES
    # -----------------------------------------------------

    X = []
    y = []
    sample_metadata = []

    print()
    print("=" * 70)
    print("EXTRACTING FEATURES")
    print("=" * 70)

    for path, session in sessions:

        activity = session.get(
            "activity",
            "unknown"
        )

        if (
            activity
            not in trainable_activities
        ):
            continue

        try:

            features = (
                extract_features(
                    session
                )
            )

            X.append(
                features
            )

            y.append(
                activity
            )

            sample_metadata.append(
                {
                    "file": path.name,

                    "session_id": (
                        session.get(
                            "session_id",
                            path.stem
                        )
                    ),

                    "activity": activity,

                    "subject_id": (
                        session.get(
                            "subject_id",
                            "unknown"
                        )
                    ),

                    "fps": (
                        session.get(
                            "fps",
                            0
                        )
                    ),

                    "frames": len(
                        session.get(
                            "frames",
                            []
                        )
                    ),
                }
            )

            print(
                f"  OK  "
                f"{path.name:<35} "
                f"{len(features)} features"
            )

        except Exception as error:

            print(
                f"  FAIL "
                f"{path.name}"
            )

            print(
                f"       {error}"
            )

    # -----------------------------------------------------
    # FINAL ARRAYS
    # -----------------------------------------------------

    if not X:

        print()
        print(
            "ERROR: No usable AI samples."
        )

        return

    X = np.array(
        X,
        dtype=np.float32
    )

    y = np.array(
        y
    )

    feature_names = (
        build_feature_names()
    )

    # -----------------------------------------------------
    # SAVE
    # -----------------------------------------------------

    ML_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    np.save(
        FEATURES_PATH,
        X
    )

    np.save(
        LABELS_PATH,
        y
    )

    metadata = {
        "dataset_name": (
            "RCON MotionAI "
            "Construction Activity Dataset"
        ),

        "samples": len(X),

        "feature_count": (
            X.shape[1]
        ),

        "selected_joints": (
            SELECTED_JOINTS
        ),

        "feature_names": (
            feature_names
        ),

        "classes": sorted(
            list(
                trainable_activities
            )
        ),

        "class_distribution": dict(
            Counter(
                y.tolist()
            )
        ),

        "samples_metadata": (
            sample_metadata
        ),
    }

    with open(
        METADATA_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metadata,
            file,
            indent=2
        )

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    print()
    print("=" * 70)
    print("AI DATASET READY")
    print("=" * 70)

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
        len(
            trainable_activities
        )
    )

    print()
    print(
        "Feature matrix:"
    )

    print(
        FEATURES_PATH
    )

    print()
    print(
        "Labels:"
    )

    print(
        LABELS_PATH
    )

    print()
    print(
        "Metadata:"
    )

    print(
        METADATA_PATH
    )

    print()
    print(
        "Next step:"
    )

    print(
        "Train MotionAI's first "
        "construction activity classifier."
    )

    print()


if __name__ == "__main__":
    main()