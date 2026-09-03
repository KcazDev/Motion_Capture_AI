import argparse
import json
import math
import re
import sys
from pathlib import Path

import bpy
from mathutils import Matrix


# =========================================================
# ROKOKO -> MOTIONAI JOINT MAPPING
# =========================================================

JOINT_MAP = {
    # Core
    "Hips": "pelvis",

    "Spine1": "lower_spine",
    "Spine2": "spine",
    "Spine3": "upper_spine",
    "Spine4": "chest",

    "Neck": "neck",
    "Head": "head",

    # Left arm
    "LeftShoulder": "left_clavicle",
    "LeftArm": "left_shoulder",
    "LeftForeArm": "left_elbow",
    "LeftHand": "left_wrist",

    # Right arm
    "RightShoulder": "right_clavicle",
    "RightArm": "right_shoulder",
    "RightForeArm": "right_elbow",
    "RightHand": "right_wrist",

    # Left leg
    "LeftThigh": "left_hip",
    "LeftUpLeg": "left_hip",
    "LeftShin": "left_knee",
    "LeftLeg": "left_knee",
    "LeftFoot": "left_ankle",
    "LeftToe": "left_toe",

    # Right leg
    "RightThigh": "right_hip",
    "RightUpLeg": "right_hip",
    "RightShin": "right_knee",
    "RightLeg": "right_knee",
    "RightFoot": "right_ankle",
    "RightToe": "right_toe",
}


# =========================================================
# ARGUMENTS
# =========================================================

def parse_arguments():

    # Blender arguments appear after "--"
    if "--" in sys.argv:
        argv = sys.argv[
            sys.argv.index("--") + 1:
        ]
    else:
        argv = []

    parser = argparse.ArgumentParser(
        description="Convert Rokoko FBX into MotionAI JSON"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Input Rokoko FBX"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output MotionAI JSON"
    )

    parser.add_argument(
        "--activity",
        default="unknown_motion",
        help="Motion label"
    )

    parser.add_argument(
        "--subject",
        default="subject_001",
        help="Subject ID"
    )

    parser.add_argument(
        "--fps",
        type=float,
        default=None,
        help="Optional FPS override"
    )

    return parser.parse_args(argv)


# =========================================================
# JOINT NAME NORMALIZATION
# =========================================================

def normalize_joint_name(name):

    # Remove namespaces if present
    if ":" in name:
        name = name.split(":")[-1]

    if name in JOINT_MAP:
        return JOINT_MAP[name]

    # Preserve finger/toe/etc. bones using snake_case.
    #
    # Example:
    #
    # LeftFinger1Proximal
    # ->
    # left_finger1_proximal

    name = re.sub(
        r"([a-z0-9])([A-Z])",
        r"\1_\2",
        name
    )

    name = name.replace(
        " ",
        "_"
    )

    return name.lower()


# =========================================================
# CLEAR BLENDER SCENE
# =========================================================

def clear_scene():

    bpy.ops.object.select_all(
        action="SELECT"
    )

    bpy.ops.object.delete(
        use_global=False
    )


# =========================================================
# IMPORT FBX
# =========================================================

def import_fbx(path):

    print()
    print("Importing Rokoko FBX:")
    print(path)

    result = bpy.ops.wm.fbx_import(
        filepath=str(path),
        use_anim=True
    )

    print("FBX import result:")
    print(result)


# =========================================================
# FIND ARMATURE
# =========================================================

def find_armature():

    armatures = [
        obj
        for obj in bpy.context.scene.objects
        if obj.type == "ARMATURE"
    ]

    if not armatures:
        raise RuntimeError(
            "No armature found in Rokoko FBX."
        )

    # If multiple armatures exist,
    # choose the one with the most bones.
    armature = max(
        armatures,
        key=lambda obj: len(obj.pose.bones)
    )

    return armature


# =========================================================
# FRAME RANGE
# =========================================================

def get_frame_range(armature):

    if (
        armature.animation_data
        and armature.animation_data.action
    ):

        action = armature.animation_data.action

        start, end = action.frame_range

        return (
            math.floor(start),
            math.ceil(end)
        )

    # Fallback
    return (
        bpy.context.scene.frame_start,
        bpy.context.scene.frame_end
    )


# =========================================================
# COORDINATE CONVERSION
# =========================================================

# Blender:
#
# X = left / right
# Y = forward / backward
# Z = height
#
# MotionAI:
#
# X = left / right
# Y = height
# Z = forward / backward

COORDINATE_CONVERSION = Matrix((
    (1.0, 0.0, 0.0),
    (0.0, 0.0, 1.0),
    (0.0, -1.0, 0.0),
))


def convert_position(position):

    converted = (
        COORDINATE_CONVERSION
        @ position
    )

    return [
        float(converted.x),
        float(converted.y),
        float(converted.z)
    ]


