import unittest

from middleware.adapters.agentic.langgraph.routes import (
    route_after_draft,
    route_after_intake,
    route_from_coordinator,
)
from middleware.adapters.agentic.langgraph.runtime import (
    DEFAULT_MAX_STEPS,
    STEP_HALTED,
    normalize_constraints,
    with_runtime,
)
from middleware.adapters.agentic.langgraph.specialists.ids import (
    COORDINATOR,
    HALT,
    REQUEST_DECLINED,
    TRAVELER_REVIEW,
    TRIP_DRAFT,
)


class RouteTests(unittest.TestCase):
    def test_intake_declines_unrelated_asks(self):
        self.assertEqual(
            route_after_intake({"request_accepted": False}),
            REQUEST_DECLINED,
        )
        self.assertEqual(route_after_intake({"request_accepted": True}), COORDINATOR)

    def test_halted_state_leaves_the_cycle(self):
        halted = {"current_step": STEP_HALTED}
        self.assertEqual(route_after_intake(halted), HALT)
        self.assertEqual(route_from_coordinator(halted), HALT)
        self.assertEqual(route_after_draft(halted), HALT)

    def test_draft_goes_to_review(self):
        self.assertEqual(route_after_draft({}), TRAVELER_REVIEW)

    def test_coordinator_uses_selected_specialists(self):
        self.assertEqual(
            route_from_coordinator({"selected_specialists": [TRIP_DRAFT]}),
            TRIP_DRAFT,
        )

    def test_constraints_stay_typed(self):
        cleaned = normalize_constraints(
            {"destination": "  Orlando ", "special_preferences": ["kids", 3], "extra": "drop"}
        )
        self.assertEqual(cleaned["destination"], "Orlando")
        self.assertEqual(cleaned["special_preferences"], ["kids", "3"])
        self.assertIn("start_date", cleaned)
        self.assertNotIn("extra", cleaned)

    def test_runtime_wrapper_bounds_steps(self):
        def boom(_state):
            raise RuntimeError("nope")

        guarded = with_runtime("air_research", boom)
        failed = guarded({"step_count": 0, "error_count": 0, "max_steps": DEFAULT_MAX_STEPS})
        self.assertEqual(failed["current_step"], "error")
        self.assertEqual(failed["error_count"], 1)

        halted = guarded({"step_count": DEFAULT_MAX_STEPS, "max_steps": DEFAULT_MAX_STEPS})
        self.assertEqual(halted["current_step"], STEP_HALTED)


if __name__ == "__main__":
    unittest.main()
