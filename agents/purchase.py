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
    state["messages"].append({
        "role": "assistant",
        "content": f"Choosing items and providers based on your preferences....."
    })
    parsedItems = state.get("parsed_items", [])
    userPincode = state.get("user_pincode", "")
    providerResults = {}

    for item in parsedItems:
        itemName = item.get("name", "")
        itemCategory = item.get("category", "").lower()

        # search in different providers
        swiggyResults = searchSwiggy(itemName, itemCategory, userPincode)
        print(f"Swiggy Results for {itemName}: {swiggyResults}")

        # one item may have results from multiple providers
        providerResults[itemName] = {
            "swiggy": swiggyResults,
        }

        state["provider_results"] = providerResults


    systemMsg = SystemMessage("""You are a purchase agent. Your job is to search for each requested 
            item from various providers based on user preferences and availability, and select the best provider for each item.
            Consider factors such as price, delivery time, pincode coverage, and availability.
            Respond only in JSON format with the following structure:
            {
                "results": [
                    {
                        "item": <item name>,
                        "selectedProvider": <provider name>,
                        "reasoning": <brief reasoning for selecting the provider>,
                        "clarificationQuestions": [<list of questions if any clarification is needed>],
                        "needsClarification": <true/false>
                    }
                ]
            }
            If clarification is needed for any item, include the relevant questions in "clarificationQuestions" and set "needsClarification" to true for that item.
            """)

    humanMsg = HumanMessage(f"items: {parsedItems}, provider results: {providerResults}, pincode: {userPincode}")
    purchaseAgentPrompt = [systemMsg, humanMsg]

    # build the chain and invoke
    response = llm.invoke(purchaseAgentPrompt)
    print(f"LLM Response: {response.content}")

    try:
        responseParsed = json.loads(response.content)
        decisions = responseParsed.get("results", [])

        needs_clarification = False
        missing_provider = False
        clarification_msgs = []
        missing_provider_msgs = []
        selected_providers = {}

        for decision in decisions:
            item_name = decision.get("item", "Unknown item")
            if decision.get("needsClarification", False):
                needs_clarification = True
                questions = decision.get("clarificationQuestions", [])
                clarification_msgs.append(
                    f"{item_name}: " + ("\n".join(questions) if questions else "Need more information.")
                )
            elif not decision.get("selectedProvider"):
                missing_provider = True
                missing_provider_msgs.append(
                    f"{item_name}: " + (decision.get("reasoning", "No provider could be selected."))
                )
            else:
                selected_providers[item_name] = decision.get("selectedProvider", "")

        if needs_clarification:
            state["messages"].append({
                "role": "assistant",
                "content": "Some items need clarification:\n" + "\n\n".join(clarification_msgs)
            })
            state["next_agent"] = "human_input"
        elif missing_provider:
            state["messages"].append({
                "role": "assistant",
                "content": "Could not select provider for some items:\n" + "\n\n".join(missing_provider_msgs) +
                           "\nCould you please provide more details or try again?"
            })
            state["next_agent"] = "human_input"
        else:
            state["selected_provider"] = selected_providers
            state["messages"].append({
                "role": "assistant",
                "content": "Selected providers:\n" + "\n".join(
                    [f"{item}: {provider}" for item, provider in selected_providers.items()]
                ) + "\nProceeding to billing."
            })
            state["next_agent"] = "billing_agent"

    except json.JSONDecodeError:
        state["messages"].append({
            "role": "assistant",
            "content": "I'm sorry, I couldn't process your request. Do you want to try again?"
        })
        state["next_agent"] = "human_input"

    return state