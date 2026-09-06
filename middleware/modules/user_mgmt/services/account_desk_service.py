from overrides import override

from middleware.adapters.agentic.objects import AgenticAdapterObjectFactory
from middleware.common.pipeline_keys import PIPELINE_ACCOUNT
from middleware.modules.shared.services.interfaces import (
    AccountDeskService,
    PipelineCacheService,
    PreferenceSkillsService,
)
from middleware.modules.shared.services.pipeline_context import menu_context, pipeline_prefs, remember_menu
from middleware.modules.shared.services.service_names import SERVICE_PIPELINE_CACHE, SERVICE_PREFERENCE_SKILLS


class AccountDeskServiceImpl(AccountDeskService):
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
    def lookup(self, user_id: str, preferences: dict, display_name: str = "") -> dict:
        prefs, source, labels = pipeline_prefs(preferences)
        packs = self._preference_skills_service().selected_names(user_id)
        context = menu_context(
            "account",
            prefs,
            source,
            {"display_name": display_name or ""},
            packs=packs,
        )
        result = remember_menu(
            self._cache_service(),
            user_id,
            PIPELINE_ACCOUNT,
            context,
            lambda: AgenticAdapterObjectFactory.account_desk(
                user_id, prefs, source, display_name
            ),
        )
        result["places_source"] = source
        result["places"] = result.get("places") or labels
        return result
