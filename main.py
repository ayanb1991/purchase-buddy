from models.state import PurchaseState
from langchain_core.messages import AIMessage, HumanMessage
from graph import create_graph
class PurchaseBuddy:
     def __init__(self, graph):
          self.graph = graph
          self.messageDisplayCount = 0
          self.state = PurchaseState(
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
     
     def display_messages(self):
      """ Display messages that haven't been displayed yet """
      currentState = self.state
      messages = currentState.get("messages", [])
      newMessages = messages[self.messageDisplayCount:]
      # print(messages)
      # print(newMessages)

      for msg in newMessages:
           if isinstance(msg, AIMessage):
                  print(f"\n🤖 Buddy: {msg.content}")
      
      # update last displayed message count
      self.messageDisplayCount += len(messages)

     def run(self):
         print("Welcome to PurchaseBuddy! Type your requests below.\n")
         print("Example: 'I want a plate of biryani for lunch in my pin 700001 within INR 300, Very hungry! Quick Please'")
         print("Type 'exit' to quit the application.\n")

         while True:
            user_input = input("You: ").strip()

            if not user_input:
                  continue
            
            if user_input.lower() in ["exit", "quit", "bye"]:
                  print("\nThanks for using PurchaseBuddy!")
                  break
            
            self.state["user_input"] = user_input

            # append user message to state messages
            self.state["messages"].append(HumanMessage(content=user_input))

            # invoke the app with the current state
            result = self.graph.invoke(self.state)
            self.state.update(result)
            
            # display messages that haven't been displayed yet
            self.display_messages()
            
            if result.get("need_human_approval", False):
                  approval = input("\nPlease type 'yes' to confirm the order or 'no' to cancel: ").strip().lower()
                  if approval in ['yes', 'y']:
                        print("\n ✅ Order confirmed! Thank you for using PurchaseBuddy.")
                        # reset state for next interaction
                        self.state = PurchaseState(
                              messages=[],
                              messageDisplayCount=0,
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
                              self.state["user_input"] = ""
                              self.state["next_agent"] = "intent_parser"
                              self.state["need_human_approval"] = False
                        else:
                              print("\nThanks for using PurchaseBuddy! Goodbye.")
                              break
                  
            
            # try:
                  
            # except Exception as e:
            #      print(f"Error: {e}")
            #      state = None

def run_purchase_buddy():
      graph = create_graph()
      app = PurchaseBuddy(graph)
      app.run()

if __name__ == "__main__":
    run_purchase_buddy()