def convert_rotation(matrix):

    blender_rotation = (
        matrix.to_3x3().normalized()
    )

    motion_rotation = (
        COORDINATE_CONVERSION
        @ blender_rotation
        @ COORDINATE_CONVERSION.inverted()
    )

    quaternion = (
        motion_rotation.to_quaternion()
    )

    # MotionAI quaternion format:
    #
    # [w, x, y, z]

    return [
        float(quaternion.w),
        float(quaternion.x),
        float(quaternion.y),
        float(quaternion.z)
    ]


# =========================================================
# EXTRACT ONE FRAME
# =========================================================

def extract_frame(
    armature,
    frame_number,
    start_frame,
    fps
):

    scene = bpy.context.scene

    scene.frame_set(
        frame_number
    )

    bpy.context.view_layer.update()

    joints = {}

    for bone in armature.pose.bones:

        motionai_name = (
            normalize_joint_name(
                bone.name
            )
        )

        # PoseBone.matrix is in armature-object space.
        # Convert it into world space.

        world_matrix = (
            armature.matrix_world
            @ bone.matrix
        )

        position = convert_position(
            world_matrix.translation
        )

        rotation = convert_rotation(
            world_matrix
        )

        joints[motionai_name] = {
            "position": position,
            "rotation": rotation
        }

    timestamp = (
        frame_number - start_frame
    ) / fps

    pelvis = joints.get(
        "pelvis",
        {
            "position": [0.0, 0.0, 0.0],
            "rotation": [1.0, 0.0, 0.0, 0.0]
        }
    )

    return {
        "timestamp": timestamp,

        "root_position": (
            pelvis["position"]
        ),

        "root_rotation": (
            pelvis["rotation"]
        ),

        "joints": joints
    }


# =========================================================
# MAIN CONVERSION
# =========================================================

def main():

    args = parse_arguments()

    input_path = Path(
        args.input
    ).resolve()

    output_path = Path(
        args.output
    ).resolve()

    if not input_path.exists():

        raise FileNotFoundError(
            f"Input FBX not found: {input_path}"
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------------------------------
    # CLEAN + IMPORT
    # -----------------------------------------------------

    clear_scene()

    import_fbx(
        input_path
    )

    # -----------------------------------------------------
    # FIND ROKOKO ARMATURE
    # -----------------------------------------------------

    armature = find_armature()

    print()
    print("Rokoko armature found:")
    print(armature.name)

    print()
    print(
        "Bones:",
        len(armature.pose.bones)
    )

    # -----------------------------------------------------
    # FRAME INFORMATION
    # -----------------------------------------------------

    start_frame, end_frame = (
        get_frame_range(
            armature
        )
    )

    scene = bpy.context.scene

    scene_fps = (
        scene.render.fps
        / scene.render.fps_base
    )

    fps = (
        args.fps
        if args.fps is not None
        else scene_fps
    )

    print()
    print(
        "Frame range:",
        start_frame,
        "->",
        end_frame
    )

    print(
        "FPS:",
        fps
    )

    # -----------------------------------------------------
    # EXTRACT MOTION
    # -----------------------------------------------------

    frames = []

    total_frames = (
        end_frame
        - start_frame
        + 1
    )

    print()
    print(
        "Extracting",
        total_frames,
        "frames..."
    )

    for index, frame_number in enumerate(
        range(
            start_frame,
            end_frame + 1
        )
    ):

        frame_data = extract_frame(
            armature,
            frame_number,
            start_frame,
            fps
        )

        frames.append(
            frame_data
        )

        if index % 50 == 0:

            print(
                f"Processed frame "
                f"{index + 1}/{total_frames}"
            )

    # -----------------------------------------------------
    # BUILD MOTIONAI SESSION
    # -----------------------------------------------------

    session = {
        "session_id": (
            input_path.stem
        ),

        "activity": (
            args.activity
        ),

        "fps": fps,

        "subject_id": (
            args.subject
        ),

        "source": (
            "rokoko_fbx"
        ),

        "metadata": {
            "original_file": (
                input_path.name
            ),

            "armature": (
                armature.name
            ),

            "original_frame_start": (
                start_frame
            ),

            "original_frame_end": (
                end_frame
            ),

            "bone_count": (
                len(armature.pose.bones)
            ),

            "coordinate_system": (
                "MotionAI X=side Y=height Z=forward"
            )
        },

        "frames": frames
    }

    # -----------------------------------------------------
    # WRITE JSON
    # -----------------------------------------------------

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            session,
            file,
            indent=2
        )

    # -----------------------------------------------------
    # COMPLETE
    # -----------------------------------------------------

    print()
    print("=" * 55)
    print("RCON MOTIONAI CONVERSION COMPLETE")
    print("=" * 55)

    print()
    print("Input:")
    print(input_path)

    print()
    print("Output:")
    print(output_path)

    print()
    print(
        "Activity:",
        args.activity
    )

    print(
        "Frames:",
        len(frames)
    )

    print(
        "Bones per frame:",
        len(
            frames[0]["joints"]
        )
    )

    print(
        "FPS:",
        fps
    )

    print()
    print("MotionAI dataset ready.")
    print()


if __name__ == "__main__":
    main()