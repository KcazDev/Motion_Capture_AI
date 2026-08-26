from src.adapters.json_adapter import JsonMotionAdapter


def main():

    adapter = JsonMotionAdapter()

    session = adapter.load_session(
        "data/samples/test_motion_001.json"
    )

    print("Adapter:", adapter.name)
    print("Session:", session.session_id)
    print("Activity:", session.activity)
    print("FPS:", session.fps)
    print("Frames:", len(session.frames))

    first_frame = session.frames[0]

    print()
    print("First frame timestamp:")
    print(first_frame.timestamp)

    print()
    print("Available joints:")

    for joint_name in first_frame.joints:
        print("-", joint_name)


if __name__ == "__main__":
    main()