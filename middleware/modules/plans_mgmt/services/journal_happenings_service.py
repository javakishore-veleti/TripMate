from datetime import date

from overrides import override

from middleware.adapters.agentic.objects import AgenticAdapterObjectFactory
from middleware.common.pipeline_keys import PIPELINE_JOURNAL
from middleware.common.popular_events import attach_nearby_events
from middleware.modules.shared.services.interfaces import (
    JournalHappeningsService,
    PipelineCacheService,
    PreferenceSkillsService,
)
from middleware.modules.shared.services.pipeline_context import menu_context, pipeline_prefs, remember_menu
from middleware.modules.shared.services.service_names import SERVICE_PIPELINE_CACHE, SERVICE_PREFERENCE_SKILLS

_ACTION_NOTE = "Go find a spark near your cities."


def _customer_note(raw) -> str:
    note = " ".join(str(raw or "").split()).strip()
    lowered = note.lower()
    if (
        not note
        or "one short sentence" in lowered
        or "what to look for" in lowered
        or "return json" in lowered
    ):
        return _ACTION_NOTE
    return note


class JournalHappeningsServiceImpl(JournalHappeningsService):
    def __init__(
        self,
        cache: PipelineCacheService | None = None,
        preference_skills: PreferenceSkillsService | None = None,
    ):
        self._cache = cache
        self._preference_skills = preference_skills

    def _cache_service(self) -> PipelineCacheService:
        if self._cache is not None:
            return self._cache
        from middleware.modules.shared.services.objects import ServicesObjectFactory

        return ServicesObjectFactory.get_service(SERVICE_PIPELINE_CACHE)

    def _preference_skills_service(self) -> PreferenceSkillsService:
        if self._preference_skills is not None:
            return self._preference_skills
        from middleware.modules.shared.services.objects import ServicesObjectFactory

        return ServicesObjectFactory.get_service(SERVICE_PREFERENCE_SKILLS)

    @override
    def lookup(
        self,
        user_id: str,
        preferences: dict,
        expand: bool = False,
        year: int | None = None,
        month: int | None = None,
    ) -> dict:
        prefs, source, labels = pipeline_prefs(preferences)
        packs = self._preference_skills_service().selected_names(user_id)
        context = menu_context(
            "journal",
            prefs,
            source,
            {"expand": bool(expand), "year": year or 0, "month": month or 0, "limit": 20},
            packs=packs,
        )
        result = remember_menu(
            self._cache_service(),
            user_id,
            PIPELINE_JOURNAL,
            context,
            lambda: AgenticAdapterObjectFactory.journal_happenings(
                user_id=user_id,
                preferences=prefs,
                expand=expand,
                year=year,
                month=month,
            ),
        )
        today = date.today()
        result = attach_nearby_events(
            result,
            labels,
            month or today.month,
            20,
        )
        result["places_source"] = source
        result["places"] = result.get("places") or labels
        result["classify_note"] = _customer_note(result.get("classify_note"))
        return result
