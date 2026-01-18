from langgraph.graph import StateGraph, END
from models.state import PurchaseState
from agents.intent_parser import intent_parser_agent
from langchain_core.messages import AIMessage

def run_purchase_buddy():
  print("Welcome to PurchaseBuddy! Type your requests below.\n")
  print("Example: 'I want a plate of biryani quickly'")
  print("Type 'exit' to quit the application.\n")

  graph = StateGraph(PurchaseState)
  graph.add_node("intent_parser", intent_parser_agent)

  graph.set_entry_point("intent_parser")

  graph.add_edge("intent_parser", END)

  # compile the graph into an executable app
  app = graph.compile()

  # print(app.get_graph().draw_mermaid())

  state = PurchaseState(
      messages=[],
      user_input="",
      parsed_items=[],
      current_agent=""
  )

  while True:
      user_input = input("You: ").strip()

      if not user_input:
            continue
      
      if user_input.lower() in ["exit", "quit", "bye"]:
            print("\nThanks for using PurchaseBuddy!")
            break
      
      state["user_input"] = user_input
      state["current_agent"] = "intent_parser"

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
            print(f"\nBuddy: {lastMessage.content}")
      # try:
            
      # except Exception as e:
      #      print(f"Error: {e}")
      #      state = None

if __name__ == "__main__":
    run_purchase_buddy()