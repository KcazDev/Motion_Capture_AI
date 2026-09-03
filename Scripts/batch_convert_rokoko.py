import argparse
import re
import subprocess
import sys
from pathlib import Path


# =========================================================
# DEFAULT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DEFAULT_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
CONVERTER_SCRIPT = PROJECT_ROOT / "scripts" / "convert_rokoko_fbx.py"


# =========================================================
# FIND BLENDER
# =========================================================

def find_blender():

    possible_paths = [
        Path(
            r"C:\Program Files\Blender Foundation"
            r"\Blender 5.2\blender.exe"
        ),
        Path(
            r"C:\Program Files\Blender Foundation"
            r"\Blender 5.2 LTS\blender.exe"
        ),
        Path(
            r"C:\Program Files\Blender Foundation"
            r"\Blender 5.1\blender.exe"
        ),
        Path(
            r"C:\Program Files\Blender Foundation"
            r"\Blender 4.5\blender.exe"
        ),
    ]

    for path in possible_paths:

        if path.exists():
            return path

    # Search Blender Foundation folder
    blender_root = Path(
        r"C:\Program Files\Blender Foundation"
    )

    if blender_root.exists():

        matches = list(
            blender_root.glob(
                "Blender */blender.exe"
            )
        )

        if matches:

            # Prefer newest-looking installation
            matches.sort(
                reverse=True
            )

            return matches[0]

    return None


# =========================================================
# ACTIVITY LABEL
# =========================================================

def get_activity_from_filename(filename):
    """
    Converts:

        box_lift_001
        hammer_strike_003
        drill_forward_002

    into:

        box_lift
        hammer_strike
        drill_forward
    """

    stem = Path(
        filename
    ).stem

    activity = re.sub(
        r"_\d+$",
        "",
        stem
    )

    return activity


# =========================================================
# ARGUMENTS
# =========================================================

def parse_arguments():

    parser = argparse.ArgumentParser(
        description=(
            "Batch convert Rokoko FBX recordings "
            "into MotionAI JSON sessions."
        )
    )

    parser.add_argument(
        "--raw-dir",
        default=str(DEFAULT_RAW_DIR),
        help="Directory containing raw Rokoko FBX files"
    )

    parser.add_argument(
        "--processed-dir",
        default=str(DEFAULT_PROCESSED_DIR),
        help="Directory for converted MotionAI JSON files"
    )

    parser.add_argument(
        "--subject",
        default="subject_001",
        help="Subject identifier"
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Reconvert JSON files that already exist"
    )

    return parser.parse_args()


# =========================================================
# CONVERT ONE FILE
# =========================================================

def convert_file(
    blender_path,
    input_path,
    output_path,
    activity,
    subject
):

    command = [
        str(blender_path),

        "--background",

        "--python",
        str(CONVERTER_SCRIPT),

        "--",

        "--input",
        str(input_path),

        "--output",
        str(output_path),

        "--activity",
        activity,

        "--subject",
        subject,
    ]

    print()
    print("=" * 65)
    print("RCON MOTIONAI")
    print("=" * 65)

    print()
    print("Converting:")
    print(input_path.name)

    print()
    print("Activity:")
    print(activity)

    print()
    print("Output:")
    print(output_path.name)

    print()

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT
    )

    return result.returncode == 0


# =========================================================
# MAIN
# =========================================================

def main():

    args = parse_arguments()

    raw_dir = Path(
        args.raw_dir
    ).resolve()

    processed_dir = Path(
        args.processed_dir
    ).resolve()

    # -----------------------------------------------------
    # CHECK BLENDER
    # -----------------------------------------------------

    blender_path = find_blender()

    if blender_path is None:

        print()
        print("ERROR:")
        print("Could not locate Blender automatically.")
        print()
        print(
            "Open batch_convert_rokoko.py "
            "and add your Blender executable "
            "to find_blender()."
        )

        sys.exit(1)

    print()
    print("Blender:")
    print(blender_path)

    # -----------------------------------------------------
    # CHECK CONVERTER
    # -----------------------------------------------------

    if not CONVERTER_SCRIPT.exists():

        print()
        print("ERROR:")
        print("MotionAI FBX converter not found:")
        print(CONVERTER_SCRIPT)

        sys.exit(1)

    # -----------------------------------------------------
    # CHECK RAW DIRECTORY
    # -----------------------------------------------------

    if not raw_dir.exists():

        print()
        print("ERROR:")
        print("Raw motion directory does not exist:")
        print(raw_dir)

        sys.exit(1)

    processed_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------------------------------
    # FIND FBX RECORDINGS
    # -----------------------------------------------------

    fbx_files = sorted(
        raw_dir.glob("*.fbx")
    )

    if not fbx_files:

        print()
        print("No FBX recordings found in:")
        print(raw_dir)

        return

    print()
    print(
        f"Found {len(fbx_files)} "
        f"Rokoko recording(s)."
    )

    # -----------------------------------------------------
    # TRACK RESULTS
    # -----------------------------------------------------

    successful = []
    failed = []
    skipped = []

    # -----------------------------------------------------
    # CONVERT
    # -----------------------------------------------------

    for index, input_path in enumerate(
        fbx_files,
        start=1
    ):

        output_path = (
            processed_dir
            / f"{input_path.stem}.json"
        )

        activity = (
            get_activity_from_filename(
                input_path.name
            )
        )

        print()
        print(
            f"[{index}/{len(fbx_files)}]"
        )

        # Skip existing conversions
        if (
            output_path.exists()
            and not args.overwrite
        ):

            print(
                f"Skipping existing file: "
                f"{output_path.name}"
            )

            skipped.append(
                input_path.name
            )

            continue

        success = convert_file(
            blender_path=blender_path,
            input_path=input_path,
            output_path=output_path,
            activity=activity,
            subject=args.subject
        )

        if success:

            successful.append(
                input_path.name
            )

        else:

            failed.append(
                input_path.name
            )

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    print()
    print()
    print("=" * 65)
    print("MOTIONAI DATASET CONVERSION SUMMARY")
    print("=" * 65)

    print()
    print(
        "Total FBX recordings:",
        len(fbx_files)
    )

    print(
        "Successfully converted:",
        len(successful)
    )

    print(
        "Skipped:",
        len(skipped)
    )

    print(
        "Failed:",
        len(failed)
    )

    if successful:

        print()
        print("Converted:")

        for filename in successful:
            print(
                f"  + {filename}"
            )

    if skipped:

        print()
        print("Skipped existing:")

        for filename in skipped:
            print(
                f"  - {filename}"
            )

    if failed:

        print()
        print("FAILED:")

        for filename in failed:
            print(
                f"  ! {filename}"
            )

    print()

    if not failed:

        print(
            "MotionAI construction dataset ready."
        )

    else:

        print(
            "Some recordings failed conversion."
        )

    print()


if __name__ == "__main__":
    main()