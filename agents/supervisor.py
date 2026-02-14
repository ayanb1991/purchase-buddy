import json
from models.state import PurchaseState
from langchain_openai import AzureChatOpenAI
from langchain.messages import HumanMessage, SystemMessage, AIMessage
from config import azure_openai_api_key, azure_openai_endpoint, azure_openai_deployment, azure_openai_api_version

# initialize LangChain LLM with Azure OpenAI
llm = AzureChatOpenAI(
    openai_api_key=azure_openai_api_key,
    azure_endpoint=azure_openai_endpoint,
    deployment_name=azure_openai_deployment,
    openai_api_version=azure_openai_api_version,
    temperature=0
)

def supervisor_agent(state: PurchaseState) -> PurchaseState:

    messages = state.get("messages", [])
    current_user_input = ""
    if messages:
        # get the last user message
        lastMessage = messages[-1]
        current_user_input = lastMessage.content if isinstance(lastMessage, HumanMessage) else ""
    
    print(f"Current user input: {current_user_input}")


    # create state representation for LLM
    currentState = {
        "isAddressProvided": bool(state.get("user_pincode", "")),
        "hasParsedItems": bool(state.get("parsed_items", [])),
        "hasSelectedProvider": bool(state.get("selected_provider", "")),
        "hasProviderResults": bool(state.get("provider_results", {})),
        "isOrderFinalized": bool(state.get("final_order", {})),
    }
    
    systemMsg = SystemMessage(f"""
    You are a supervisor agent overseeing the entire purchase process. Your responsibility is to 
    route the flow based on the current state and outputs of each agent.(intent parser, purchase agent, billing agent)
    - If the intent parser has not yet extracted items, or address is not provided, route to intent_parser.
    - If items are parsed but providers are not yet selected, route to purchase_agent.
    - If providers are selected but order is not finalized, route to billing_agent.
    - If at any point the state is ambiguous or if there are errors in agent outputs, ask for human input by routing to human_input.
    - Respond in JSON format strictly with the following structure:
        {{
            "next_agent": <agent name to route to: intent_parser|purchase_agent|billing_agent|human_input|human_approval|end>,
        }}
    """)
    humanMsg = HumanMessage(f"current user request: {current_user_input}, current state: {json.dumps(currentState)}")

    supervisorPrompt = [systemMsg, humanMsg]
    # build the chain and invoke
    response = llm.invoke(supervisorPrompt)
    print(f"Supervisor:LLM Response: {response.content}")

    try:
        decision = json.loads(response.content)
        state["next_agent"] = decision.get("next_agent", "human_input")
    except json.JSONDecodeError:
        state["messages"].append(
            AIMessage(content="I'm sorry, There's a problem understading your request. Could you please rephrase?")
        )
        state["next_agent"] = "human_input"

    return state