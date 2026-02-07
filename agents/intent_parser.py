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

"""
  This agent will be the frontline of all user queries. Responsibility of this agent will be:
  - Parse raw user queries and extract required information.
  - Detect category of item like grocery, electronics, clothing, etc.
  - Extract quantity of the item.
  - Extract unit of the desired quantity such as pcs, pieces, kg, litre, boxes, and so on.
  - Decide the next action.
"""
def intent_parser_agent(state: PurchaseState) -> PurchaseState:
    user_input = state.get("user_input", "")

    if not user_input:
        messages = state.get("messages", [])
        if messages:
            # get the last user message
            user_input = messages[-1].get("content", "")

    systemMsg = SystemMessage("""You are an intent parser cum analyser agent. Your job is to parse user requests for purchasing items and extract relevant information such as item names, categories, quantities, price expectations, delivery preferences and units.
        Respond only in JSON format with the following structure:
        {{
            "items": [{{
                "name": <item name>,
                "category": <grocery|electronics|cookedFood>,
                "quantity": <quantity>,
                "unit": <kg|litre|pcs||plate>,
                "priceExpectation": <price expectation if mentioned>,
                "isQuickDelivery": <true/false if mentioned like urgent|asap|instantly|quickly>,
            }}],
        "pincode": <pincode if mentioned>,
        "deliveryPreference": <preferred delivery time if mentioned>,
        "needsClarification": <true/false>,
        "clarificationQuestions": [<list of questions if needsClarification is true>]
        }}
        - Normalize delivery preferences into specific hour ranges in 24Hr format like "10-12", "14-16".
        - Morning time refers to "6-10".
        - Before lunch refers to "12-14".
        - After Lunch time refers to "14-17".
        - Before Dinner time refers to "16-19".
        """)
    humanMsg = HumanMessage(f"{user_input}")

    intentParserPrompt = [systemMsg, humanMsg]
    # build the chain and invoke
    response = llm.invoke(intentParserPrompt)
    print(f"LLM Response: {response.content}")

    try:
        parsedResult = json.loads(response.content)

        if parsedResult.get("needsClarification", False):
            state["messages"].append(
                AIMessage(content="I have a few questions to clarify your request:\n" + "\n".join(parsedResult.get("clarificationQuestions", [])))
            )
        else:
            parsedItems = parsedResult.get("items", [])
            if not parsedItems:
                state["messages"].append(
                    AIMessage(content="I'm sorry, I couldn't identify any items in your request. Could you please specify what you would like to purchase?")
                )
                state["next_agent"] = "human_input"
            else:
                state["parsed_items"] = parsedItems
                state["user_pincode"] = parsedResult.get("pincode", "")
                state["delivery_time_preference"] = parsedResult.get("deliveryPreference", "")

                # show parsed items to user
                state["messages"].append(
                    AIMessage(
                        content=f"I have understood your request. Here are the details:\n" +
                                "\n".join([f"- {item['quantity']} {item.get('unit', '')} of {item['name']} ({item['category']})" for item in parsedItems]) +
                                (f"\nPincode: {state['user_pincode']}" if state['user_pincode'] else "") +
                                (f"\nPreferred Delivery Time: {state['delivery_time_preference']}" if state['delivery_time_preference'] else "")
                    )
                )

            state["next_agent"] = "purchase_agent"
    except json.JSONDecodeError:
        state["messages"].append(
            AIMessage(content="I'm sorry, I couldn't understand your request. Could you please rephrase?")
        )
        state["next_agent"] = "human_input"

    return state