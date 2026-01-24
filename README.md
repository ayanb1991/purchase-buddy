# purchase-buddy
An intelligent agentic shopping assistant built with langgraph that helps users purchase items from multiple providers.

# project goals
This is a learning project that takes an agentic approach to create a conversational purchase experience. It involves buying items 
through natural language conversations and it aims to support different item categories such as grocery, electronics, cooked foods
from multiple vendors or providers.

# agents
Supervisor: routes requests to appropriate agents depending upon next action
IntentParser: parses the user request, extract key factors like item name, quantity, unit, and preferences. 
Purchase: Queries multiple provides and compares different options based on user preference.
Billing: Calculate totals, generates order, summary.
Support: Handles generic queries about current order through the contextual data from other agents.

# tech stack
- Python
- Streamlit UI
- Langchain
- Langgraph
- LLM

# architecture


# limitations
- provider and inventory data is static for now
- item availability is hard-coded
- no order shipment tracking
- no user profile management
- conversations history is not persistent
- no real payment involved
