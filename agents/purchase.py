import json
from langchain_openai import AzureChatOpenAI
from langchain.messages import HumanMessage, SystemMessage
from config import azure_openai_api_key, azure_openai_endpoint, azure_openai_deployment, azure_openai_api_version
from models.state import PurchaseState
from tools.swiggy import searchSwiggy

# initialize LangChain LLM with Azure OpenAI
llm = AzureChatOpenAI(
    openai_api_key=azure_openai_api_key,
    azure_endpoint=azure_openai_endpoint,
    deployment_name=azure_openai_deployment,
    openai_api_version=azure_openai_api_version,
    temperature=0
)

def purchase_agent(state: PurchaseState) -> PurchaseState:
    """ purchase agent - placeholder for future implementation """
    parsedItems = state.get("parsed_items", [])
    userPincode = state.get("user_pincode", "")
    providerResults = {}

    for item in parsedItems:
        itemName = item.get("name", "")
        itemCategory = item.get("category", "").lower()

        # search in different providers
        swiggyResults = searchSwiggy(itemName, itemCategory, userPincode)

        providerResults[itemName] = {
            "swiggy": swiggyResults,
        }

        state["provider_results"] = providerResults


    systemMsg = SystemMessage("""You are a purchase agent. Your job is to search for requested 
            items from various providers based on user preferences and availability and
            select the best option for the user.
            Consider factors such as price, delivery time, pincode coverage and availability.
            Respond only in JSON format with the following structure:
            {{
            selectedProvider: <provider name>,
            reasoning: <brief reasoning for selecting the provider>,
            clarificationQuestions: [<list of questions if any clarification is needed>]
            needsClarification: <true/false>
            }}
            """)
    humanMsg = HumanMessage(f"items: {parsedItems}, provider results: {providerResults}, pincode: {userPincode}")
    purchaseAgentPrompt = [systemMsg, humanMsg]

    # build the chain and invoke
    response = llm.invoke(purchaseAgentPrompt)
    print(f"LLM Response: {response.content}")

    try:
        decision = json.loads(response.content)
        if decision.get("needsClarification", False):
            state["messages"].append({
                "role": "assistant",
                "content": "Found your items! But need below inputs\n" +
                           "\n".join(decision.get("clarificationQuestions", []))
            })
            state["next_agent"] = "human_input_agent"
        else:
            state["selected_provider"] = decision.get("selectedProvider", "")
            state["messages"].append({
                "role": "assistant",
                "content": f"Selected provider: {state['selected_provider']}. Proceeding to billing."
            })
            # for now end here
            state["next_agent"] = "end"

    except json.JSONDecodeError:
        state["messages"].append({
            "role": "assistant",
            "content": "I'm sorry, I couldn't process your request. Do you want to try again?"
        })
        state["next_agent"] = "human_input_agent"

    return state