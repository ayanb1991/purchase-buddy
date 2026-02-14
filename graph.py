from langgraph.graph import StateGraph, END
from agents.billing import billing_agent
from agents.purchase import purchase_agent
from models.state import PurchaseState
from agents.intent_parser import intent_parser_agent
from agents.supervisor import supervisor_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage

def conditional_routing(state: PurchaseState):
      """ Conditional routing logic based on state """
      next_agent = state.get("next_agent", "")

      if next_agent == "human_input":
          return END
      if next_agent == "human_approval":
          return END
      elif next_agent == "end":
          return END
      
      return next_agent

def prepareState(state:PurchaseState = None, userInput="") -> PurchaseState:
    if state and state != {}:
        state["messages"].append(HumanMessage(content=userInput))
        state["next_agent"] = "intent_parser"
        state["need_human_approval"] = False
        return state
    return PurchaseState(
            messages=[HumanMessage(content=userInput)],
            # user_input must store the initial user query
            user_input= userInput,
            parsed_items=[],
            user_pincode="",
            delivery_time_preference="",
            next_agent="intent_parser",
            selected_provider="",
            provider_results=None,
            final_order=None,
            need_human_approval=False
        )

def create_graph():
  graph = StateGraph(PurchaseState)
  # nodes
  graph.add_node("intent_parser", intent_parser_agent)
  graph.add_node("purchase_agent", purchase_agent)
  graph.add_node("billing_agent", billing_agent)
  graph.add_node("supervisor_agent", supervisor_agent)

  graph.set_entry_point("supervisor_agent")

  # edges
  graph.add_conditional_edges("supervisor_agent", conditional_routing, {
       "intent_parser": "intent_parser",
       "purchase_agent": "purchase_agent",
       "billing_agent": "billing_agent",
       "human_input": END,
       END: END
  })
  graph.add_conditional_edges("intent_parser", conditional_routing, {
       "purchase_agent": "purchase_agent",
       "human_input": END,
       END: END
  })
  graph.add_conditional_edges("purchase_agent", conditional_routing, {
       "billing_agent": "billing_agent",
       "human_input": END,
       END: END
  })
  graph.add_conditional_edges("billing_agent", conditional_routing, {
       "human_input": END,
       END: END
  })

  # print(app.get_graph().draw_mermaid())
  # compile the graph into an executable app
  checkpointer = InMemorySaver()
  return graph.compile(checkpointer=checkpointer)
