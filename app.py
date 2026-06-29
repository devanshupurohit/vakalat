import gradio as gr
import speech_recognition as sr
from voice_of_the_user import transcribe_audio
from voice_of_the_lawyer import speak_response
from brain_of_the_lawyer import (
    analyze_legal_query_with_images, generate_pdf_report, summarize_document,
    extract_legal_terms, analyze_document_sentiment, extract_text_from_pdf,
    analyze_mediation, summarize_text
)
from utils import cleanup_temp_files, save_uploaded_file, save_text_to_file
import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("vakalat.log"),
        logging.StreamHandler()
    ]
)

load_dotenv()
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

LEGAL_CATEGORIES = ["Family", "Tenant", "Cyber", "Workplace", "Consumer", "Property", "Other"]

def send_email(recipient, subject, body, attachment_path=None):
    if not SMTP_USER or not SMTP_PASSWORD:
        return "Error: SMTP credentials not configured."
    
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, 'rb') as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
                msg.attach(part)
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        logging.info(f"Email sent to {recipient}")
        return f"Email sent successfully to {recipient}."
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        return f"Error sending email: {str(e)}"

def transcribe_and_analyze(audio_file, text_query, legal_category, uploaded_file=None, email_address=None):
    chat_history = []
    try:
        # Handle audio_file
        transcription = None
        if audio_file:
            # Handle tuple input (e.g., (sample_rate, audio_data) or (file_path, file_name))
            if isinstance(audio_file, tuple):
                logging.info(f"Audio input is tuple: {audio_file}")
                if len(audio_file) > 0:
                    audio_file = audio_file[0]  # Extract first element (file path or data)
                else:
                    chat_history.append({"role": "assistant", "content": "Error: Invalid audio input tuple."})
                    audio_file = None
            if isinstance(audio_file, (int, float)):
                logging.error(f"Invalid audio input: {type(audio_file)}")
                chat_history.append({"role": "assistant", "content": "Error: Invalid audio input. Please upload a valid audio file (e.g., WAV, MP3)."})

            if audio_file:
                audio_path = save_uploaded_file(audio_file)
                if audio_path:
                    transcription = transcribe_audio(audio_path)
                    if transcription:
                        logging.info(f"Transcription Result: {transcription}")
                        chat_history.append({"role": "user", "content": transcription})
                    else:
                        chat_history.append({"role": "assistant", "content": "Error: Could not transcribe audio. Using text query if provided."})
                else:
                    chat_history.append({"role": "assistant", "content": "Error: Could not process audio file. Using text query if provided."})

        # Fallback to text_query
        if not transcription and text_query:
            transcription = text_query
            logging.info(f"Using text query: {transcription}")
            chat_history.append({"role": "user", "content": transcription})

        if not transcription:
            return [{"role": "assistant", "content": "Error: Please provide an audio query or text query."}], None, None, None, None

        # Handle uploaded_file
        document_paths = []
        if uploaded_file:
            if isinstance(uploaded_file, tuple):
                uploaded_file = uploaded_file[0] if len(uploaded_file) > 0 else None
            file_path = save_uploaded_file(uploaded_file)
            if file_path:
                document_paths.append(file_path)
            else:
                chat_history.append({"role": "assistant", "content": "Error: Invalid or unsupported file type."})
                return chat_history, None, None, None, None

        response = analyze_legal_query_with_images(legal_category, transcription, [], document_paths, chat_history)
        if not response:
            logging.error("No response from legal analysis")
            chat_history.append({"role": "assistant", "content": "Error: Unable to generate legal analysis."})
            return chat_history, None, None, None, None

        summary = summarize_text(response) if len(response.split()) > 200 else ""
        if summary:
            response = f"**Summary**: {summary}\n\n**Full Response**: {response}"
        chat_history.append({"role": "assistant", "content": response})

        pdf_report = generate_pdf_report(transcription, response, chat_history, document_paths)
        if not pdf_report:
            logging.error("Failed to generate PDF report")
            chat_history.append({"role": "assistant", "content": "Error: Could not generate PDF report."})

        audio_response = speak_response(response)
        audio_button = gr.Button("Play Audio Response", visible=True)

        email_status = None
        if email_address:
            email_body = f"Legal Query: {transcription}\n\nResponse:\n{response}"
            email_status = send_email(email_address, "VAKALAT Legal Advice", email_body, pdf_report)
            chat_history.append({"role": "assistant", "content": email_status})

        return chat_history, pdf_report, audio_response, audio_button, email_status

    except Exception as e:
        logging.error(f"Error in transcribe_and_analyze: {e}")
        chat_history.append({"role": "assistant", "content": f"Error: {str(e)}"})
        return chat_history, None, None, None, None

