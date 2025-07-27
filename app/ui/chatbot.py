import requests
import streamlit as st

st.set_page_config(page_title="AI Travel Assistant", page_icon="🌍", layout="centered")
st.title("AI Travel Assistant")
st.write("Have a conversation about your travel plans!")
st.write("For example, try asking:")
st.write("• Family vacation in Orlando in July from London")
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hi! I'm your AI Travel Assistant. Tell me about your dream trip - where would you like to go?",
        }
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.text(message["content"])

if prompt := st.chat_input("Ask about travel destinations..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.text(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Planning your perfect trip..."):
            try:
                response = requests.post(
                    "http://localhost:8000/travel-assistant",
                    json={"query": prompt},
                    timeout=120,
                )

                if response.status_code == 200:
                    advice = response.json()
                    formatted_response = f"""
Based on your request, here is my recommendation. \n                    
🌍 Recommended Destination:
{advice['destination']}\n
💡 Why am I recommending this destination:
{advice['reason']}\n
💰 Budget Estimate:
{advice['budget']}"""
                    if advice.get("hotel"):
                        hotel = advice["hotel"]
                        formatted_response += f"""
\n🏨 Hotel Recommendation:
• {hotel['name']} in {hotel['city']}
• Rating: {hotel['rating']} ⭐
• Price: ${hotel['price_per_night']}/night"""

                    if advice.get("flight"):
                        flight = advice["flight"]
                        formatted_response += f"""
\n🛫 Flight Recommendation:
• {flight['airline']} - {flight['from_airport']} → {flight['to_airport']}
• Duration: {flight['duration']}
• Price: ${flight['price']}
• Date: {flight['date']}"""

                    if advice.get("experience"):
                        experience = advice["experience"]
                        formatted_response += f"""
\n🎉 Experience Recommendation:
• {experience['name']} in {experience['city']}
• Duration: {experience['duration']}
• Price: ${experience['price']}"""

                    if advice.get("tips"):
                        formatted_response += f"""
\n💡 Travel Tips:
{chr(10).join(f'• {tip}' for tip in advice['tips'])}"""

                    st.text(formatted_response)

                    st.session_state.messages.append(
                        {"role": "assistant", "content": formatted_response}
                    )

                else:
                    error_msg = "Sorry, I couldn't get travel advice right now."
                    st.error(error_msg)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_msg}
                    )

            except Exception as e:
                error_msg = f"Error connecting to travel assistant: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_msg}
                )
