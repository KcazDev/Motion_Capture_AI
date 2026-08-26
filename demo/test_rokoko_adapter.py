from src.adapters.rokoko_adapter import RokokoAdapter


def main():

    adapter = RokokoAdapter()

    print()
    print("RCON MotionAI")
    print("-----------------------------")

    print("Adapter:")
    print(adapter.name)

    print()
    print("Live streaming:")
    print(adapter.supports_live_stream())

    print()
    print("Current status:")

    for key, value in adapter.status().items():
        print(f"{key}: {value}")

    print()
    print("Joint normalization test:")

    test_joints = [
        "Hips",
        "Spine",
        "LeftForeArm",
        "RightHand",
        "LeftUpLeg",
        "RightFoot"
    ]

    for joint in test_joints:

        normalized = adapter.normalize_joint_name(
            joint
        )

        print(
            f"{joint} -> {normalized}"
        )


if __name__ == "__main__":
    main()