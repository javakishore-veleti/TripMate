from middleware.core.agents.agent_interfaces import TravelAgent
from middleware.core.agents.agent_names import AGENT_TRAVEL_REQUEST
from middleware.core.agents.impl.travel_req_agent import TravelRequestAgentImpl


agent_instances = {}

agent_names_to_classes = {
    AGENT_TRAVEL_REQUEST: TravelRequestAgentImpl,
}

class AgentsObjectFactory:
    @staticmethod
    def get_agent(agent_name: str) -> TravelAgent:
        if agent_name not in agent_names_to_classes:
            raise ValueError(f"Agent {agent_name} not found")
        if agent_name not in agent_instances:
            agent_instances[agent_name] = agent_names_to_classes[agent_name]()  
        return agent_instances[agent_name]