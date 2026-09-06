from middleware.modules.plans_mgmt.services.journal_happenings_service import JournalHappeningsServiceImpl
from middleware.modules.plans_mgmt.services.plan_desk_service import PlanDeskServiceImpl
from middleware.modules.plans_mgmt.services.planner_service import TravelPlannerServiceImpl
from middleware.modules.preferences_mgmt.services.packs_lens_service import PacksLensServiceImpl
from middleware.modules.preferences_mgmt.services.preference_skills_service import PreferenceSkillsServiceImpl
from middleware.modules.shared.services.pipeline_cache_service import PipelineCacheServiceImpl
from middleware.modules.shared.services.pipeline_cancel_service import PipelineCancelServiceImpl
from middleware.modules.shared.services.run_trace_service import RunTraceServiceImpl
from middleware.modules.shared.services.service_names import (
    SERVICE_ACCOUNT_DESK,
    SERVICE_AUTH,
    SERVICE_DASHBOARD_PLACES,
    SERVICE_JOURNAL_HAPPENINGS,
    SERVICE_PACKS_LENS,
    SERVICE_PIPELINE_CACHE,
    SERVICE_PIPELINE_CANCEL,
    SERVICE_PLAN_DESK,
    SERVICE_PREFERENCE_SKILLS,
    SERVICE_RUN_TRACE,
    SERVICE_TRAVEL_PLANNER,
)
from middleware.modules.travel_search.services.dashboard_places_service import DashboardPlacesServiceImpl
from middleware.modules.user_mgmt.services.account_desk_service import AccountDeskServiceImpl
from middleware.modules.user_mgmt.services.auth_service import AuthService

service_instances = {}
service_names_to_classes = {
    SERVICE_TRAVEL_PLANNER: TravelPlannerServiceImpl,
    SERVICE_AUTH: AuthService,
    SERVICE_DASHBOARD_PLACES: DashboardPlacesServiceImpl,
    SERVICE_JOURNAL_HAPPENINGS: JournalHappeningsServiceImpl,
    SERVICE_PIPELINE_CACHE: PipelineCacheServiceImpl,
    SERVICE_PLAN_DESK: PlanDeskServiceImpl,
    SERVICE_PACKS_LENS: PacksLensServiceImpl,
    SERVICE_ACCOUNT_DESK: AccountDeskServiceImpl,
    SERVICE_PREFERENCE_SKILLS: PreferenceSkillsServiceImpl,
    SERVICE_RUN_TRACE: RunTraceServiceImpl,
    SERVICE_PIPELINE_CANCEL: PipelineCancelServiceImpl,
}


class ServicesObjectFactory:
    @staticmethod
    def get_service(service_name: str):
        if service_name not in service_names_to_classes:
            raise ValueError(f"Service {service_name} not found")
        if service_name not in service_instances:
            service_instances[service_name] = service_names_to_classes[service_name]()
        return service_instances[service_name]
