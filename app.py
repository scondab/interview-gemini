import streamlit as st
import google.generativeai as genai
import PyPDF2
import io
import os

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the config.py file in the same directory
config_path = os.path.join(current_dir, 'config.py')

# Use exec to load the GOOGLE_API_KEY from config.py
try:
    with open(config_path, 'r') as config_file:
        exec(config_file.read())
except FileNotFoundError:
    st.error(f"Config file not found at {config_path}. Please create a config.py file with your GOOGLE_API_KEY.")
    st.stop()

# Now GOOGLE_API_KEY should be available
if 'GOOGLE_API_KEY' not in locals():
    st.error("GOOGLE_API_KEY not found in config.py. Please make sure it's defined correctly.")
    st.stop()

# Configure the Gemini Pro model
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def get_ai_response(prompt):
    response = model.generate_content(prompt)
    return response.text

def main():
    st.markdown("""
    <style>
    .big-font {
        font-size:50px !important;
        color: #1E90FF;
        text-align: center;
    }
    .medium-font {
        font-size:30px !important;
        color: #4682B4;
    }
    .small-font {
        font-size:14px !important;
        color: #4169E1;
    }
    .stTextInput > div > div > input {
        color: #4682B4;
    }
    .stTextArea > div > div > textarea {
        color: #4682B4;
    }
    .stButton>button {
        color: #4682B4;
        border-radius: 20px;
        border: 2px solid #4682B4;
        background-color: white;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #4682B4;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="big-font">AI Job Interview Coach</p>', unsafe_allow_html=True)

    # Job Description Input
    st.markdown('<p class="medium-font">Job Description</p>', unsafe_allow_html=True)
    job_description = st.text_area("Enter the job description:", height=200)

    # Company Website Input
    st.markdown('<p class="medium-font">Company Website Info</p>', unsafe_allow_html=True)
    company_website = st.text_area("Enter the company's website Info:", height=200)

    # Resume Upload
    st.markdown('<p class="medium-font">Your Resume</p>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type="pdf")

    if uploaded_file is not None:
        resume_text = extract_text_from_pdf(uploaded_file)
    else:
        resume_text = ""

    if st.button("Start Interview", key="start_interview"):
        if job_description and company_website and resume_text:
            st.session_state.interview_started = True
            st.session_state.question_count = 0
            st.session_state.conversation = []

            with st.spinner('Preparing your interview...'):
                initial_prompt = f"""
                Act like a professional job interview coach.

                You will help me prepare for my next job interview by simulating a complex, realistic & tricky job interview. 

                First step: you need to know, master & be an expert of the position itself and the company I apply to. 

                Here's the job description:

                {job_description}

                Here's the company's website about us section:

                {company_website}

                Step 2: Write a quick summary of your learnings, and who you have to become in order to be my job interviewer.

                Step 3: Read my resume / CV:

                {resume_text}

                Step 4: Start the job interview, one question at a time, like a real simulation.
                """

                response = get_ai_response(initial_prompt)
                st.session_state.conversation.append(("AI", response))
            st.experimental_rerun()

    if 'interview_started' in st.session_state and st.session_state.interview_started:
        st.markdown('<p class="medium-font">Interview Simulation</p>', unsafe_allow_html=True)

        for speaker, message in st.session_state.conversation:
            if speaker == "AI":
                st.markdown(f'<p class="small-font"><b>Interviewer:</b> {message}</p>', unsafe_allow_html=True)
            else:
                st.markdown(f'<p class="small-font"><b>You:</b> {message}</p>', unsafe_allow_html=True)

        user_response = st.text_area("Your response:", key=f"response_{st.session_state.question_count}")

        if st.button("Submit Response", key="submit_response"):
            st.session_state.conversation.append(("You", user_response))

            with st.spinner('Analyzing your response...'):
                feedback_prompt = f"""
                Based on the previous conversation and the following user response, provide feedback and the next question:

                User response: {user_response}

                Provide 5 paragraphs, divided by line breaks:

                Paragraph 1 = What was good in my answer?
                Paragraph 2 = What was bad in my answer?
                Paragraph 3 = What could be added to my answer?
                Paragraph 4 = Pretend you are me & write a detailed perfect answer using the CARL method.
                Paragraph 5 = Ask me if we can move on to the next interview question.
                """

                response = get_ai_response(feedback_prompt)
                st.session_state.conversation.append(("AI", response))
            st.session_state.question_count += 1
            st.experimental_rerun()

def extract_text_from_pdf(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.getvalue()))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

if __name__ == "__main__":
    main()