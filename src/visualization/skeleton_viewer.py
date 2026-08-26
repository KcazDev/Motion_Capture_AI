import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button


# =========================================================
# SKELETON DEFINITION
# =========================================================

BONES = [
    ("pelvis", "spine"),
    ("spine", "neck"),
    ("neck", "head"),

    ("neck", "left_shoulder"),
    ("left_shoulder", "left_elbow"),
    ("left_elbow", "left_wrist"),

    ("neck", "right_shoulder"),
    ("right_shoulder", "right_elbow"),
    ("right_elbow", "right_wrist"),

    ("pelvis", "left_hip"),
    ("left_hip", "left_knee"),
    ("left_knee", "left_ankle"),

    ("pelvis", "right_hip"),
    ("right_hip", "right_knee"),
    ("right_knee", "right_ankle"),
]


# =========================================================
# COMMAND-LINE INPUT
# =========================================================

def parse_arguments():
    """
    Allows a MotionAI JSON file to be supplied from the command line.

    Example:

    python -m src.visualization.skeleton_viewer \
        data/samples/material_lift_001.json
    """

    parser = argparse.ArgumentParser(
        description="RCON MotionAI 3D Motion Viewer"
    )

    parser.add_argument(
        "motion_file",
        nargs="?",
        default="data/samples/material_lift_001.json",
        help="Path to a MotionAI JSON motion file"
    )

    return parser.parse_args()


# =========================================================
# MOTION LOADING
# =========================================================

def load_motion(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


# =========================================================
# DISPLAY HELPERS
# =========================================================

def format_activity(activity):
    return activity.replace("_", " ").title()


def is_construction_lift(activity):
    return activity == "ground_to_table_lift"


def get_motion_phase(activity, timestamp):
    """
    Provides detailed phases for the construction lift.

    Other motion types use a generic playback state.
    """

    if activity != "ground_to_table_lift":
        return "MOTION PLAYBACK"

    if timestamp < 1.0:
        return "STANDING"

    if timestamp < 2.0:
        return "SQUATTING / REACHING"

    if timestamp < 3.2:
        return "LIFTING MATERIAL"

    if timestamp < 4.2:
        return "MOVING MATERIAL"

    if timestamp < 5.2:
        return "PLACING MATERIAL"

    return "RETURNING TO NEUTRAL"


# =========================================================
# MATERIAL BOX
# =========================================================

def create_box_lines(ax):
    lines = []

    for _ in range(12):
        line, = ax.plot(
            [],
            [],
            [],
            linewidth=2
        )

        lines.append(line)

    return lines


def update_box(
    box_lines,
    center_x,
    center_y,
    center_z
):

    width = 0.30
    depth = 0.22
    height = 0.20

    x0 = center_x - width / 2
    x1 = center_x + width / 2

    z0 = center_z - depth / 2
    z1 = center_z + depth / 2

    y0 = center_y - height / 2
    y1 = center_y + height / 2

    corners = [
        (x0, z0, y0),
        (x1, z0, y0),
        (x1, z1, y0),
        (x0, z1, y0),

        (x0, z0, y1),
        (x1, z0, y1),
        (x1, z1, y1),
        (x0, z1, y1),
    ]

    edges = [
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 0),

        (4, 5),
        (5, 6),
        (6, 7),
        (7, 4),

        (0, 4),
        (1, 5),
        (2, 6),
        (3, 7),
    ]

    for line, (start, end) in zip(
        box_lines,
        edges
    ):

        a = corners[start]
        b = corners[end]

        line.set_data(
            [a[0], b[0]],
            [a[1], b[1]]
        )

        line.set_3d_properties(
            [a[2], b[2]]
        )


def hide_box(box_lines):
    for line in box_lines:

        line.set_data(
            [],
            []
        )

        line.set_3d_properties(
            []
        )


# =========================================================
# CONSTRUCTION ENVIRONMENT
# =========================================================

def draw_ground(ax):

    ax.plot(
        [-1.0, 1.5],
        [0.0, 0.0],
        [0.0, 0.0],
        linewidth=2
    )


def draw_table(ax):

    table_x_start = 0.40
    table_x_end = 1.05

    table_z_start = 0.28
    table_z_end = 0.78

    table_height = 0.82

    # Table top
    surface_x = [
        table_x_start,
        table_x_end,
        table_x_end,
        table_x_start,
        table_x_start
    ]

    surface_y = [
        table_z_start,
        table_z_start,
        table_z_end,
        table_z_end,
        table_z_start
    ]

    surface_z = [
        table_height,
        table_height,
        table_height,
        table_height,
        table_height
    ]

    ax.plot(
        surface_x,
        surface_y,
        surface_z,
        linewidth=3
    )

    # Table legs
    leg_positions = [
        (table_x_start, table_z_start),
        (table_x_end, table_z_start),
        (table_x_start, table_z_end),
        (table_x_end, table_z_end),
    ]

    for x, z in leg_positions:

        ax.plot(
            [x, x],
            [z, z],
            [0.0, table_height],
            linewidth=2
        )


