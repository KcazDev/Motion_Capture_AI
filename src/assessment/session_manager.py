from collections import Counter


class AssessmentSession:
    """
    Controls the five-box MotionAI assessment.

    PASS and FAIL complete a box.
    RETRY keeps the participant on the same box.
    """

    def __init__(
        self,
        total_boxes=5
    ):
        self.total_boxes = total_boxes

        self.results = []

        self.current_box = 1

        self.is_complete = False

        self.last_result = None

    # =====================================================
    # RECORD ASSESSMENT
    # =====================================================

    def record_assessment(
        self,
        assessment
    ):

        if assessment is None:
            return None

        if self.is_complete:
            return None

        result = assessment.get(
            "result",
            "RETRY"
        )

        # ---------------------------------------------
        # RETRY DOES NOT ADVANCE BOX
        # ---------------------------------------------

        if result == "RETRY":

            self.last_result = {
                "box_number": self.current_box,
                "assessment": assessment,
                "advanced": False,
            }

            return self.last_result

        # ---------------------------------------------
        # SAVE VALID ASSESSMENT
        # ---------------------------------------------

        entry = {
            "box_number": self.current_box,

            "result": result,

            "score": assessment.get(
                "overall_score",
                0.0
            ),

            "reasons": assessment.get(
                "reasons",
                []
            ),

            "strengths": assessment.get(
                "strengths",
                []
            ),

            "assessment": assessment,
        }

        self.results.append(
            entry
        )

        self.last_result = {
            "box_number": self.current_box,
            "assessment": assessment,
            "advanced": True,
        }

        # ---------------------------------------------
        # SESSION COMPLETE
        # ---------------------------------------------

        if (
            len(self.results)
            >=
            self.total_boxes
        ):

            self.is_complete = True

        else:

            self.current_box += 1

        return self.last_result

    # =====================================================
    # SUMMARY
    # =====================================================

    def get_summary(
        self
    ):

        pass_count = sum(
            1
            for result in self.results
            if result["result"] == "PASS"
        )

        fail_count = sum(
            1
            for result in self.results
            if result["result"] == "FAIL"
        )

        if self.results:

            average_score = (
                sum(
                    result["score"]
                    for result in self.results
                )
                /
                len(self.results)
            )

        else:

            average_score = 0.0

        # ---------------------------------------------
        # MOST COMMON ISSUE
        # ---------------------------------------------

        all_reasons = []

        for result in self.results:

            all_reasons.extend(
                result.get(
                    "reasons",
                    []
                )
            )

        primary_issue = None

        if all_reasons:

            counts = Counter(
                all_reasons
            )

            primary_issue = (
                counts.most_common(
                    1
                )[0][0]
            )

        return {
            "completed": len(
                self.results
            ),

            "total": self.total_boxes,

            "pass_count": pass_count,

            "fail_count": fail_count,

            "average_score": round(
                average_score,
                1
            ),

            "primary_issue": (
                primary_issue
            ),

            "is_complete": (
                self.is_complete
            ),

            "current_box": (
                self.current_box
            ),

            "results": list(
                self.results
            ),
        }

    # =====================================================
    # RESET
    # =====================================================

    def reset(
        self
    ):

        self.results = []

        self.current_box = 1

        self.is_complete = False

        self.last_result = None