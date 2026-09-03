import json
from collections import Counter, defaultdict
from pathlib import Path


# =========================================================
# PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROCESSED_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)


# =========================================================
# LOAD SESSION
# =========================================================

def load_session(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# =========================================================
# ANALYZE ONE SESSION
# =========================================================

def analyze_session(path):

    session = load_session(path)

    frames = session.get(
        "frames",
        []
    )

    fps = float(
        session.get(
            "fps",
            0
        )
    )

    activity = session.get(
        "activity",
        "unknown"
    )

    subject = session.get(
        "subject_id",
        "unknown"
    )

    source = session.get(
        "source",
        "unknown"
    )

    if fps > 0:
        duration = len(frames) / fps
    else:
        duration = 0.0

    # -----------------------------------------------------
    # JOINT INFORMATION
    # -----------------------------------------------------

    joint_counts = []

    joint_sets = []

    for frame in frames:

        joints = frame.get(
            "joints",
            {}
        )

        joint_counts.append(
            len(joints)
        )

        joint_sets.append(
            set(joints.keys())
        )

    if joint_counts:

        minimum_joints = min(
            joint_counts
        )

        maximum_joints = max(
            joint_counts
        )

    else:

        minimum_joints = 0
        maximum_joints = 0

    # Joints present in EVERY frame
    if joint_sets:

        common_joints = set.intersection(
            *joint_sets
        )

        all_joints = set.union(
            *joint_sets
        )

    else:

        common_joints = set()
        all_joints = set()

    missing_joint_frames = (
        minimum_joints
        != maximum_joints
    )

    return {
        "file": path.name,
        "session_id": session.get(
            "session_id",
            path.stem
        ),
        "activity": activity,
        "subject": subject,
        "source": source,
        "frames": len(frames),
        "fps": fps,
        "duration": duration,
        "min_joints": minimum_joints,
        "max_joints": maximum_joints,
        "common_joints": common_joints,
        "all_joints": all_joints,
        "joint_inconsistency": (
            missing_joint_frames
        )
    }


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print("=" * 70)
    print("RCON MOTIONAI DATASET ANALYZER")
    print("=" * 70)

    if not PROCESSED_DIR.exists():

        print()
        print("ERROR:")
        print(
            "Processed dataset folder "
            "does not exist."
        )

        print(
            PROCESSED_DIR
        )

        return

    json_files = sorted(
        PROCESSED_DIR.glob(
            "*.json"
        )
    )

    if not json_files:

        print()
        print(
            "No processed MotionAI "
            "JSON files found."
        )

        return

    print()
    print(
        "Dataset directory:"
    )

    print(
        PROCESSED_DIR
    )

    print()
    print(
        "Recordings found:",
        len(json_files)
    )

    # -----------------------------------------------------
    # ANALYZE FILES
    # -----------------------------------------------------

    results = []

    failed = []

    for path in json_files:

        try:

            result = analyze_session(
                path
            )

            results.append(
                result
            )

        except Exception as error:

            failed.append(
                (
                    path.name,
                    str(error)
                )
            )

    # -----------------------------------------------------
    # INDIVIDUAL RECORDINGS
    # -----------------------------------------------------

    print()
    print("=" * 70)
    print("RECORDINGS")
    print("=" * 70)

    for result in results:

        status = "OK"

        if result[
            "joint_inconsistency"
        ]:

            status = (
                "WARNING: "
                "JOINT COUNT CHANGES"
            )

        print()
        print(
            result["file"]
        )

        print(
            f"  Activity : "
            f"{result['activity']}"
        )

        print(
            f"  Frames   : "
            f"{result['frames']}"
        )

        print(
            f"  FPS      : "
            f"{result['fps']}"
        )

        print(
            f"  Duration : "
            f"{result['duration']:.2f} sec"
        )

        print(
            f"  Joints   : "
            f"{result['min_joints']}"
            f" - "
            f"{result['max_joints']}"
        )

        print(
            f"  Status   : "
            f"{status}"
        )

    # -----------------------------------------------------
    # DATASET SUMMARY
    # -----------------------------------------------------

    print()
    print()
    print("=" * 70)
    print("DATASET SUMMARY")
    print("=" * 70)

    total_frames = sum(
        result["frames"]
        for result in results
    )

    total_duration = sum(
        result["duration"]
        for result in results
    )

    activity_counts = Counter(
        result["activity"]
        for result in results
    )

    fps_counts = Counter(
        result["fps"]
        for result in results
    )

    joint_count_distribution = Counter(
        result["max_joints"]
        for result in results
    )

    print()
    print(
        "Valid recordings:",
        len(results)
    )

    print(
        "Failed recordings:",
        len(failed)
    )

    print(
        "Total frames:",
        total_frames
    )

    print(
        "Total motion time:",
        f"{total_duration:.2f} seconds"
    )

    print(
        "Total motion time:",
        f"{total_duration / 60:.2f} minutes"
    )

    # -----------------------------------------------------
    # ACTIVITIES
    # -----------------------------------------------------

    print()
    print("Activity distribution:")
    print()

    for activity, count in sorted(
        activity_counts.items()
    ):

        print(
            f"  {activity:<25} "
            f"{count}"
        )

    # -----------------------------------------------------
    # FPS
    # -----------------------------------------------------

    print()
    print("FPS distribution:")
    print()

    for fps, count in sorted(
        fps_counts.items()
    ):

        print(
            f"  {fps:<10} "
            f"{count} recording(s)"
        )

    # -----------------------------------------------------
    # JOINT COUNTS
    # -----------------------------------------------------

    print()
    print(
        "Joint-count distribution:"
    )

    print()

    for count, recordings in sorted(
        joint_count_distribution.items()
    ):

        print(
            f"  {count:<5} joints -> "
            f"{recordings} recording(s)"
        )

    # -----------------------------------------------------
    # COMMON JOINTS ACROSS DATASET
    # -----------------------------------------------------

    if results:

        dataset_joint_sets = [
            result["common_joints"]
            for result in results
        ]

        common_dataset_joints = (
            set.intersection(
                *dataset_joint_sets
            )
        )

        all_dataset_joints = (
            set.union(
                *[
                    result["all_joints"]
                    for result in results
                ]
            )
        )

        print()
        print(
            "Unique joints across dataset:",
            len(all_dataset_joints)
        )

        print(
            "Joints present in every "
            "frame of every recording:",
            len(common_dataset_joints)
        )

        if (
            common_dataset_joints
            != all_dataset_joints
        ):

            inconsistent_joints = (
                all_dataset_joints
                - common_dataset_joints
            )

            print()
            print(
                "WARNING:"
            )

            print(
                "These joints are not "
                "present everywhere:"
            )

            for joint in sorted(
                inconsistent_joints
            ):

                print(
                    f"  - {joint}"
                )

    # -----------------------------------------------------
    # FAILED FILES
    # -----------------------------------------------------

    if failed:

        print()
        print("=" * 70)
        print("FAILED FILES")
        print("=" * 70)

        for filename, error in failed:

            print()
            print(
                filename
            )

            print(
                "  ",
                error
            )

    # -----------------------------------------------------
    # FINAL HEALTH CHECK
    # -----------------------------------------------------

    print()
    print()
    print("=" * 70)
    print("DATASET HEALTH CHECK")
    print("=" * 70)

    warnings = 0

    if failed:

        warnings += len(
            failed
        )

    inconsistent_sessions = [
        result
        for result in results
        if result[
            "joint_inconsistency"
        ]
    ]

    warnings += len(
        inconsistent_sessions
    )

    if warnings == 0:

        print()
        print(
            "PASS"
        )

        print()
        print(
            "All MotionAI recordings "
            "loaded successfully."
        )

        print(
            "Joint counts are consistent "
            "within each recording."
        )

        print()
        print(
            "Dataset is ready for the "
            "next preprocessing stage."
        )

    else:

        print()
        print(
            f"Dataset contains "
            f"{warnings} warning(s)."
        )

        print(
            "Review warnings before "
            "training AI models."
        )

    print()


if __name__ == "__main__":
    main()