def play_legal_query_audio(chat_history):
    if chat_history and isinstance(chat_history, list) and chat_history[-1].get("role") == "assistant":
        return speak_response(chat_history[-1]["content"])
    return None

def handle_document_analysis(uploaded_files, legal_category, email_address=None):
    chat_history = []
    try:
        document_paths = []
        extracted_texts = []
        
        if not uploaded_files:
            error_msg = "Error: Please upload at least one PDF document."
            chat_history.append({"role": "assistant", "content": error_msg})
            return chat_history, error_msg, [], "No sentiment analysis available", None, None, None, None

        # Handle uploaded_files
        for file in uploaded_files:
            if isinstance(file, tuple):
                file = file[0] if len(file) > 0 else None
            if file:
                file_path = save_uploaded_file(file)
                if file_path:
                    document_paths.append(file_path)
                    text = extract_text_from_pdf(file_path)
                    extracted_texts.append(text)
                else:
                    error_msg = f"Error: Invalid or unsupported file type for {getattr(file, 'name', 'unknown file')}."
                    chat_history.append({"role": "assistant", "content": error_msg})
                    return chat_history, error_msg, [], "No sentiment analysis available", None, None, None, None

        if not document_paths:
            error_msg = "Error: No valid PDF files were uploaded. Please ensure files are valid PDFs."
            chat_history.append({"role": "assistant", "content": error_msg})
            return chat_history, error_msg, [], "No sentiment analysis available", None, None, None, None

        chat_history.append({"role": "user", "content": f"Analyze the uploaded legal documents.\n\nAnalyzed {len(document_paths)} document(s)"})

        # Summarize documents
        summary = summarize_document(extracted_texts, legal_category)
        
        # Extract legal terms
        legal_terms = []
        for text in extracted_texts:
            legal_terms.extend(extract_legal_terms(text))
        legal_terms = list(set(legal_terms))  # Remove duplicates

        # Analyze sentiment
        combined_text = "\n".join(extracted_texts)
        sentiment = analyze_document_sentiment(combined_text)

        # Generate legal analysis
        response = analyze_legal_query_with_images(legal_category, "Analyze the uploaded legal documents.", [], document_paths, chat_history)
        if not response:
            logging.error("No response from legal analysis")
            chat_history.append({"role": "assistant", "content": "Error: Unable to generate legal analysis."})
            return chat_history, "Error in analysis", [], "No sentiment analysis available", None, None, None, None

        response_summary = summarize_text(response) if len(response.split()) > 200 else ""
        if response_summary:
            response = f"**Summary**: {response_summary}\n\n**Full Response**: {response}"
        chat_history.append({"role": "assistant", "content": response})

        # Save summary to file
        summary_file = save_text_to_file(summary, ".txt", "document_summary")

        # Generate PDF report
        pdf_report = generate_pdf_report("Analyze the uploaded legal documents.", response, chat_history, document_paths)
        if not pdf_report:
            logging.error("Failed to generate PDF report")
            chat_history.append({"role": "assistant", "content": "Error: Could not generate PDF report."})

        # Prepare text preview
        text_preview = "\n\n".join([f"Document {i+1}:\n{text[:500]}" for i, text in enumerate(extracted_texts)])
        text_preview = text_preview[:1000] + ("..." if len(text_preview) > 1000 else "")

        audio_response = speak_response(response)
        audio_button = gr.Button("Play Audio Response", visible=True)

        email_status = None
        if email_address:
            email_body = f"Document Analysis Summary:\n{summary}\n\nLegal Terms:\n{', '.join(legal_terms)}\n\nSentiment: {sentiment}\n\nFull Analysis:\n{response}"
            email_status = send_email(email_address, "VAKALAT Document Analysis", email_body, pdf_report)
            chat_history.append({"role": "assistant", "content": email_status})

        return chat_history, text_preview, legal_terms, sentiment, summary_file, pdf_report, audio_response, audio_button, email_status

    except Exception as e:
        logging.error(f"Error in handle_document_analysis: {e}")
        error_msg = f"Error analyzing documents: {str(e)}"
        chat_history.append({"role": "assistant", "content": error_msg})
        return chat_history, error_msg, [], "No sentiment analysis available", None, None, None, None, None

