import streamlit as st
import os
import PyPDF2 as pdf
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def getGeminiResponse(input):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input)
    return response.text  # Ensure we return response.text directly

def inputPDFText(uploadedFile):
    reader = pdf.PdfReader(uploadedFile)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text()) if page.extract_text() else ""
    return text

geminiPrompt = """
You are an experienced HR Manager with a strong background in Tech Recruiting, especially for Full Stack web development, data science, software engineering, big data engineering, DevOps, Data Analyst, and Machine Learning Engineering roles.

1. Extract technical skills, soft skills, education details, and experience/project information directly from the resume. Ensure to include only the information explicitly stated in the resume for each category.
2. Scrutinize the resume in light of the job description provided. Generate a table that illustrates the match between them. Use cues to represent areas of high, medium, and low match, highlighting both strengths and weaknesses.
3. Identify keywords and skills mentioned in the job description that are absent from the resume. Prioritize these keywords and skills based on their frequency and relevance to the job. Provide suggestions for integrating these keywords into the resume, emphasizing achievements and quantifiable results.
4. Calculate the overall match percentage between the resume and the job description. Break down the percentage match by categories such as technical skills, soft skills, education, and experience. Highlight areas with high match percentages and suggest improvements for areas with low match percentages.

Job Description of Job in hand: {jobDesc}

Format your response as follows:
Profile Summary:
<Extracted Profile Summary>

Missing Keywords:
<Comma-separated list of missing keywords>

Job Description Match:
Total Match Percentage: <Total Match Percentage>%

| Category        | Match Percentage | Breakdown                                  | Strengths                                    | Weaknesses                                    |
|-----------------|------------------|--------------------------------------------|---------------------------------------------|----------------------------------------------|
| Technical Skills| <Percentage>%    | <Breakdown>                                | <Strengths>                                  | <Weaknesses>                                  |
| Soft Skills     | <Percentage>%    | <Breakdown>                                | <Strengths>                                  | <Weaknesses>                                  |
| Education       | <Percentage>%    | <Breakdown>                                | <Strengths>                                  | <Weaknesses>                                  |
| Experience      | <Percentage>%    | <Breakdown>                                | <Strengths>                                  | <Weaknesses>                                  |

Resume Content:
{text}
"""

# Streamlit Application

st.set_page_config(page_title="ResuMaster | ATS Resume Reviewer")
st.title("ResuMaster")
st.text("By Hamza Luay Kurdi, 2024.")
st.markdown("""
Please provide a detailed job description including:
- The technical and soft skills required
- Educational qualifications
- Specific experience sought
""")
jobDesc = st.text_area("Job Description: ", key="input")
uploadedFile = st.file_uploader("Upload Your Resume (PDF Format)", type="pdf", help="Please upload your resume in PDF format here.")

if uploadedFile is not None:
    st.write("PDF Uploaded Successfully")

submitButton = st.button("Submit")
if submitButton:
    if uploadedFile is not None:
        with st.spinner("Processing your resume..."):
            text = inputPDFText(uploadedFile)
            formattedPrompt = geminiPrompt.format(text=text, jobDesc=jobDesc)
            responseText = getGeminiResponse(formattedPrompt)
        
        profileSummary = ""
        keyWords = ""
        jdMatch = ""
        
        if "Profile Summary:" in responseText:
            profileSummary = responseText.split("Profile Summary:")[1].split("Missing Keywords:")[0].strip()
            profileSummary = profileSummary.replace('**', '')
        if "Missing Keywords:" in responseText:
            keyWords = responseText.split("Missing Keywords:")[1].split("Job Description Match:")[0].strip()
            keyWords = keyWords.replace('**', '').replace('\n', '').split(',')
            keyWords = ', '.join([kw.strip() for kw in keyWords])
            st.session_state['keyWords'] = keyWords

        if "Job Description Match:" in responseText:
            jdMatch = responseText.split("Job Description Match:")[1].split("Resume Content:")[0].strip()
            jdMatch = jdMatch.replace('**', '')

        st.subheader("Profile Summary")
        st.markdown(profileSummary if profileSummary else "Not found")
        st.subheader("Missing Keywords")
        st.markdown(keyWords.split(', ') if keyWords else "Not found")
        st.subheader("Job Description Match:")
        st.markdown(jdMatch if jdMatch else "Not found")
    else:
        st.write("Error: Please upload your resume in PDF format.")
else:
    st.write("Please upload your resume in PDF format.")
