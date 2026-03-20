import streamlit as st
import requests

# --- UI CONFIGURATION ---
st.set_page_config(page_title="AI Router Engine", page_icon="🧠", layout="centered")

st.title("🧠 Dynamic AI Router")
st.markdown("The Semantic Brain analyzes your request and routes it to the optimal AI model.")

# --- CREATE TABS ---
chat_tab, admin_tab = st.tabs(["💬 Router Chat", "⚙️ Model Database"])

# ==========================================
# TAB 1: THE CHAT ROUTER
# ==========================================
with chat_tab:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a coding question, request a summary, or test its reasoning..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("🧠 Semantic Brain is analyzing and routing..."):
            try:
                response = requests.post(
                    "http://backend:8000/route/",
                    json={"user_prompt": prompt}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    selected_model = data.get("selected_model", "Unknown")
                    specialty = data.get("specialty", "Unknown")
                    cost = data.get("cost", 0)
                    ai_message = data.get("message", "")
                    
                    ui_response = f"**🤖 Routed to:** `{selected_model}` | **Specialty:** `{specialty.upper()}` | **Cost:** `${cost}`\n\n---\n\n{ai_message}"
                    
                    with st.chat_message("assistant"):
                        st.markdown(ui_response)
                    
                    st.session_state.messages.append({"role": "assistant", "content": ui_response})
                    
                else:
                    st.error(f"Backend Error: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                st.error("🚨 Could not connect to the backend. Is your FastAPI server running on port 8000?")


# ==========================================
# TAB 2: THE ADMIN DASHBOARD
# ==========================================
with admin_tab:
    st.header("Live Database")
    
    # 1. READ: Fetch and display all models
    try:
        res = requests.get("http://backend:8000/models/")
        if res.status_code == 200:
            models = res.json()
            if models:
                # Streamlit automatically turns lists of dictionaries into beautiful tables!
                st.dataframe(models, width="stretch")
            else:
                st.info("No models found in the database.")
    except:
        st.error("Could not connect to database.")

    st.divider()

    # 2. CREATE: Form to add a new model
    st.subheader("Add New Model")
    with st.form("add_model_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        new_name = col1.text_input("Model Name (e.g., gpt-4o)")
        new_provider = col2.text_input("Provider (e.g., OpenAI, Groq)")
        new_cost = col1.number_input("Cost per 1k tokens", min_value=0.0, format="%.4f")
        new_specialty = col2.selectbox("Specialty", ["general", "coding", "reasoning"])
        
        submit_add = st.form_submit_button("➕ Add Model")
        
        if submit_add and new_name and new_provider:
            new_data = {
                "name": new_name,
                "provider": new_provider,
                "cost_per_1k_tokens": new_cost,
                "specialty": new_specialty
            }
            requests.post("http://backend:8000/models/", json=new_data)
            st.rerun() # Instantly refreshes the page to show the new table!

    st.divider()

    # 3. DELETE: Form to remove a model
    st.subheader("Delete Model")
    with st.form("delete_model_form", clear_on_submit=True):
        del_id = st.number_input("Enter the ID of the model to delete", min_value=1, step=1)
        submit_del = st.form_submit_button("🗑️ Delete Model")
        
        if submit_del:
            requests.delete(f"http://backend:8000/models/{del_id}")
            st.rerun()
    
    st.divider()

    # 4. UPDATE: Form to modify an existing model
    st.subheader("Update Existing Model")
    with st.form("update_model_form", clear_on_submit=True):
        st.markdown("Enter the ID of the model you want to change, then fill in the new details.")
        update_id = st.number_input("Model ID to Update", min_value=1, step=1)
        
        col3, col4 = st.columns(2)
        up_name = col3.text_input("New Model Name")
        up_provider = col4.text_input("New Provider")
        up_cost = col3.number_input("New Cost per 1k", min_value=0.0, format="%.4f")
        up_specialty = col4.selectbox("New Specialty", ["general", "coding", "reasoning"])
        
        submit_update = st.form_submit_button("✏️ Update Model")
        
        if submit_update and up_name and up_provider:
            update_data = {
                "name": up_name,
                "provider": up_provider,
                "cost_per_1k_tokens": up_cost,
                "specialty": up_specialty
            }
            # Hit the PUT door we built in FastAPI!
            res = requests.put(f"http://backend:8000/models/{update_id}", json=update_data)
            if res.status_code == 200:
                st.success("Model updated successfully!")
                st.rerun()
            else:
                st.error("Model ID not found.")