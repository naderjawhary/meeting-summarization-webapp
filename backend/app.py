from flask import Flask, render_template, request, send_file
import os
import whisperx
import time
import torch
from openai import OpenAI
import re
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Configuration for WhisperX
device = "cuda" if torch.cuda.is_available() else "cpu"
compute_type = "int8"
# Load default WhisperX model (will be overridden per user selection)
model = whisperx.load_model("large-v2", device, compute_type=compute_type)

# Setup OpenAI client for summarization via LiteLLM-compatible endpoint
api_key = "sk-hfB7vnN41tjgRAMcxltPwg"
base_url = "https://litellm.s.studiumdigitale.uni-frankfurt.de/v1/"
client = OpenAI(api_key=api_key, base_url=base_url)

latest_summary = ""

@app.route("/", methods=["GET", "POST"])
# Main route for both GET and POST requests
# Handles two main operations:
# 1. Audio transcription: allows user to upload audio and select a WhisperX model to convert speech to text
# 2. Summarization: sends the transcript to a language model with a structured prompt to generate a summary
# Returns the rendered HTML template with transcript and/or summary
def upload_file():
    global latest_summary
    transcript = None
    summary = None

    if request.method == "POST":
        action = request.form.get("action")

        # ---- SUMMARIZATION ----
        if action == "summarize":
            edited = request.form["edited_transcript"]

            summary_prompt = f"""
You are an AI assistant helping with summarizing audio meetings in educational settings. Your task is to create an accurate, well-structured summary of the following transcript. Please produce a summary of approximately 1000 words.

The transcript may include discussions between instructors, students, administrators, or other educational stakeholders.

Create your summary with the following structure:
- Meeting title, date, and participants (if provided)
- Brief overview of the meeting's purpose and key outcomes (3–5 sentences)
- Main discussion topics in chronological order
- Key decisions or agreements reached
- Notable questions raised during the discussion
- Action items or next steps mentioned
- Areas of consensus and disagreement

Include a final section that analyzes the main themes of the discussion, identifying:
- Central arguments presented
- Supporting evidence or examples mentioned
- Counterpoints or alternative perspectives raised
- Unresolved issues requiring further discussion

The summary should be written in clear, academic language and organized into readable sections. Use bullet points to highlight specific points when appropriate. Direct quotes should be formatted with quotation marks and italics, but use them sparingly and only when they capture a critical point that paraphrasing would not convey effectively.

IMPORTANT: Only include information explicitly stated in the transcript. Do not add interpretations, assumptions, or external information not present in the original discussion.

Here is the transcript:

{...}


{edited}
"""
            # Send request to summarization model
            response = client.chat.completions.create(
                model="deepseek-r1-distill-llama-70b",
                messages=[{"role": "user", "content": summary_prompt}],
                temperature=0.5,
                timeout=360
            )

            # Extract and clean the output
            raw_output = response.choices[0].message.content

            # Remove <think>...</think> blocks completely
            clean_summary = re.sub(r"<think>.*?</think>", "", raw_output, flags=re.DOTALL)

            # Also remove stray '</think>' and preceding thought-like content if no matching <think> was found
            clean_summary = re.sub(r"(?:^|\n).*?</think>\n?", "", clean_summary, flags=re.DOTALL)

            # Remove excessive line breaks
            clean_summary = re.sub(r"\n\s*\n", "\n\n", clean_summary).strip()

            latest_summary = clean_summary

            return render_template("upload.html", transcript=edited, summary=clean_summary)

        # ---- TRANSCRIPTION ----
        else:
            # Get model selection from form (default to large-v2)
            model_choice = request.form.get("model_choice", "large-v2")

            # Load the selected WhisperX model
            model = whisperx.load_model(model_choice, device, compute_type=compute_type)

            file = request.files["audio"]
            if file:
                # Save the uploaded audio file to the server's upload folder
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
                file.save(filepath)

                # Load the audio file into a format WhisperX can process
                audio = whisperx.load_audio(filepath)
                start = time.time()
                # Transcribe the audio using the selected WhisperX model
                result = model.transcribe(audio, batch_size=8)
                end = time.time()
                
                """
                #THIS SECTION IS USEFUL IF WE WANT TO USE DIARIZATION (IMPROVES TIMESTAMP ACCURACY; WORD-BASED)
                # Load alignment model to improve word-level timestamp accuracy
                model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
                # Align the transcribed segments with the audio
                result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)
                """
                # Combine all segments into one full transcript string
                transcript = "\n".join([seg["text"] for seg in result["segments"]])
                # Render the template with the generated transcript
                return render_template("upload.html", transcript=transcript, audio_file=file.filename)
                
    return render_template("upload.html")


@app.route("/download")
def download_pdf():
    summary = request.args.get("summary", "")

    # Define absolute path for PDF output
    downloads_dir = os.path.join(os.path.dirname(__file__), "downloads")
    os.makedirs(downloads_dir, exist_ok=True)
    output_path = os.path.join(downloads_dir, "summary.pdf")

    # Create PDF with ReportLab for better formatting
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles for different heading levels
    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=12,
        textColor='black',
        fontName='Helvetica-Bold'
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10,
        textColor='black',
        fontName='Helvetica-Bold'
    )
    
    heading3_style = ParagraphStyle(
        'CustomHeading3',
        parent=styles['Heading3'],
        fontSize=12,
        spaceAfter=8,
        textColor='black',
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        alignment=TA_JUSTIFY
    )
    
    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=styles['Normal'],
        fontSize=11,
        leftIndent=20,
        spaceAfter=4
    )
    
    numbered_style = ParagraphStyle(
        'NumberedStyle',
        parent=styles['Normal'],
        fontSize=11,
        leftIndent=20,
        spaceAfter=4
    )
    
    # Process the summary line by line
    lines = summary.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if not line:
            elements.append(Spacer(1, 12))
            i += 1
            continue
        
        # Remove markdown headers and format appropriately
        if line.startswith('#### '):
            text = line[5:].strip()
            # Replace markdown bold with HTML
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
            elements.append(Paragraph(text, heading3_style))
            elements.append(Spacer(1, 8))
        elif line.startswith('### '):
            text = line[4:].strip()
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
            elements.append(Paragraph(text, heading3_style))
            elements.append(Spacer(1, 8))
        elif line.startswith('## '):
            text = line[3:].strip()
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
            elements.append(Paragraph(text, heading2_style))
            elements.append(Spacer(1, 10))
        elif line.startswith('# '):
            text = line[2:].strip()
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
            elements.append(Paragraph(text, heading1_style))
            elements.append(Spacer(1, 12))
        elif line.startswith(('- ', '* ')):
            # Handle bullet points
            text = line[2:].strip()
            # Replace markdown bold with HTML
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
            elements.append(Paragraph(f"• {text}", bullet_style))
            elements.append(Spacer(1, 4))
        elif re.match(r'^\d+\.\s', line):
            # Handle numbered lists
            # Replace markdown bold with HTML
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
            elements.append(Paragraph(text, numbered_style))
            elements.append(Spacer(1, 4))
        else:
            # Regular paragraph
            # Replace markdown bold with HTML
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
            elements.append(Paragraph(text, normal_style))
            elements.append(Spacer(1, 6))
        
        i += 1
    
    # Build PDF
    doc.build(elements)

    return send_file(output_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)