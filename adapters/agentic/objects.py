from adapters.agentic.interfaces import AgenticFrameworkAdapter
from adapters.agentic.langgraph.travel_planner import TravelPlannerLangGraphAdapter
from common.constants.agentic_adapters import AGENTIC_ADAPTER_LANGGRAPH

agentic_adapter_instances = {}
agentic_adapter_names_to_classes = {
    AGENTIC_ADAPTER_LANGGRAPH: TravelPlannerLangGraphAdapter,
}

class AgenticAdapterObjectFactory:
    @staticmethod
    def get_agentic_adapter(agentic_adapter_name: str) -> AgenticFrameworkAdapter:
        if agentic_adapter_name not in agentic_adapter_names_to_classes:
            raise ValueError(f"Agentic adapter {agentic_adapter_name} not found")
        if agentic_adapter_name not in agentic_adapter_instances:
            agentic_adapter_instances[agentic_adapter_name] = agentic_adapter_names_to_classes[agentic_adapter_name]()
        return agentic_adapter_instances[agentic_adapter_name]