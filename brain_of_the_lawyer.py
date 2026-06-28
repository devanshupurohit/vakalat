import fitz  # PyMuPDF
from groq import Groq
import logging
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os
from PIL import Image
import io
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
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

def extract_text_from_pdf(pdf_path: str) -> str:
    try:
        # Validate PDF header
        with open(pdf_path, 'rb') as f:
            header = f.read(4)
            if not header.startswith(b'%PDF'):
                logging.error("PDF Extraction Error: Invalid PDF header")
                return "Error: Invalid PDF file"
        
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        logging.info(f"Extracted text from PDF: {pdf_path}, length: {len(text)}")
        return text if text else "No text extracted from PDF."
    except Exception as e:
        logging.error(f"PDF Extraction Error: {e}")
        return f"Error reading PDF: {str(e)}"

def analyze_legal_query_with_images(category: str, query: str, image_paths: list, document_paths: list, chat_history: list) -> str:
    try:
        context = f"Legal Category: {category}\n\n"
        for path in document_paths:
            text = extract_text_from_pdf(path)
            context += f"Document Content: {text}\n\n"
        
        for path in image_paths:
            try:
                with Image.open(path) as img:
                    context += f"Image Description: {describe_image(img)}\n\n"
            except Exception as e:
                logging.error(f"Error processing image {path}: {e}")
                context += f"Image Description: Error processing image\n\n"
        
        messages = [
            {"role": "system", "content": "You are a legal assistant providing accurate and concise legal advice. Use the provided context and chat history to respond."},
        ] + chat_history + [{"role": "user", "content": f"Query: {query}\n\nContext: {context}"}]
        
        logging.info("Sending legal analysis request to Groq...")
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Error in legal analysis: {e}")
        return f"Error analyzing query: {str(e)}"

def describe_image(image: Image.Image) -> str:
    return "Image analysis not implemented."

def summarize_document(texts: list, category: str) -> str:
    try:
        combined_text = "\n".join(texts)
        if not combined_text.strip():
            return "No text available to summarize."
        
        messages = [
            {"role": "system", "content": f"You are a legal assistant summarizing documents in the {category} category. Provide a concise summary (100-200 words)."},
            {"role": "user", "content": f"Summarize the following documents:\n\n{combined_text}"}
        ]
        
        logging.info("Sending document summary request to Groq...")
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Error summarizing document: {e}")
        return f"Error summarizing document: {str(e)}"

def summarize_text(text: str) -> str:
    try:
        if len(text.split()) <= 200:
            return ""
        
        messages = [
            {"role": "system", "content": "You are a legal assistant summarizing legal advice. Provide a concise summary (50-100 words)."},
            {"role": "user", "content": f"Summarize the following text:\n\n{text}"}
        ]
        
        logging.info("Sending text summary request to Groq...")
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Error summarizing text: {e}")
        return f"Error summarizing text: {str(e)}"

def extract_legal_terms(text: str) -> list:
    try:
        messages = [
            {"role": "system", "content": "You are a legal assistant extracting key legal terms from text. Return a list of terms."},
            {"role": "user", "content": f"Extract legal terms from:\n\n{text}"}
        ]
        
        logging.info("Sending legal terms extraction request to Groq...")
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            max_tokens=500
        )
        terms = response.choices[0].message.content.strip().split("\n")
        return [term.strip() for term in terms if term.strip()]
    except Exception as e:
        logging.error(f"Error extracting legal terms: {e}")
        return []

def analyze_document_sentiment(text: str) -> str:
    try:
        messages = [
            {"role": "system", "content": "You are a legal assistant analyzing document sentiment. Return 'Positive', 'Negative', 'Neutral', or 'Mixed' with a brief explanation."},
            {"role": "user", "content": f"Analyze the sentiment of:\n\n{text}"}
        ]
        
        logging.info("Sending sentiment analysis request to Groq...")
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Error analyzing sentiment: {e}")
        return f"Error analyzing sentiment: {str(e)}"

def analyze_mediation(parties: str, issue: str, desired_outcome: str, category: str) -> str:
    try:
        messages = [
            {"role": "system", "content": f"You are a legal assistant specializing in mediation for {category} disputes. Provide a mediation analysis, suggested resolution steps, and a draft agreement."},
            {"role": "user", "content": f"Parties: {parties}\nIssue: {issue}\nDesired Outcome: {desired_outcome}"}
        ]
        
        logging.info("Sending mediation analysis request to Groq...")
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Error in mediation analysis: {e}")
        return f"Error analyzing mediation: {str(e)}"

def generate_pdf_report(query: str, response: str, chat_history: list, document_paths: list, title: str = "Legal Report") -> str:
    try:
        from utils import create_temp_file
        pdf_path = create_temp_file(".pdf")
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        story.append(Paragraph(title, styles['Title']))
        story.append(Spacer(1, 12))
        
        story.append(Paragraph("Query:", styles['Heading2']))
        story.append(Paragraph(query, styles['Normal']))
        story.append(Spacer(1, 12))
        
        story.append(Paragraph("Response:", styles['Heading2']))
        story.append(Paragraph(response, styles['Normal']))
        story.append(Spacer(1, 12))
        
        if chat_history:
            story.append(Paragraph("Chat History:", styles['Heading2']))
            for msg in chat_history:
                role = msg['role'].capitalize()
                content = msg['content']
                story.append(Paragraph(f"{role}: {content}", styles['Normal']))
                story.append(Spacer(1, 6))
        
        if document_paths:
            story.append(Paragraph("Documents Analyzed:", styles['Heading2']))
            for path in document_paths:
                story.append(Paragraph(os.path.basename(path), styles['Normal']))
                story.append(Spacer(1, 6))
        
        doc.build(story)
        logging.info(f"PDF report generated: {pdf_path}")
        return pdf_path
    except Exception as e:
        logging.error(f"Error generating PDF report: {e}")
        return None