# =========================================================
# MAIN VIEWER
# =========================================================

def main():

    # -----------------------------------------------------
    # READ COMMAND-LINE ARGUMENT
    # -----------------------------------------------------

    args = parse_arguments()

    motion_path = Path(
        args.motion_file
    )

    # -----------------------------------------------------
    # VALIDATE FILE
    # -----------------------------------------------------

    if not motion_path.exists():

        print()
        print("RCON MotionAI")
        print("-----------------------------")
        print("ERROR: Motion file not found.")
        print()
        print("Requested file:")
        print(motion_path)
        print()

        return

    if motion_path.suffix.lower() != ".json":

        print()
        print("RCON MotionAI")
        print("-----------------------------")
        print(
            "ERROR: Viewer currently expects "
            "a MotionAI JSON file."
        )
        print()
        print("Requested file:")
        print(motion_path)
        print()

        return

    # -----------------------------------------------------
    # LOAD MOTION
    # -----------------------------------------------------

    try:

        motion = load_motion(
            motion_path
        )

    except json.JSONDecodeError as error:

        print()
        print("RCON MotionAI")
        print("-----------------------------")
        print("ERROR: Invalid JSON file.")
        print(error)
        print()

        return

    # -----------------------------------------------------
    # VALIDATE MOTION DATA
    # -----------------------------------------------------

    frames = motion.get(
        "frames",
        []
    )

    if not frames:

        print()
        print("RCON MotionAI")
        print("-----------------------------")
        print("ERROR: Motion file contains no frames.")
        print()

        return

    fps = motion.get(
        "fps",
        60
    )

    activity = motion.get(
        "activity",
        "unknown_motion"
    )

    session_id = motion.get(
        "session_id",
        "unknown_session"
    )

    source = motion.get(
        "source",
        "unknown"
    )

    construction_demo = is_construction_lift(
        activity
    )

    print()
    print("RCON MotionAI")
    print("-----------------------------")
    print("Loading motion:")
    print(motion_path)
    print()
    print("Session:", session_id)
    print(
        "Activity:",
        format_activity(activity)
    )
    print(
        "Frames:",
        len(frames)
    )
    print(
        "FPS:",
        fps
    )
    print()

    # -----------------------------------------------------
    # CREATE WINDOW
    # -----------------------------------------------------

    fig = plt.figure(
        figsize=(11, 8)
    )

    ax = fig.add_subplot(
        111,
        projection="3d"
    )

    fig.canvas.manager.set_window_title(
        "RCON MotionAI"
    )

    # -----------------------------------------------------
    # TITLE
    # -----------------------------------------------------

    ax.set_title(
        "RCON MotionAI\n"
        "Human Motion Visualization Prototype",
        fontsize=15,
        pad=20
    )

    # -----------------------------------------------------
    # 3D WORLD
    # -----------------------------------------------------

    ax.set_xlim(
        -1.0,
        1.5
    )

    ax.set_ylim(
        -0.5,
        1.2
    )

    ax.set_zlim(
        0.0,
        2.2
    )

    ax.set_xlabel(
        "X - Side Movement"
    )

    ax.set_ylabel(
        "Z - Forward Movement"
    )

    ax.set_zlabel(
        "Y - Height"
    )

    ax.view_init(
        elev=20,
        azim=-60
    )

    # -----------------------------------------------------
    # ENVIRONMENT
    # -----------------------------------------------------

    draw_ground(
        ax
    )

    if construction_demo:
        draw_table(
            ax
        )

    # -----------------------------------------------------
    # SKELETON
    # -----------------------------------------------------

    skeleton_lines = []

    for _ in BONES:

        line, = ax.plot(
            [],
            [],
            [],
            marker="o",
            linewidth=3,
            markersize=5
        )

        skeleton_lines.append(
            line
        )

    # -----------------------------------------------------
    # MATERIAL BOX
    # -----------------------------------------------------

    box_lines = create_box_lines(
        ax
    )

    if not construction_demo:
        hide_box(
            box_lines
        )

    # -----------------------------------------------------
    # STATUS DISPLAY
    # -----------------------------------------------------

    status_text = fig.text(
        0.03,
        0.03,
        "",
        fontsize=10,
        verticalalignment="bottom"
    )

    # -----------------------------------------------------
    # PLAYBACK STATE
    # -----------------------------------------------------

    playback = {
        "paused": False,
        "frame": 0
    }

    # -----------------------------------------------------
    # UPDATE ANIMATION
    # -----------------------------------------------------

    def update(frame_number):

        playback["frame"] = frame_number

        frame = frames[
            frame_number
        ]

        joints = frame.get(
            "joints",
            {}
        )

        timestamp = frame.get(
            "timestamp",
            frame_number / fps
        )

        # -------------------------------------------------
        # UPDATE SKELETON
        # -------------------------------------------------

        for line, (joint_a, joint_b) in zip(
            skeleton_lines,
            BONES
        ):

            if joint_a not in joints:
                continue

            if joint_b not in joints:
                continue

            a = joints[
                joint_a
            ]["position"]

            b = joints[
                joint_b
            ]["position"]

            # MotionAI coordinates:
            #
            # [x, y, z]
            #
            # x = left / right
            # y = vertical height
            # z = forward / backward
            #
            # Matplotlib:
            #
            # display X = x
            # display Y = z
            # display Z = y

            xs = [
                a[0],
                b[0]
            ]

            ys = [
                a[2],
                b[2]
            ]

            zs = [
                a[1],
                b[1]
            ]

            line.set_data(
                xs,
                ys
            )

            line.set_3d_properties(
                zs
            )

        # -------------------------------------------------
        # CONSTRUCTION MATERIAL
        # -------------------------------------------------

        if (
            construction_demo
            and "left_wrist" in joints
            and "right_wrist" in joints
        ):

            left_wrist = joints[
                "left_wrist"
            ]["position"]

            right_wrist = joints[
                "right_wrist"
            ]["position"]

            average_hand_x = (
                left_wrist[0]
                + right_wrist[0]
            ) / 2

            average_hand_y = (
                left_wrist[1]
                + right_wrist[1]
            ) / 2

            average_hand_z = (
                left_wrist[2]
                + right_wrist[2]
            ) / 2

            # Material starts on ground
            if timestamp < 1.7:

                box_x = 0.0
                box_y = 0.14
                box_z = 0.38

            # Material follows hands
            elif timestamp < 4.6:

                box_x = average_hand_x
                box_y = average_hand_y - 0.10
                box_z = average_hand_z

            # Material placement
            elif timestamp < 5.2:

                box_x = average_hand_x

                box_y = max(
                    average_hand_y - 0.10,
                    0.94
                )

                box_z = max(
                    average_hand_z,
                    0.52
                )

            # Material remains on table
            else:

                box_x = 0.72
                box_y = 0.94
                box_z = 0.52

            update_box(
                box_lines,
                box_x,
                box_y,
                box_z
            )

        # -------------------------------------------------
        # MOTION PHASE
        # -------------------------------------------------

        phase = get_motion_phase(
            activity,
            timestamp
        )

        # -------------------------------------------------
        # STATUS
        # -------------------------------------------------

        status_text.set_text(
            "RCON MotionAI\n"
            "-----------------------------\n"
            f"Task: {format_activity(activity)}\n"
            f"Phase: {phase}\n"
            f"Source: {source.title()}\n"
            f"Session: {session_id}\n"
            f"Frame: {frame_number + 1} / {len(frames)}\n"
            f"Time: {timestamp:.2f} sec"
        )

        return (
            skeleton_lines
            + box_lines
            + [status_text]
        )

    # -----------------------------------------------------
    # ANIMATION
    # -----------------------------------------------------

    interval_ms = (
        1000 / fps
    )

    animation = FuncAnimation(
        fig,
        update,
        frames=len(frames),
        interval=interval_ms,
        repeat=True,
        blit=False
    )

    # -----------------------------------------------------
    # BUTTON AREA
    # -----------------------------------------------------

    play_pause_ax = fig.add_axes(
        [
            0.40,
            0.05,
            0.12,
            0.055
        ]
    )

    restart_ax = fig.add_axes(
        [
            0.54,
            0.05,
            0.12,
            0.055
        ]
    )

    play_pause_button = Button(
        play_pause_ax,
        "Pause"
    )

    restart_button = Button(
        restart_ax,
        "Restart"
    )

    # -----------------------------------------------------
    # PLAY / PAUSE
    # -----------------------------------------------------

    def toggle_playback(event=None):

        if playback["paused"]:

            animation.event_source.start()

            playback["paused"] = False

            play_pause_button.label.set_text(
                "Pause"
            )

        else:

            animation.event_source.stop()

            playback["paused"] = True

            play_pause_button.label.set_text(
                "Play"
            )

        fig.canvas.draw_idle()

    # -----------------------------------------------------
    # RESTART
    # -----------------------------------------------------

    def restart_animation(event=None):

        animation.frame_seq = (
            animation.new_frame_seq()
        )

        playback["frame"] = 0

        update(
            0
        )

        fig.canvas.draw_idle()

        if not playback["paused"]:

            animation.event_source.stop()
            animation.event_source.start()

    # -----------------------------------------------------
    # BUTTON EVENTS
    # -----------------------------------------------------

    play_pause_button.on_clicked(
        toggle_playback
    )

    restart_button.on_clicked(
        restart_animation
    )

    # -----------------------------------------------------
    # KEYBOARD CONTROLS
    # -----------------------------------------------------

    def keyboard_controls(event):

        if event.key == " ":

            toggle_playback()

        elif (
            event.key
            and event.key.lower() == "r"
        ):

            restart_animation()

    fig.canvas.mpl_connect(
        "key_press_event",
        keyboard_controls
    )

    # -----------------------------------------------------
    # DISPLAY
    # -----------------------------------------------------

    plt.subplots_adjust(
        left=0.08,
        right=0.95,
        top=0.88,
        bottom=0.24
    )

    plt.show()


# =========================================================
# START PROGRAM
# =========================================================

if __name__ == "__main__":
    main()