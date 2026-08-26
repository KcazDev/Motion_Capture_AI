import json
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


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
# LOAD MOTION FILE
# ---------------------------------------------------------

def load_motion(path):
    with open(path, "r") as file:
        return json.load(file)


# ---------------------------------------------------------
# FORMAT ACTIVITY NAME
# ---------------------------------------------------------

def format_activity(activity):
    """
    Converts:
        ground_to_table_lift

    Into:
        Ground To Table Lift
    """

    return activity.replace("_", " ").title()


# ---------------------------------------------------------
# MOTION PHASE
# ---------------------------------------------------------

def get_motion_phase(timestamp):
    """
    Determine which stage of the construction
    movement is currently occurring.
    """

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
# MAIN VIEWER
# ---------------------------------------------------------

def main():

    # Current demo motion
    motion_path = "data/samples/material_lift_001.json"

    motion = load_motion(motion_path)

    frames = motion["frames"]
    fps = motion["fps"]

    # -----------------------------------------------------
    # CREATE WINDOW
    # -----------------------------------------------------

    fig = plt.figure(figsize=(10, 8))

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
    ax.set_ylim(-0.5, 1.0)
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

    # Initial camera position
    ax.view_init(
        elev=18,
        azim=-65
    )

    # -----------------------------------------------------
    # CREATE SKELETON BONES
    # -----------------------------------------------------

    lines = []

    for _ in BONES:

        line, = ax.plot(
            [],
            [],
            [],
            marker="o",
            linewidth=3,
            markersize=5
        )

        lines.append(line)

    # -----------------------------------------------------
    # INFORMATION DISPLAY
    # -----------------------------------------------------

    status_text = fig.text(
        0.03,
        0.03,
        "",
        fontsize=10,
        verticalalignment="bottom"
    )

    # -----------------------------------------------------
    # UPDATE EACH FRAME
    # -----------------------------------------------------

    def update(frame_number):

        frame = frames[frame_number]

        joints = frame["joints"]

        # Update each skeleton bone
        for line, (joint_a, joint_b) in zip(
            lines,
            BONES
        ):

            if joint_a not in joints:
                continue

            if joint_b not in joints:
                continue

            a = joints[joint_a]["position"]
            b = joints[joint_b]["position"]

            # -------------------------------------------------
            # MotionAI stores:
            #
            # [x, y, z]
            #
            # x = left/right
            # y = vertical
            # z = forward/backward
            #
            # Matplotlib wants:
            #
            # X
            # Y
            # Z
            #
            # So we remap:
            #
            # display X = motion X
            # display Y = motion Z
            # display Z = motion Y
            # -------------------------------------------------

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
        # DETERMINE CURRENT MOTION PHASE
        # -------------------------------------------------

        phase = get_motion_phase(
            frame["timestamp"]
        )

        # -------------------------------------------------
        # UPDATE INFORMATION
        # -------------------------------------------------

        status_text.set_text(
            "RCON MotionAI\n"
            "-----------------------------\n"
            f"Task: {format_activity(motion['activity'])}\n"
            f"Phase: {phase}\n"
            f"Source: {motion['source'].title()} Prototype\n"
            f"Session: {motion['session_id']}\n"
            f"Frame: {frame_number + 1} / {len(frames)}\n"
            f"Time: {frame['timestamp']:.2f} sec"
        )

        return lines + [status_text]

    # -----------------------------------------------------
    # ANIMATION SPEED
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

    # Prevent matplotlib from deleting animation reference
    _ = animation

    # Leave room for status information
    plt.subplots_adjust(
        left=0.08,
        right=0.95,
        top=0.88,
        bottom=0.22
    )

    # -----------------------------------------------------
    # SHOW VIEWER
    # -----------------------------------------------------

    plt.show()


# ---------------------------------------------------------
# START PROGRAM
# ---------------------------------------------------------

if __name__ == "__main__":
    main()