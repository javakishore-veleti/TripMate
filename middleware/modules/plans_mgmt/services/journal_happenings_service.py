from overrides import override

from middleware.adapters.agentic.objects import AgenticAdapterObjectFactory
from middleware.modules.shared.services.interfaces import JournalHappeningsService


class JournalHappeningsServiceImpl(JournalHappeningsService):
    @override
    def lookup(
        self,
        user_id: str,
        preferences: dict,
        expand: bool = False,
        year: int | None = None,
        month: int | None = None,
    ) -> dict:
        return AgenticAdapterObjectFactory.journal_happenings(
            user_id=user_id,
            preferences=preferences,
            expand=expand,
            year=year,
            month=month,
        )
