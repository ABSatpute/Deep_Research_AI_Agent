import streamlit as st
from deep_research_backend import research_agent, retrieve_all_threads, generate_chat_title_from_messages
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import uuid


# ************************* Uility functions *****************************************

def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
    state = research_agent.get_state(config={'configurable': {'thread_id': thread_id}})
    # Check if messages key exists in state values, return empty list if not
    return state.values.get("messages", [])

#st.session_state -> dict ->
# CONFIG = {'configurable': {'thread_id': 'thread-1'}}

# ******************** Session Setup ***********************************
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []
    
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()
    
if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = retrieve_all_threads()

# NEW: persistent mappings for chat titles and title metadata
if 'chat_titles' not in st.session_state:
    st.session_state['chat_titles'] = {}

if 'chat_title_meta' not in st.session_state:
    # stores last message count at which title was updated for each thread_id
    st.session_state['chat_title_meta'] = {}
       
add_thread(st.session_state['thread_id'])

# # ********************** Slidebar UI ************************************

# st.sidebar.title("My Research Chats")

# if st.sidebar.button("New Chat"):
#     reset_chat()
    
# st.sidebar.header("My Conversations")
# for thread_id in st.session_state["chat_threads"][::-1]:
#     if st.sidebar.button(str(thread_id)):
#         st.session_state["thread_id"] = thread_id
#         messages = load_conversation(thread_id)

#         temp_messages = []
#         for msg in messages:
#             role = "user" if isinstance(msg, HumanMessage) else "assistant"
#             temp_messages.append({"role": role, "content": msg.content})
#         st.session_state["message_history"] = temp_messages

# ********************** Sidebar UI ************************************
st.sidebar.title("My Research Chats")

if st.sidebar.button("New Chat"):
    reset_chat()

st.sidebar.header("My Conversations")
for thread_id in st.session_state["chat_threads"][::-1]:
    chat_title = st.session_state['chat_titles'].get(thread_id, str(thread_id))
    # use thread_id as key to avoid duplicate widget key errors
    if st.sidebar.button(chat_title, key=str(thread_id)):
        # switch thread and load messages
        st.session_state["thread_id"] = thread_id
        messages = load_conversation(thread_id)

        temp_messages = []
        for msg in messages:
            role = "user" if isinstance(msg, HumanMessage) else "assistant"
            temp_messages.append({"role": role, "content": msg.content})

        st.session_state["message_history"] = temp_messages

        # If this thread has no title yet, set a fallback from the first message
        if temp_messages and (thread_id not in st.session_state['chat_titles'] or st.session_state['chat_titles'][thread_id] == "New Chat"):
            st.session_state['chat_titles'][thread_id] = temp_messages[0]['content'][:60]
            # Also set the meta to the number of messages we've loaded so the update logic won't re-run immediately
            st.session_state['chat_title_meta'][thread_id] = len(temp_messages)


# ============================ Main UI ============================

# loading the conversation History
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input("Type Here")

if user_input:
    # first add message to message history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)
        
    # CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']},
              "metadata": {
                  "thread_id": st.session_state['thread_id']
              },
              "run_name": "chat_turn"
              }

    # response = deep_research.invoke({'messages': [HumanMessage(content= user_input)]})
    # ai_message = response['messages'][-1].content
    
    # first add message to message history
    
    # st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
    
    # Assistant streaming block
    with st.chat_message("assistant"):
        # Use a mutable holder so the generator can set/modify it
        status_holder = {"box": None}

        def ai_only_stream():
            for message_chunk, metadata in research_agent.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages",
            ):
                # Lazily create & update the SAME status container when any tool runs
                if isinstance(message_chunk, ToolMessage):
                    tool_name = getattr(message_chunk, "name", "tool")
                    if status_holder["box"] is None:
                        status_holder["box"] = st.status(
                            f"🔧 Using `{tool_name}` …", expanded=True
                        )
                    else:
                        status_holder["box"].update(
                            label=f"🔧 Using `{tool_name}` …",
                            state="running",
                            expanded=True,
                        )

                # Stream ONLY assistant tokens
                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())

        # Finalize only if a tool was actually used
        if status_holder["box"] is not None:
            status_holder["box"].update(
                label="✅ Tool finished", state="complete", expanded=False
            )

    # Save assistant message
    st.session_state["message_history"].append(
        {"role": "assistant", "content": ai_message}
    )
    

# ------------------ Title update logic ------------------
    thread_id = st.session_state['thread_id']
    total_messages = len(st.session_state['message_history'])
    last_updated_at = st.session_state['chat_title_meta'].get(thread_id, 0)

    # Phase 1: before we hit 3 messages -> use first user message as title (if not set)
    if total_messages < 3:
        if st.session_state['message_history']:
            st.session_state['chat_titles'][thread_id] = st.session_state['message_history'][0]['content'][:60]

    # Phase 2: once total_messages >= 3, update the title every time total_messages is a multiple of 3
    # and we haven't updated at this message-count already.
    elif total_messages >= 3 and (total_messages % 3 == 0) and total_messages > last_updated_at:
        # prepare last 3 messages' content
        last_three = [m['content'] for m in st.session_state['message_history'][-3:]]
        try:
            new_title = generate_chat_title_from_messages(last_three)
            st.session_state['chat_titles'][thread_id] = new_title
            st.session_state['chat_title_meta'][thread_id] = total_messages
        except Exception:
            # On LLM failure, keep previous title (no crash)
            pass