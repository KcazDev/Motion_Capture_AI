import subprocess


class VoiceFeedback:

    def __init__(
        self,
        enabled=True,
        rate=0,
        volume=100
    ):
        self.enabled = enabled
        self.rate = rate
        self.volume = volume
        self.closed = False

    def say(
        self,
        message,
        clear_existing=False
    ):

        if not self.enabled:
            return

        if self.closed:
            return

        if not message:
            return

        message = str(message)

        print(
            "VOICE:",
            message
        )

        safe_message = (
            message.replace(
                "'",
                "''"
            )
        )

        command = (
            "Add-Type -AssemblyName System.Speech; "
            "$voice = New-Object "
            "System.Speech.Synthesis.SpeechSynthesizer; "
            f"$voice.Rate = {self.rate}; "
            f"$voice.Volume = {self.volume}; "
            f"$voice.Speak('{safe_message}'); "
            "$voice.Dispose();"
        )

        result = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-Command",
                command
            ],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:

            print(
                "VOICE ERROR:"
            )

            print(
                result.stderr
            )

    def announce_ready(self):

        self.say(
            (
                "Calibration complete. "
                "Motion AI is ready. "
                "Begin your lift when you are ready."
            )
        )

    def announce_assessment(
        self,
        assessment,
        lift_number
    ):

        if not assessment:
            return

        result = assessment.get(
            "result",
            "RETRY"
        )

        score = assessment.get(
            "overall_score",
            0
        )

        reasons = assessment.get(
            "reasons",
            []
        )

        strengths = assessment.get(
            "strengths",
            []
        )

        if result == "PASS":

            message = (
                f"Lift {lift_number}. "
                f"Pass. "
                f"Your movement score is "
                f"{score:.0f} out of 100."
            )

            if strengths:

                message += (
                    " "
                    + " ".join(
                        strengths[:2]
                    )
                )

        elif result == "FAIL":

            message = (
                f"Lift {lift_number}. "
                f"Fail. "
                f"Your movement score is "
                f"{score:.0f} out of 100."
            )

            if reasons:

                message += (
                    " "
                    + " ".join(
                        reasons[:2]
                    )
                )

        else:

            message = (
                f"Lift {lift_number}. "
                "Please retry the lift."
            )

            if reasons:

                message += (
                    " "
                    + reasons[0]
                )

        self.say(
            message
        )

    def close(self):
        self.closed = True

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback
    ):
        self.close()
        return False