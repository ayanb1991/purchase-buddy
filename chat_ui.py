import uuid
import streamlit as st
import time
from datetime import datetime
import streamlit.components.v1 as components
from langchain_core.messages import AIMessage, HumanMessage
from graph import create_graph, prepareState

# Page configuration
st.set_page_config(
    page_title="PurchaseBuddy",
    page_icon="🥕",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Import Google Font - Poppins */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Main container styling */
    .stApp {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        background-image: 
            url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
    }
    
    /* Style the chat input */
    .stChatInput > div {
        background: #f9fafb;
        border: 2px solid #10b981 !important;
        border-radius: 25px;
    }
    
    .stChatInput textarea {
        background: #f9fafb;
        color: #1f2937;
        font-family: 'Poppins', sans-serif;
    }
    
    stChatInput textarea {
        background: #f9fafb !important;
        color: #1f2937 !important;
        font-family: 'Poppins', sans-serif !important;
        caret-color: #10b981 !important; /* Add cursor color */
    }

    .stChatInput textarea:focus {
        background: white !important; /* Change background on focus */
        outline: none !important;
        caret-color: #10b981 !important;
    }

    .stChatInput textarea::placeholder {
        color: #9ca3af !important;
    }
    
    .stChatInput textarea::placeholder {
        color: #9ca3af;
    }
    
    .stChatInput button {
        background: #10b981 !important;
        color: white !important;
        border-radius: 50%;
    }
    
    .stChatInput button:hover {
        background: #059669 !important;
    }
</style>
""", unsafe_allow_html=True)

# SVG Icons as data URIs
GROCERY_ICON = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'%3E%3Cpath d='M7 18c-1.1 0-1.99.9-1.99 2S5.9 22 7 22s2-.9 2-2-.9-2-2-2zM1 2v2h2l3.6 7.59-1.35 2.45c-.16.28-.25.61-.25.96 0 1.1.9 2 2 2h12v-2H7.42c-.14 0-.25-.11-.25-.25l.03-.12.9-1.63h7.45c.75 0 1.41-.41 1.75-1.03l3.58-6.49c.08-.14.12-.31.12-.48 0-.55-.45-1-1-1H5.21l-.94-2H1zm16 16c-1.1 0-1.99.9-1.99 2s.89 2 1.99 2 2-.9 2-2-.9-2-2-2z'/%3E%3C/svg%3E"

FRUIT_ICON = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'%3E%3Cpath d='M12 2c3 0 3 2 3 2s2-2 4-2c3 0 4 3 4 5 0 4-6 8-8 10-2-2-8-6-8-10 0-2 1-5 4-5 2 0 4 2 4 2s0-2 3-2z'/%3E%3C/svg%3E"

VEGGIE_ICON = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'%3E%3Cpath d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z'/%3E%3C/svg%3E"

DAIRY_ICON = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'%3E%3Cpath d='M18 6H6v2h12V6zm-2 4H8v2h8v-2zm-2 4H10v2h4v-2zm0-8H10v2h4V6z'/%3E%3C/svg%3E"

MEAT_ICON = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'%3E%3Cpath d='M12 2C8.14 2 5 5.14 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.86-3.14-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z'/%3E%3C/svg%3E"

ASSISTANT_AVATAR = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='50' fill='%2310b981'/%3E%3Cpath d='M30 35h10v5H30zm30 0h10v5H60z' fill='white'/%3E%3Cpath d='M35 60c0-8.28 6.72-15 15-15s15 6.72 15 15' stroke='white' stroke-width='3' fill='none' stroke-linecap='round'/%3E%3Cpath d='M50 25c-8.28 0-15 6.72-15 15h30c0-8.28-6.72-15-15-15z' fill='white' opacity='0.3'/%3E%3C/svg%3E"

USER_AVATAR = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='50' fill='%236366f1'/%3E%3Ccircle cx='50' cy='40' r='15' fill='white'/%3E%3Cpath d='M50 60c-15 0-25 10-25 20h50c0-10-10-20-25-20z' fill='white'/%3E%3C/svg%3E"

# initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.graph = create_graph()
    st.session_state.threadID = st.query_params.get("threadID", str(uuid.uuid4()))
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hey! 👋 I am Purchase Buddy, your personal shopping assistant.",
            "timestamp": datetime.now().strftime("%H:%M")
        }
    ]
    st.session_state.showTyping = False
    st.session_state.scroll_key = 0

# build the entire HTML as a single string
html_content = """
<style>
    /* Import Google Font - Poppins */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Chat container */
    .chat-container {
        max-width: 800px;
        margin: 0 auto;
        background: white;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        overflow: hidden;
        height: 90vh;
        display: flex;
        flex-direction: column;
        position: relative;
    }
    
    /* Header */
    .chat-header {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 20px;
        text-align: center;
        position: relative;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .chat-header h1 {
        margin: 0;
        font-size: 32px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    /* Avatar */
    .avatar-container {
        margin: 20px auto 10px;
        text-align: center;
    }
    
    .avatar {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        border: 4px solid white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        background: white;
        padding: 10px;
    }
    
    .subtitle {
        color: rgba(255,255,255,0.95);
        margin-top: 15px;
        font-size: 17px;
        font-weight: 500;
    }
    
    .subtitle-small {
        color: rgba(255,255,255,0.8);
        margin-top: 5px;
        font-size: 13px;
        font-weight: 300;
    }
    
    /* Grocery category icons */
    .category-icons {
        display: flex;
        justify-content: center;
        gap: 15px;
        margin-top: 15px;
        padding: 10px;
    }
    
    .category-icon {
        width: 40px;
        height: 40px;
        background: rgba(255,255,255,0.2);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .category-icon:hover {
        background: rgba(255,255,255,0.3);
        transform: scale(1.1);
    }
    
    /* Messages area */
    .messages-container {
        flex: 1;
        overflow-y: auto;
        padding: 20px;
        background: #ffffff;
    }
    
    /* Date separator */
    .date-separator {
        text-align: center;
        color: #9ca3af;
        font-size: 13px;
        margin: 20px 0;
        font-weight: 400;
    }
    
    /* Message bubbles */
    .message {
        display: flex;
        align-items: flex-start;
        margin: 15px 0;
        animation: fadeIn 0.3s ease-in;
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .message-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        margin-right: 12px;
        flex-shrink: 0;
        background: white;
        padding: 5px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .message-content {
        background: white;
        border: 2px solid #e5e7eb;
        padding: 15px 20px;
        border-radius: 18px;
        max-width: 70%;
        font-size: 15px;
        line-height: 1.6;
        color: #1f2937;
        font-weight: 400;
    }
    
    .message.user {
        flex-direction: row-reverse;
    }
    
    .message.user .message-avatar {
        margin-left: 12px;
        margin-right: 0;
    }
    
    .message.user .message-content {
        background: white;
        border: 2px solid #10b981;
        color: #1f2937;
    }
    
    /* Action buttons */
    .action-buttons {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin: 15px 0;
        align-items: flex-end;
    }
    
    .action-button {
        background: white;
        border: 2px solid #10b981;
        color: #059669;
        padding: 12px 24px;
        border-radius: 25px;
        font-size: 15px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .action-button:hover {
        background: #10b981;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(16,185,129,0.3);
    }
    
    /* Typing indicator */
    .typing-indicator {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 15px 20px;
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 18px;
        width: fit-content;
    }
    
    .typing-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #10b981;
        animation: typing 1.4s infinite;
    }
    
    .typing-dot:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .typing-dot:nth-child(3) {
        animation-delay: 0.4s;
    }
    
    @keyframes typing {
        0%, 60%, 100% {
            transform: translateY(0);
            opacity: 0.5;
        }
        30% {
            transform: translateY(-10px);
            opacity: 1;
        }
    }
    
    /* Scrollbar styling */
    .messages-container::-webkit-scrollbar {
        width: 6px;
    }
    
    .messages-container::-webkit-scrollbar-track {
        background: #f9fafb;
    }
    
    .messages-container::-webkit-scrollbar-thumb {
        background: #d1d5db;
        border-radius: 3px;
    }
    
    .messages-container::-webkit-scrollbar-thumb:hover {
        background: #9ca3af;
    }
    
    /* Add padding to messages container to account for fixed input */
    .messages-container {
        padding-bottom: 80px !important;
    }
    
    /* Hide default Streamlit chat message styling */
    .stChatMessage {
        background: transparent !important;
        padding: 0 !important;
    }
</style>
"""
html_content += f"""

<div class="chat-container">
    <div class="chat-header">
        <h1>PurchaseBuddy</h1>
        <div class="avatar-container">
            <img src="{ASSISTANT_AVATAR}" class="avatar" alt="PurchaseBuddy">
            <div class="subtitle">We will reply as soon as we can</div>
            <div class="subtitle-small">Ask us anything, or share your feedback.</div>
        </div>
        <div class="category-icons">
            <div class="category-icon" title="Shopping Cart">
                <img src="{GROCERY_ICON}" width="24" height="24">
            </div>
            <div class="category-icon" title="Fruits">
                <img src="{FRUIT_ICON}" width="24" height="24">
            </div>
            <div class="category-icon" title="Vegetables">
                <img src="{VEGGIE_ICON}" width="24" height="24">
            </div>
            <div class="category-icon" title="Dairy">
                <img src="{DAIRY_ICON}" width="24" height="24">
            </div>
            <div class="category-icon" title="Meat & Seafood">
                <img src="{MEAT_ICON}" width="24" height="24">
            </div>
        </div>
    </div>
    <div class="messages-container" id="messages">
"""

# build messages HTML
for idx, message in enumerate(st.session_state.messages):
    if message["role"] == "assistant":
        if idx == 0:
            html_content += f'<div class="date-separator">{message["timestamp"]}</div>'
        
        html_content += f"""
<div class="message assistant">
    <img src="{ASSISTANT_AVATAR}" class="message-avatar" alt="Assistant">
    <div class="message-content">{message["content"]}</div>
</div>
"""
        
        # show action buttons after first assistant message
        if idx == 0:
            html_content += """
<div class="action-buttons">
    <button class="action-button">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
        </svg>
        Find more about pricing!
    </button>
    <button class="action-button">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"/>
        </svg>
        Talk to an expert!
    </button>
</div>
"""
    else:
        html_content += f"""
<div class="message user">
    <img src="{USER_AVATAR}" class="message-avatar" alt="User">
    <div class="message-content">{message["content"]}</div>
</div>
"""

# typing indicator
if st.session_state.get('showTyping', False):
    html_content += f"""
<div class="message assistant">
    <img src="{ASSISTANT_AVATAR}" class="message-avatar" alt="Assistant">
    <div class="typing-indicator">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    </div>
</div>
"""

# HTML structur closing tags
html_content += f"""
</div>
</div>
<script>
    // Use unique key to ensure script runs on each update
    const scrollKey_{st.session_state.scroll_key}_{int(time.time() * 1000)} = true;
    setTimeout(function() {{
        const messagesContainer = document.getElementById('messages');
        if (messagesContainer) {{
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }}
    }}, 100);
</script>
"""

# render the entire HTML as a single block
# embed the HTML string and execute the JavaScript
components.html(html_content, height=1000)

def syncUserMsgToGraph(userMessageContent: str):
    """ sync last user message to the graph's state for processing"""

    config = {"configurable": {"thread_id": st.session_state.threadID}}
    # graphState = st.session_state.graph.get_state()
    graphStateNext = prepareState()
    graphStateNext["messages"].append(HumanMessage(content=userMessageContent))
    currentGraphState = st.session_state.graph.invoke(graphStateNext, config=config)

    return currentGraphState

# chat input (Streamlit's native chat input) - placed outside
user_input = st.chat_input("What you like to order...")

if user_input:
    # add user message to st session state
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().strftime("%H:%M")
    })
    
    # increment scroll key to trigger scroll
    st.session_state.scroll_key += 1
    
    # show typing indicator
    st.session_state.showTyping = True
    st.rerun()

if st.session_state.get('showTyping', False):
    time.sleep(1.5)
    st.session_state.showTyping = False

    # try:
    # get last user message
    lastUserMessageFromStState = next((msg for msg in reversed(st.session_state.messages) if msg["role"] == "user"), None)
    if lastUserMessageFromStState:
        responseState = syncUserMsgToGraph(lastUserMessageFromStState["content"])
        responseStateMessages = responseState["messages"]

        # get assistant messages from graph response and add to session state
        assistantMessages = responseStateMessages[-1]
        if assistantMessages:
            # add assistant messages to session state
            st.session_state.messages.append({
                "role": "assistant",
                "content": assistantMessages.content,
                "timestamp": datetime.now().strftime("%H:%M")
            })

    # except Exception as e:
    #     print(f"Error processing message: {e}")
    #     st.session_state.messages.append({
    #         "role": "assistant",
    #         "content": "Sorry, something went wrong. Please try again.",
    #         "timestamp": datetime.now().strftime("%H:%M")
    #     })
    
    # increment scroll key to trigger scroll
    st.session_state.scroll_key += 1
    st.rerun()