def play_document_analysis_audio(chat_history):
    if chat_history and isinstance(chat_history, list) and chat_history[-1].get("role") == "assistant":
        return speak_response(chat_history[-1]["content"])
    return None

def handle_mediation(parties, issue, desired_outcome, legal_category, email_address=None):
    chat_history = []
    try:
        if not parties or not issue or not desired_outcome:
            error_msg = "Error: Please provide all mediation details (parties, issue, desired outcome)."
            chat_history.append({"role": "assistant", "content": error_msg})
            return chat_history, None, None, None

        chat_history.append({"role": "user", "content": f"Mediation Request:\nParties: {parties}\nIssue: {issue}\nDesired Outcome: {desired_outcome}"})

        response = analyze_mediation(parties, issue, desired_outcome, legal_category)
        if not response:
            logging.error("No response from mediation analysis")
            chat_history.append({"role": "assistant", "content": "Error: Unable to generate mediation analysis."})
            return chat_history, None, None, None

        summary = summarize_text(response) if len(response.split()) > 200 else ""
        if summary:
            response = f"**Summary**: {summary}\n\n**Full Response**: {response}"
        chat_history.append({"role": "assistant", "content": response})

        agreement_file = generate_pdf_report(
            f"Mediation: {issue}", response, chat_history, [], title="Mediation Agreement"
        )
        if not agreement_file:
            logging.error("Failed to generate mediation agreement")
            chat_history.append({"role": "assistant", "content": "Error: Could not generate mediation agreement."})

        audio_response = speak_response(response)
        audio_button = gr.Button("Play Audio Response", visible=True)

        email_status = None
        if email_address:
            email_body = f"Mediation Details:\nParties: {parties}\nIssue: {issue}\nDesired Outcome: {desired_outcome}\n\nResponse:\n{response}"
            email_status = send_email(email_address, "VAKALAT Mediation Agreement", email_body, agreement_file)
            chat_history.append({"role": "assistant", "content": email_status})

        return chat_history, agreement_file, audio_response, audio_button, email_status

    except Exception as e:
        logging.error(f"Error in handle_mediation: {e}")
        error_msg = f"Error processing mediation: {str(e)}"
        chat_history.append({"role": "assistant", "content": error_msg})
        return chat_history, None, None, None, None

def play_mediation_audio(chat_history):
    if chat_history and isinstance(chat_history, list) and chat_history[-1].get("role") == "assistant":
        return speak_response(chat_history[-1]["content"])
    return None

def reset_document_analysis():
    return [], "", [], "No sentiment analysis available", None, None, None, None, None

