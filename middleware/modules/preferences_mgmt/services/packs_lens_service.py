from overrides import override

from middleware.adapters.agentic.objects import AgenticAdapterObjectFactory
from middleware.common.pipeline_keys import PIPELINE_PREFERENCES
from middleware.modules.shared.services.interfaces import (
    PacksLensService,
    PipelineCacheService,
    PreferenceSkillsService,
)
from middleware.modules.shared.services.pipeline_context import menu_context, pipeline_prefs, remember_menu
from middleware.modules.shared.services.service_names import SERVICE_PIPELINE_CACHE, SERVICE_PREFERENCE_SKILLS


class PacksLensServiceImpl(PacksLensService):
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
    def lookup(self, user_id: str, preferences: dict) -> dict:
        prefs, source, labels = pipeline_prefs(preferences)
        packs = self._preference_skills_service().selected_names(user_id)
        context = menu_context("preferences", prefs, source, packs=packs)
        result = remember_menu(
            self._cache_service(),
            user_id,
            PIPELINE_PREFERENCES,
            context,
            lambda: AgenticAdapterObjectFactory.packs_lens(user_id, prefs, packs),
        )
        result["places_source"] = source
        result["places"] = result.get("places") or labels
        return result
