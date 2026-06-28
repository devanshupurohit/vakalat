# VAKALAT: Transforming legal accessibility for HackIndia Spark 9!

VAKALAT is an innovative legal assistant platform built as an MVP (Minimum Viable Product) for HackIndia Spark 9. It aims to make legal support affordable, intuitive, and accessible, especially for everyday Indians facing challenges like tenant disputes, consumer issues, and family matters. By blending cutting-edge AI technology with RAG-based legal knowledge retrieval, VAKALAT provides users with actionable insights and tools for resolving legal concerns without costly consultations.

## 🚀 RAG-Based AI Legal Advice

VAKALAT features **Retrieval-Augmented Generation (RAG)** capabilities, providing more accurate and context-aware legal advice by leveraging a comprehensive legal knowledge base. The system retrieves relevant legal documents and precedents before generating responses, ensuring advice is grounded in actual legal principles and Indian laws.

## Features

### Legal Query:
1. Users can ask legal questions via audio input (microphone or file upload) or text.
2. Covers categories such as Family, Tenant, Cyber, Workplace, Consumer, Property, and Other.
3. **RAG-Enhanced**: System retrieves relevant legal documents from the knowledge base before generating advice
4. Provides AI-generated advice, detailed PDF reports, audio responses (via Google Text-to-Speech), and optional email delivery.
● Example: "Can my landlord evict me without notice?" gives a detailed response, including actionable insights based on actual rent control laws.

### Document Analyzer:
### Upload legal PDFs (e.g., contracts, agreements) to:
1. Extract and preview text.
2. Summarize the document.
3. Highlight legal terms.
4. Analyze sentiment (e.g., whether the tone is neutral or aggressive).
5. Outputs include a chatbot-style response, summary file, sentiment score, list of terms, and downloadable PDF reports, all deliverable via email.

### Mediation Assistant:
1. Users input dispute details like parties involved, issue description, and desired outcome.
2. The platform generates AI-driven mediation strategies along with a clear mediation plan and PDF agreement.
● Example: Resolving unpaid rent disputes amicably.

### RAG Knowledge Base:
1. **TF-IDF Powered**: Uses scikit-learn TF-IDF vectorization for lightweight document retrieval
2. **IPC Legal Knowledge Base**: Automatically indexes the IPC book for legal context
3. **Persistent Storage**: Knowledge base is stored locally using pickle files in `tfidf_db/` for fast retrieval


# ⚙ Technical Highlights

## Backend:
1. Built using Gradio (AI web interface) and Python 3.12.

## Incorporates:
1. Groq API for legal analysis, summarization, and sentiment assessment.
2. **scikit-learn TF-IDF** for lightweight document retrieval (RAG system).
3. SpeechRecognition for processing audio inputs.
4. PyMuPDF and ReportLab for managing PDF files.
5. gTTS for generating audio outputs and smtplib for sending emails securely via environment variables.
6. FastAPI and Starlette for enhanced web server capabilities.

## RAG Architecture:
1. **Vector Database**: TF-IDF vectorization with scikit-learn for persistent storage of legal documents
2. **Document Chunking**: Automatic text chunking with overlap for better retrieval
3. **Cosine Similarity**: Efficient similarity search for document retrieval
4. **IPC Knowledge Base**: Automatically indexes the IPC book from `data/ipc_book.pdf` for legal context



# 🎯 Real-World Impact

## Accessibility: 
● Designed for underserved rural and semi-urban communities in India, where legal help is often expensive and scarce.
Multilingual Capabilities (future): Planned support for regional languages like Hindi and Tamil, making it inclusive for diverse user groups.

## Usability:
● User-friendly Gradio interface with audio and text inputs to address technical barriers.



# 🚀 Scalability & Vision

## VAKALAT is built with modular architecture, allowing future upgrades:
### Language Support:
1. Adding regional languages to cater to more users across India.
2. Additional Features: Introducing legal notice generation, consumer complaint drafting, and personalized legal assistance.
3. Community Focus: Empowering millions by bridging the gap between legal systems and everyday citizens.



# 🛠 Tech Stack Overview

## Backend:
1. Gradio: Streamlined AI-powered web interface.
2. Python 3.12: Core backend logic.
3. Groq API: Legal analysis and AI functionality.
4. SpeechRecognition: Audio input processing.
5. PyMuPDF & ReportLab: For PDF manipulation and creation.
6. gTTS: Converts text to speech for audio responses.
7. smtplib: Securely sends email outputs.
8. python-dotenv: Secure configuration.
9. scikit-learn: TF-IDF vectorization for RAG system.
10. FastAPI & Starlette: Enhanced web server capabilities.
11. NumPy & Pandas: Data processing and analysis.



# 📋 Prerequisites
1. Python 3.12+
2. Groq API Key
3. SMTP Credentials: Gmail app-specific password (optional for email features)
4. Git: For cloning



# 🛠 Installation

## Backend Setup (Gradio)

1. Clone the Repository:
```
git clone https://github.com/<your-username>/vakalat.git
```
```
cd vakalat
```

2. Set Up Virtual Environment:
```
python -m venv venv
```
```
# Windows:
venv\Scripts\activate
```
```
# Linux/Mac:
source venv/bin/activate
```

3. Install Dependencies:
```
pip install -r requirements.txt
```
● requirements.txt:
```
gradio==4.44.1
gradio_client==1.8.0
huggingface_hub==0.25.2
groq==0.11.0
httpx==0.27.2
pydantic==2.10.6
fastapi==0.115.6
starlette==0.41.3
PyMuPDF==1.24.2
gtts==2.5.3
python-dotenv==1.0.1
reportlab==4.2.2
pillow==10.4.0
SpeechRecognition==3.10.4
scikit-learn==1.5.0
numpy
pandas
```

4. Configure Environment:
```
# don't forget to replace your gmail in next line
echo -e "GROQ_API_KEY=your_groq_api_key\nSMTP_USER=your_email@gmail.com\nSMTP_PASSWORD=your_app_password\nSMTP_SERVER=smtp.gmail.com\nSMTP_PORT=587" > .env
```

5. Run Gradio App:
```
python app.py
```

**Note**: On first run, the RAG engine will automatically load and index the IPC book from `data/ipc_book.pdf` for legal context retrieval. The vectorized database will be stored in `tfidf_db/` for persistent storage.





# 🎥 Demo
[![video demo](https://img.youtube.com/vi/T2C6aCxVlUU/0.jpg)](https://www.youtube.com/watch?v=T2C6aCxVlUU)



# 🚀 Usage

1. Open http://localhost:7860 in your browser
2. Features: Use Legal Query, Document Analyzer, or Mediation with audio/text inputs.
3. Outputs: Get text responses, PDFs, audio, and emails.
4. Logs: Check vakalat.log in the project root.



# Why VAKALAT?
● VAKALAT isn’t just a legal assistant; it’s a transformative tool for equitable justice. By merging AI capabilities with intuitive design, it addresses the critical challenge of legal accessibility for HackIndia Spark 9 and beyond.



# 📜 License
● MIT License. See LICENSE.



# 🙌 HackIndia Spark 9
● VAKALAT, built for HackIndia Spark 9, empowers Indians with accessible legal tools, blending AI and modern web tech for real-world impact.



# Contact

● If you have any query, suggestions or feedback, feel free to contact us and mail us at dogradhruv2005@gmail.com or abhinavsinghal876@gmail.com
