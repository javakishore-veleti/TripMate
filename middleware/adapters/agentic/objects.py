from middleware.adapters.agentic.interfaces import AgenticFrameworkAdapter
from middleware.adapters.agentic.langgraph.dashboard.places_planner.main import run_places_planner
from middleware.adapters.agentic.langgraph.journal.happenings.main import run_journal_happenings
from middleware.adapters.agentic.langgraph.menus.account_desk import run_account_desk
from middleware.adapters.agentic.langgraph.menus.packs_lens import run_packs_lens
from middleware.adapters.agentic.langgraph.menus.plan_desk import run_plan_desk
from middleware.adapters.agentic.langgraph.trip_compose import TripComposeAdapter
from middleware.common.constants.agentic_adapters import AGENTIC_ADAPTER_LANGGRAPH

agentic_adapter_instances = {}
agentic_adapter_names_to_classes = {
    AGENTIC_ADAPTER_LANGGRAPH: TripComposeAdapter,
}


class AgenticAdapterObjectFactory:
    @staticmethod
    def get_agentic_adapter(agentic_adapter_name: str) -> AgenticFrameworkAdapter:
        if agentic_adapter_name not in agentic_adapter_names_to_classes:
            raise ValueError(f"Agentic adapter {agentic_adapter_name} not found")
        if agentic_adapter_name not in agentic_adapter_instances:
            agentic_adapter_instances[agentic_adapter_name] = agentic_adapter_names_to_classes[
                agentic_adapter_name
            ]()
        return agentic_adapter_instances[agentic_adapter_name]

    @staticmethod
    def journal_happenings(
        user_id: str,
        preferences: dict,
        expand: bool = False,
        year: int | None = None,
        month: int | None = None,
    ) -> dict:
        return run_journal_happenings(
            user_id=user_id,
            preferences=preferences,
            expand=expand,
            year=year,
            month=month,
        )

    @staticmethod
    def places_planner(user_id: str, preferences: dict, horizon: str) -> dict:
        return run_places_planner(
            user_id=user_id,
            preferences=preferences,
            horizon=horizon,
        )

    @staticmethod
    def plan_desk(
        user_id: str,
        preferences: dict,
        leftover_line: str = "",
        skill_names: list[str] | None = None,
    ) -> dict:
        return run_plan_desk(
            user_id=user_id,
            preferences=preferences,
            leftover_line=leftover_line,
            skill_names=skill_names,
        )

    @staticmethod
    def packs_lens(
        user_id: str,
        preferences: dict,
        skill_names: list[str] | None = None,
    ) -> dict:
        return run_packs_lens(
            user_id=user_id,
            preferences=preferences,
            skill_names=skill_names,
        )

    @staticmethod
    def account_desk(
        user_id: str,
        preferences: dict,
        places_source: str,
        display_name: str = "",
    ) -> dict:
        return run_account_desk(
            user_id=user_id,
            preferences=preferences,
            places_source=places_source,
            display_name=display_name,
        )
