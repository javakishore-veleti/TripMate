from overrides import override

from middleware.modules.preferences_mgmt.persistence.store import selected_skill_names
from middleware.modules.shared.services.interfaces import PreferenceSkillsService


class PreferenceSkillsServiceImpl(PreferenceSkillsService):
    @override
    def selected_names(self, user_id: str) -> list[str]:
        return selected_skill_names(user_id)
