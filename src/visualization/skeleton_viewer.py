import json

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button


# ---------------------------------------------------------
# SKELETON CONNECTIONS
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# LOAD MOTION
# ---------------------------------------------------------

def load_motion(path):
    with open(path, "r") as file:
        return json.load(file)


# ---------------------------------------------------------
# DISPLAY HELPERS
# ---------------------------------------------------------

def format_activity(activity):
    return activity.replace("_", " ").title()


def get_motion_phase(timestamp):

    if timestamp < 1.0:
        return "STANDING"

    elif timestamp < 2.0:
        return "SQUATTING / REACHING"

    elif timestamp < 3.2:
        return "LIFTING MATERIAL"

    elif timestamp < 4.2:
        return "MOVING MATERIAL"

    elif timestamp < 5.2:
        return "PLACING MATERIAL"

    else:
        return "RETURNING TO NEUTRAL"


# ---------------------------------------------------------
# MATERIAL BOX
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# TABLE
# ---------------------------------------------------------

def draw_table(ax):

    table_x_start = 0.40
    table_x_end = 1.05

    table_z_start = 0.28
    table_z_end = 0.78

    table_height = 0.82

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


# ---------------------------------------------------------
# GROUND
# ---------------------------------------------------------

def draw_ground(ax):

    ax.plot(
        [-1.0, 1.5],
        [0.0, 0.0],
        [0.0, 0.0],
        linewidth=2
    )


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    motion_path = (
        "data/samples/material_lift_001.json"
    )

    motion = load_motion(
        motion_path
    )

    frames = motion["frames"]
    fps = motion["fps"]

    # -----------------------------------------------------
    # WINDOW
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
        "Construction Human Motion Prototype",
        fontsize=15,
        pad=20
    )

    # -----------------------------------------------------
    # 3D WORLD
    # -----------------------------------------------------

    ax.set_xlim(-1.0, 1.5)
    ax.set_ylim(-0.5, 1.2)
    ax.set_zlim(0.0, 2.2)

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

    draw_ground(ax)
    draw_table(ax)

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

        skeleton_lines.append(line)

    # -----------------------------------------------------
    # MATERIAL
    # -----------------------------------------------------

    box_lines = create_box_lines(
        ax
    )

    # -----------------------------------------------------
    # STATUS
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
    # UPDATE FRAME
    # -----------------------------------------------------

    def update(frame_number):

        playback["frame"] = frame_number

        frame = frames[frame_number]
        joints = frame["joints"]

        timestamp = frame["timestamp"]

        # -------------------------------------------------
        # SKELETON
        # -------------------------------------------------

        for line, (joint_a, joint_b) in zip(
            skeleton_lines,
            BONES
        ):

            if joint_a not in joints:
                continue

            if joint_b not in joints:
                continue

            a = joints[joint_a]["position"]
            b = joints[joint_b]["position"]

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
        # HAND POSITION
        # -------------------------------------------------

        left_wrist = (
            joints["left_wrist"]["position"]
        )

        right_wrist = (
            joints["right_wrist"]["position"]
        )

        average_hand_x = (
            left_wrist[0] +
            right_wrist[0]
        ) / 2

        average_hand_y = (
            left_wrist[1] +
            right_wrist[1]
        ) / 2

        average_hand_z = (
            left_wrist[2] +
            right_wrist[2]
        ) / 2

        # -------------------------------------------------
        # BOX POSITION
        # -------------------------------------------------

        if timestamp < 1.7:

            box_x = 0.0
            box_y = 0.14
            box_z = 0.38

        elif timestamp < 4.6:

            box_x = average_hand_x
            box_y = average_hand_y - 0.10
            box_z = average_hand_z

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
            timestamp
        )

        # -------------------------------------------------
        # STATUS DISPLAY
        # -------------------------------------------------

        status_text.set_text(
            "RCON MotionAI\n"
            "-----------------------------\n"
            f"Task: "
            f"{format_activity(motion['activity'])}\n"
            f"Phase: {phase}\n"
            f"Source: "
            f"{motion['source'].title()} Prototype\n"
            f"Session: {motion['session_id']}\n"
            f"Frame: "
            f"{frame_number + 1} / {len(frames)}\n"
            f"Time: {timestamp:.2f} sec"
        )

        return (
            skeleton_lines +
            box_lines +
            [status_text]
        )

    # -----------------------------------------------------
    # ANIMATION
    # -----------------------------------------------------

    interval_ms = 1000 / fps

    animation = FuncAnimation(
        fig,
        update,
        frames=len(frames),
        interval=interval_ms,
        repeat=True,
        blit=False
    )

    # -----------------------------------------------------
    # BUTTONS
    # -----------------------------------------------------

    play_pause_ax = fig.add_axes(
        [0.40, 0.05, 0.12, 0.055]
    )

    restart_ax = fig.add_axes(
        [0.54, 0.05, 0.12, 0.055]
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

    def toggle_playback(event):

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

    def restart_animation(event):

        # Reset FuncAnimation sequence
        animation.frame_seq = (
            animation.new_frame_seq()
        )

        playback["frame"] = 0

        # Immediately redraw frame zero
        update(0)

        fig.canvas.draw_idle()

        # If animation is currently playing,
        # restart its timer as well.
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
    # KEYBOARD SHORTCUT
    # -----------------------------------------------------

    def keyboard_controls(event):

        # Space = Play/Pause
        if event.key == " ":
            toggle_playback(event)

        # R = Restart
        elif event.key.lower() == "r":
            restart_animation(event)

    fig.canvas.mpl_connect(
        "key_press_event",
        keyboard_controls
    )

    # Keep enough space for controls
    plt.subplots_adjust(
        left=0.08,
        right=0.95,
        top=0.88,
        bottom=0.24
    )

    plt.show()


# ---------------------------------------------------------
# START
# ---------------------------------------------------------

if __name__ == "__main__":
    main()