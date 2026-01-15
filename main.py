from langgraph.graph import StateGraph, END
from models.state import PurchaseState
from agents.intent_parser import intent_parser_agent
from langchain_core.messages import AIMessage

def run_purchase_buddy():
  print("Welcome to PurchaseBuddy! Type your requests below.\n")
  print("Example: 'I want to buy 6 eggs and 1 bread.'")
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
      current_agent="",
      conversation_complete=False
  )

  while not state.get("conversation_complete"):
      user_input = input("You: ").strip()

      if not user_input:
            continue
      
      if user_input.lower() in ["exit", "quit", "bye"]:
            print("\nThanks for using PurchaseBuddy!")
            break
      
      state["user_input"] = user_input
      state["current_agent"] = "intent_parser"

      # invoke the app with the current state
      result = app.invoke(state)
      state.update(result)
      # print(state["messages"])

      for msg in state.get("messages", []):
            if isinstance(msg, AIMessage):
                print(f"\nBuddy: {msg.content}")
      
      state["messages"] = []

if __name__ == "__main__":
    run_purchase_buddy()