from overrides import override

from middleware.modules.plans_mgmt.workflows.happenings.main import run_journal_happenings
from middleware.core.services.interfaces import JournalHappeningsService


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
        return run_journal_happenings(
            user_id=user_id,
            preferences=preferences,
            expand=expand,
            year=year,
            month=month,
        )
