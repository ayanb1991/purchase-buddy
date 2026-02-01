from langgraph.graph import StateGraph, END
from agents.billing import billing_agent
from agents.purchase import purchase_agent
from models.state import PurchaseState
from agents.intent_parser import intent_parser_agent
from langchain_core.messages import AIMessage

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

def run_purchase_buddy():
  print("Welcome to PurchaseBuddy! Type your requests below.\n")
  print("Example: 'I want a plate of biryani for dinner in my pin 700001 within INR 300, Very hungry! Quick Please'")
  print("Type 'exit' to quit the application.\n")

  graph = StateGraph(PurchaseState)
  # nodes
  graph.add_node("intent_parser", intent_parser_agent)
  graph.add_node("purchase_agent", purchase_agent)
  graph.add_node("billing_agent", billing_agent)

  graph.set_entry_point("intent_parser")

  # edges
  graph.add_conditional_edges("intent_parser", conditional_routing, {
       "human_input": END,
       "purchase_agent": "purchase_agent",
       END: END
  })
  graph.add_conditional_edges("purchase_agent", conditional_routing, {
       "human_input": END,
       "billing_agent": "billing_agent",
       END: END
  })
  graph.add_conditional_edges("billing_agent", conditional_routing, {
       "human_input": END,
       END: END
  })

  # compile the graph into an executable app
  app = graph.compile()

  # print(app.get_graph().draw_mermaid())

  state = PurchaseState(
      messages=[],
      user_input="",
      parsed_items=[],
      user_pincode="",
      delivery_time_preference="",
      next_agent="intent_parser",
      selected_provider="",
      provider_results={},
      final_order={},
      need_human_approval=False
  )

  while True:
      user_input = input("You: ").strip()

      if not user_input:
            continue
      
      if user_input.lower() in ["exit", "quit", "bye"]:
            print("\nThanks for using PurchaseBuddy!")
            break
      
      state["user_input"] = user_input

      # append user message to state messages
      state["messages"].append({
            "role": "user",
            "content": user_input
      })

      # invoke the app with the current state
      result = app.invoke(state)
      state.update(result)
      # print(state["messages"])

      messages = result.get("messages", [])
      if messages:
            lastMessage = messages[-1]
      if isinstance(lastMessage, AIMessage):
            print(f"\n🤖 Buddy: {lastMessage.content}")
      
      if result.get("need_human_approval", False):
            approval = input("\nPlease type 'yes' to confirm the order or 'no' to cancel: ").strip().lower()
            if approval in ['yes', 'y']:
                  print("\n ✅ Order confirmed! Thank you for using PurchaseBuddy.")
                  # reset state for next interaction
                  state = PurchaseState(
                        messages=[],
                        user_input="",
                        parsed_items=[],
                        user_pincode="",
                        delivery_time_preference="",
                        next_agent="intent_parser",
                        selected_provider="",
                        provider_results={},
                        final_order={},
                        need_human_approval=False
                  )
            else:
                  print("\n ❌ Order cancelled. You can modify your request or exit.")
                  approval_change = input("\nWould you like to adjust your request? (yes to continue, no to exit): ").strip().lower()
                  if approval_change in ['yes', 'y']:
                        print("\nLet's try again. Please enter your new request.")
                        # Reset only necessary fields, keep messages if needed
                        state["user_input"] = ""
                        state["next_agent"] = "intent_parser"
                        state["need_human_approval"] = False
                  else:
                        print("\nThanks for using PurchaseBuddy! Goodbye.")
                        break
            
           
      # try:
            
      # except Exception as e:
      #      print(f"Error: {e}")
      #      state = None

if __name__ == "__main__":
    run_purchase_buddy()