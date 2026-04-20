#  Bud AI: The Rival-Mentor Learning Framework
**Built for PromptWars 2026** *Empowering BCA Students through Interactive AI Persona-Driven Mentorship.*

##  The Vision
**Bud AI** isn't just another chatbot; it's a dual-persona AI system designed to bridge the gap between "Passive Learning" and "Active Building." Built using **LangChain** and **Google’s Gemini/Llama-3.3**, Bud AI offers a unique "Rival-Mentor" framework to keep students engaged and motivated.

##  The Elite Squad (Mascots)
Our system features two distinct AI personas that the user can toggle between:
* **Professor Z (The Mentor):** An expert teacher who provides structured, glass-clear explanations and deep technical insights.
* **Aman (The Rival):** A high-energy, competitive peer who challenges you to code faster, think sharper, and beat the clock.

##  Tech Stack
* **Frontend:** Streamlit (Custom Glassmorphic UI)
* **Orchestration:** LangChain
* **Models:** Google Gemini / Groq (Llama-3.3-70B)
* **Vector Database:** ChromaDB (Ready for RAG-based syllabus integration)
* **Environment:** Developed in **Google Antigravity**

##  Security First
Bud AI implements professional-grade security practices:
* **Zero-Exposure API Management:** Utilizes `st.secrets` and `.env` protocols to ensure API keys are never leaked in the source code.
* **Modular Architecture:** Clean separation of concerns between UI (`app.py`) and Logic (`assistant.py`).

##  Quick Start
1. Clone the repo:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Bud-AI.git
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   streamlit run app.py
   ```

---
**Developed by:** Jouzia Afreen H  
**Cohort:** BCA 2024–2027, St. Joseph’s College  
**Location:** Cuddalore, TN
