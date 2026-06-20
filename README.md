A web-based AI-powered plagiarism detection system that detects both copied/paraphrased content and ChatGPT-generated text in student assignments using transformer-based NLP models.

🚀 Live Demo: https://huggingface.co/spaces/Deepthi832/plagiarism-detection

📌 Features

✅ Semantic Plagiarism Detection — Uses Sentence-BERT + Cosine Similarity to detect paraphrased content (not just copy-paste)
🤖 AI Content Detection — Identifies ChatGPT-generated text using phrase analysis, perplexity scoring, and sentence uniformity checks
📄 Multi-Format Support — Accepts PDF, DOCX, and TXT files
👤 Role-Based Access — Separate interfaces for Students and Instructors
📊 Instructor Dashboard — View all submissions with plagiarism %, AI verdict, and IST timestamps
🎯 Color-Coded Reports — Green (0-24%), Yellow (25-49%), Orange (50-74%), Red (75%+)
☁️ Cloud Deployed — Hosted on Hugging Face Spaces using Docker

⚙️ Local Setup
1. Clone the repository : 
git clone https://github.com/saideepthi832-boop/plagiarism_detection.git
cd plagiarism_detection

3. Create virtual environment :
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac

5. Install dependencies :
pip install -r requirements.txt

7. Run the application :
python run.py

9. Open in browser :
http://127.0.0.1:5000

👥 User Roles

🎓 Student

-Register and login

-Upload assignment (PDF / DOCX / TXT)

-Get instant plagiarism % and AI detection verdict

👩‍🏫 Instructor

-Login with instructor role

-View all student submissions

-Monitor plagiarism %, AI verdict, timestamps

🔬 Algorithms Used

Sentence-BERT  :  Generate semantic sentence embeddings

Cosine Similarity  :  Compare embeddings to find similarity

Perplexity Scoring  :  Detect AI-generated text patterns

Phrase Detection  :  Identify ChatGPT-specific vocabulary

Sentence Uniformity  :  Detect AI writing structure patterns

🐳 Docker Deployment

Dockerfile

FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt 

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p database uploads

EXPOSE 7860

CMD ["python", "run.py"]

🚀 Live Demo

Try the live application here:

👉 https://huggingface.co/spaces/Deepthi832/plagiarism-detection

Test credentials:

Register as a Student to upload assignments

Register as an Instructor to view the dashboard


📄 License

This project is licensed under the MIT License.
