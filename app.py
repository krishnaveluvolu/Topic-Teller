from flask import Flask, render_template, request, send_file, redirect, url_for
import google.generativeai as genai
from fpdf import FPDF
import os

app = Flask(__name__)

# ✅ Configure Gemini API Key
API_KEY = "AIzaSyBYt5tFEDXiIr4mH1dY0d2fHvHkv4ZNVH4"
genai.configure(api_key=API_KEY)

# ✅ Load Gemini Model
model = genai.GenerativeModel("models/gemini-1.5-flash")

generated_data = ""  # Stores the latest generated content

def generate_topic_info(topic):
    prompt = f"""
    Provide detailed structured information about the topic: "{topic}".
    Format it like this:

    🔹 Definition:
    🔹 History:
    🔹 Types:
    🔹 Examples:
    🔹 RealTimeExamples:
    🔹 Functionalities:
    🔹 Advantages:
    🔹 Disadvantages:
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Error from Gemini API: {str(e)}"

# ✅ Updated: Save as PDF with special character handling
def save_to_pdf(text):
    # Replace special characters that FPDF can't handle
    clean_text = text.replace("🔹", "-")  # Replace bullet emoji with simple dash
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    # Safely write each line to PDF
    for line in clean_text.split('\n'):
        try:
            pdf.multi_cell(0, 10, txt=line)
        except:
            pdf.multi_cell(0, 10, txt="[Unsupported characters removed]")

    filepath = os.path.join("static", "topic_info.pdf")
    pdf.output(filepath)
    return filepath

@app.route('/', methods=['GET', 'POST'])
def index():
    global generated_data
    result = ""
    topic = ""

    if request.method == 'POST':
        topic = request.form['topic']
        result = generate_topic_info(topic)
        generated_data = result
    return render_template('index.html', result=result, topic=topic)

@app.route('/regenerate', methods=['POST'])
def regenerate():
    topic = request.form['topic']
    result = generate_topic_info(topic)
    global generated_data
    generated_data = result
    return render_template('index.html', result=result, topic=topic)

# ✅ Fixed: Handle Unicode and provide safe file download
@app.route('/download', methods=['POST'])
def download():
    if not generated_data:
        return redirect(url_for('index'))
    
    filepath = save_to_pdf(generated_data)
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists("static"):
        os.makedirs("static")
    app.run(debug=True)
