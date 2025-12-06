import streamlit as st
import random

# === In-Memory Data ===
allowed_names = {"Rickey", "Jordan", "Uyên", "Alex", "Taylor", "Morgan"}
all_missions = [
    "Say 'It's giving Oscar energy' during a speech.",
    "Start a synchronized laugh.",
    "Reference a fake award that never happened.",
    "Convince someone to switch seats.",
    "Make a dramatic exit and casually return.",
    "Get 3 people to pose like dinosaurs.",
    "Toast to something oddly specific.",
    "Whisper 'the ducks are in formation' and walk away.",
    "Create a fake Just Side Chatting Rule.",
    "Mistake two people's names on purpose.",
    "Put a spoon in someone's pocket secretly.",
    "Teach someone a fake secret handshake."
]

# Initialize session state
if 'assigned' not in st.session_state:
    st.session_state.assigned = {}
if 'history' not in st.session_state:
    st.session_state.history = []
if 'assigned_missions' not in st.session_state:
    st.session_state.assigned_missions = set()
if 'unavailable_missions' not in st.session_state:
    st.session_state.unavailable_missions = set()
if 'admin' not in st.session_state:
    st.session_state.admin = False

# === Utility Functions ===
def assign_mission(name):
    user = st.session_state.assigned.get(name)
    if user and user['status'] == 'IN PROGRESS':
        return
    available = [m for m in all_missions if m not in st.session_state.unavailable_missions]
    if not available:
        st.error("No missions left!")
        return
    mission = random.choice(available)
    st.session_state.assigned[name] = {
        'mission': mission,
        'swaps': 0,
        'status': 'IN PROGRESS',
        'proof': ''
    }
    st.session_state.assigned_missions.add(mission)
    st.session_state.unavailable_missions.add(mission)
    st.session_state.history.append({
        'name': name,
        'mission': mission,
        'status': 'IN PROGRESS',
        'swaps': 0,
        'proof': ''
    })


def swap_mission(name):
    user = st.session_state.assigned.get(name)
    if not user or user['swaps'] >= 2 or user['status'] != 'IN PROGRESS':
        return
    current = user['mission']
    st.session_state.assigned_missions.discard(current)
    st.session_state.history.append({
        'name': name,
        'mission': current,
        'status': 'SWAPPED',
        'swaps': user['swaps'],
        'proof': ''
    })
    available = [m for m in all_missions if m not in st.session_state.unavailable_missions]
    if not available:
        st.error("No missions to swap into!")
        st.session_state.assigned_missions.add(current)
        return
    new = random.choice(available)
    user['mission'] = new
    user['swaps'] += 1
    user['status'] = 'IN PROGRESS'
    st.session_state.assigned_missions.add(new)
    st.session_state.unavailable_missions.add(new)
    st.session_state.history.append({
        'name': name,
        'mission': new,
        'status': 'IN PROGRESS',
        'swaps': user['swaps'],
        'proof': ''
    })


def complete_mission(name, proof):
    user = st.session_state.assigned.get(name)
    if not user or user['status'] != 'IN PROGRESS':
        return
    user['status'] = 'COMPLETED'
    user['proof'] = proof
    st.session_state.history.append({
        'name': name,
        'mission': user['mission'],
        'status': 'COMPLETED',
        'swaps': user['swaps'],
        'proof': proof
    })
    st.session_state.assigned_missions.discard(user['mission'])


def fail_mission(name):
    user = st.session_state.assigned.get(name)
    if not user or user['status'] != 'IN PROGRESS':
        return
    user['status'] = 'FAILED'
    st.session_state.history.append({
        'name': name,
        'mission': user['mission'],
        'status': 'FAILED',
        'swaps': user['swaps'],
        'proof': ''
    })
    st.session_state.assigned_missions.discard(user['mission'])
    assign_mission(name)

# === Page Functions ===
def login_page():
    st.title("Just Side Chatting - Oscar Missions")
    name = st.text_input("Enter your name to login")
    if st.button("Login"):
        if name in allowed_names:
            st.session_state.user = name
            st.session_state.admin = (name == 'Uyên')
        else:
            st.error("Name not recognized.")


def mission_page():
    user = st.session_state.user
    st.header(f"Hello, {user}")
    data = st.session_state.assigned.get(user)
    if data:
        st.info(f"Mission: {data['mission']}")
        st.write(f"Swaps used: {data['swaps']}/2")
        st.write(f"Status: {data['status']}")
    else:
        st.write("You have no mission yet.")

    cols = st.columns(4)
    if cols[0].button("Get Mission"):
        assign_mission(user)
    if cols[1].button("Swap Mission"):
        swap_mission(user)
    if cols[2].button("Fail Mission"):
        fail_mission(user)
    if cols[3].button("Complete Mission"):
        proof = st.text_input("Enter proof of completion:")
        if proof and st.button("Submit Proof"):
            complete_mission(user, proof)


def manager_page():
    st.header("🛠 Game Manager Dashboard")
    stats = {
        'Assigned': len(st.session_state.assigned_missions),
        'Available': len(all_missions) - len(st.session_state.unavailable_missions),
        'Used': len(st.session_state.unavailable_missions)
    }
    st.write(stats)
    st.subheader("Current Assignments")
    st.write(st.session_state.assigned)
    st.subheader("Mission History")
    st.write(st.session_state.history)

# === Main ===
st.set_page_config(page_title="Oscar Missions", layout="centered")

if 'user' not in st.session_state:
    login_page()
else:
    pages = {"Missions": mission_page}
    if st.session_state.admin:
        pages["Manager"] = manager_page
    choice = st.sidebar.selectbox("Navigate to", list(pages.keys()))
    pages[choice]()