def reset_mediation():
    return [], None, None, None, None

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("<h1 style='text-align: center;'>VAKALAT: Your Legal Assistant</h1>")
    
    with gr.Tabs():
        with gr.Tab("Legal Query"):
            legal_category = gr.Dropdown(choices=LEGAL_CATEGORIES, label="Select Legal Category", value="Other")
            audio_input = gr.Audio(
                sources=["microphone", "upload"],
                type="filepath",
                label="Record or Upload Your Legal Query"
            )
            text_input = gr.Textbox(label="Text Query (Optional Fallback)", placeholder="Type your query if audio is unavailable")
            file_input = gr.File(label="Upload Supporting Document (PDF or Image)", file_types=[".pdf", ".jpg", ".jpeg", ".png"])
            email_input = gr.Textbox(label="Email Address (Optional)", placeholder="Enter email to receive advice")
            submit_button = gr.Button("Submit Query")
            chatbot = gr.Chatbot(label="Legal Assistant Response", type="messages")
            pdf_output = gr.File(label="Download Legal Report (PDF)")
            audio_output = gr.Audio(label="Audio Response", type="filepath")
            audio_button = gr.Button("Play Audio Response", visible=False)
            email_status = gr.Textbox(label="Email Status", visible=False)
            
            submit_button.click(
                fn=transcribe_and_analyze,
                inputs=[audio_input, text_input, legal_category, file_input, email_input],
                outputs=[chatbot, pdf_output, audio_output, audio_button, email_status]
            )
            audio_button.click(
                fn=play_legal_query_audio,
                inputs=[chatbot],
                outputs=[audio_output]
            )

        with gr.Tab("Document Analyzer"):
            doc_legal_category = gr.Dropdown(choices=LEGAL_CATEGORIES, label="Select Legal Category", value="Other")
            doc_file_input = gr.File(label="Upload Documents (PDFs)", file_count="multiple", file_types=[".pdf"])
            doc_email_input = gr.Textbox(label="Email Address (Optional)", placeholder="Enter email to receive analysis")
            analyze_button = gr.Button("Analyze Documents")
            reset_button = gr.Button("Reset Analysis")
            doc_chatbot = gr.Chatbot(label="Document Analysis", type="messages")
            text_preview = gr.Textbox(label="Text Preview (Extracted from Documents)", lines=10)
            legal_terms = gr.Textbox(label="Extracted Legal Terms")
            sentiment = gr.Textbox(label="Document Sentiment")
            summary_file = gr.File(label="Download Summary (TXT)")
            doc_pdf_output = gr.File(label="Download Analysis Report (PDF)")
            doc_audio_output = gr.Audio(label="Audio Response", type="filepath")
            doc_audio_button = gr.Button("Play Audio Response", visible=False)
            doc_email_status = gr.Textbox(label="Email Status", visible=False)
            
            analyze_button.click(
                fn=handle_document_analysis,
                inputs=[doc_file_input, doc_legal_category, doc_email_input],
                outputs=[
                    doc_chatbot, text_preview, legal_terms, sentiment,
                    summary_file, doc_pdf_output, doc_audio_output, doc_audio_button, doc_email_status
                ]
            )
            reset_button.click(
                fn=reset_document_analysis,
                inputs=None,
                outputs=[
                    doc_chatbot, text_preview, legal_terms, sentiment,
                    summary_file, doc_pdf_output, doc_audio_output, doc_audio_button, doc_email_status
                ]
            )
            doc_audio_button.click(
                fn=play_document_analysis_audio,
                inputs=[doc_chatbot],
                outputs=[doc_audio_output]
            )

        with gr.Tab("Mediation"):
            med_legal_category = gr.Dropdown(choices=LEGAL_CATEGORIES, label="Select Legal Category", value="Other")
            parties_input = gr.Textbox(label="Parties Involved", placeholder="E.g., John Doe vs. Jane Smith")
            issue_input = gr.Textbox(label="Dispute Description", lines=5, placeholder="Describe the issue...")
            outcome_input = gr.Textbox(label="Desired Outcome", lines=3, placeholder="E.g., Mutual agreement on payment...")
            med_email_input = gr.Textbox(label="Email Address (Optional)", placeholder="Enter email to receive agreement")
            mediate_button = gr.Button("Analyze Mediation")
            reset_med_button = gr.Button("Reset Mediation")
            med_chatbot = gr.Chatbot(label="Mediation Analysis", type="messages")
            agreement_file = gr.File(label="Download Mediation Agreement (PDF)")
            med_audio_output = gr.Audio(label="Audio Response", type="filepath")
            med_audio_button = gr.Button("Play Audio Response", visible=False)
            med_email_status = gr.Textbox(label="Email Status", visible=False)
            
            mediate_button.click(
                fn=handle_mediation,
                inputs=[parties_input, issue_input, outcome_input, med_legal_category, med_email_input],
                outputs=[med_chatbot, agreement_file, med_audio_output, med_audio_button, med_email_status]
            )
            reset_med_button.click(
                fn=reset_mediation,
                inputs=None,
                outputs=[med_chatbot, agreement_file, med_audio_output, med_audio_button, med_email_status]
            )
            med_audio_button.click(
                fn=play_mediation_audio,
                inputs=[med_chatbot],
                outputs=[med_audio_output]
            )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", 7860)),
        share=True
    )