from overrides import override

from middleware.adapters.agentic.objects import AgenticAdapterObjectFactory
from middleware.common.pipeline_keys import PIPELINE_PLAN
from middleware.modules.plans_mgmt.persistence.interfaces import TravelRequestDao
from middleware.modules.shared.persistence.dao.dao_names import DAO_TRAVEL_REQUEST
from middleware.modules.shared.persistence.dao.objects import DaoObjectFactory
from middleware.modules.shared.services.interfaces import (
    PipelineCacheService,
    PlanDeskService,
    PreferenceSkillsService,
)
from middleware.modules.shared.services.pipeline_context import menu_context, pipeline_prefs, remember_menu
from middleware.modules.shared.services.service_names import SERVICE_PIPELINE_CACHE, SERVICE_PREFERENCE_SKILLS


class PlanDeskServiceImpl(PlanDeskService):
    def __init__(
        self,
        cache: PipelineCacheService | None = None,
        travel_requests: TravelRequestDao | None = None,
        preference_skills: PreferenceSkillsService | None = None,
    ):
        self._cache = cache
        self._travel_requests = travel_requests
        self._preference_skills = preference_skills

    def _cache_service(self) -> PipelineCacheService:
        if self._cache is not None:
            return self._cache
        from middleware.modules.shared.services.objects import ServicesObjectFactory

        return ServicesObjectFactory.get_service(SERVICE_PIPELINE_CACHE)

    def _travel_request_dao(self) -> TravelRequestDao:
        if self._travel_requests is not None:
            return self._travel_requests
        return DaoObjectFactory.get_dao(DAO_TRAVEL_REQUEST)

    def _preference_skills_service(self) -> PreferenceSkillsService:
        if self._preference_skills is not None:
            return self._preference_skills
        from middleware.modules.shared.services.objects import ServicesObjectFactory

        return ServicesObjectFactory.get_service(SERVICE_PREFERENCE_SKILLS)

    @override
    def lookup(self, user_id: str, preferences: dict) -> dict:
        prefs, source, labels = pipeline_prefs(preferences)
        records = self._travel_request_dao().list_for_user(user_id)
        leftover = next(
            (row for row in records if row.get("status") == "awaiting_approval"),
            records[0] if records else None,
        )
        leftover_line = str((leftover or {}).get("prompt") or "").strip()
        packs = self._preference_skills_service().selected_names(user_id)
        context = menu_context(
            "plan",
            prefs,
            source,
            {"leftover": leftover_line},
            packs=packs,
        )
        result = remember_menu(
            self._cache_service(),
            user_id,
            PIPELINE_PLAN,
            context,
            lambda: AgenticAdapterObjectFactory.plan_desk(
                user_id, prefs, leftover_line, packs
            ),
        )
        result["places_source"] = source
        result["places"] = result.get("places") or labels
        return result
