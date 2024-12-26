import ollama
from bs4 import BeautifulSoup
import requests
import pdfplumber
import io
# Data Sources for Recommendations and Context
data_sources = [
    "https://www.allen.ac.in/engineering/jee-main/tips-tricks",
    "https://motion.ac.in/blog/jee-main-weightage-chapter-wise",
    "https://www.allen.ac.in/engineering/jee-main/preparation-strategy",
    "https://byjus.com/jee/how-to-prepare-for-jee-at-home",
    "https://www.askiitians.com/iit-jee/how-to-prepare-for-iit-jee-from-class-11.html",
    "https://byjus.com/jee/complete-study-plan-to-crack-jee-main",
    "https://mystudycart.com/iit-jee-preparation",
    "https://engineering.careers360.com/articles/how-prepare-for-jee-main",
    "https://www.allenoverseas.com/blog/jee-main-2024-exam-strategies-subject-wise-preparation-tips",
    "'cs",
    "https://www.pw.live/exams/wp-content/uploads/2024/01/syllabus-for-jee-main-2024-as-on-01-november-2023-1-3.pdf",
    "https://www.pw.live/exams/wp-content/uploads/2024/01/syllabus-for-jee-main-2024-as-on-01-november-2023-4-8.pdf",
    "https://www.pw.live/exams/jee/jee-main-chemistry-syllabus",
    "https://www.pw.live/topics-chemistry-class-11",
    "https://www.pw.live/topics-chemistry-class-12",    
]
# Function to extract text from PDFs
def extract_text_from_pdf(url):
    try:
        response = requests.get(url, timeout=10)
        pdf_file = response.content
        with pdfplumber.open(io.BytesIO(pdf_file)) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    except Exception as e:
        return f"Error processing PDF {url}: {e}"
    # Retrieve external context dynamically
def retrieve_context(query):
    context = ""
    for url in data_sources:
        if url.endswith(".pdf"):
            context += extract_text_from_pdf(url)
        else:
            try:
                response = requests.get(url, timeout=10)
                soup = BeautifulSoup(response.content, "html.parser")
                paragraphs = soup.find_all("p")
                for para in paragraphs[:5]:  # Limit to first 5 paragraphs
                    context += para.text.strip() + "\n"
            except Exception as e:
                context += f"Error fetching content from {url}: {e}\n"
    return f"Query: {query}\n{context[:1000]}"  # Limit context size to 1000 characters
# List of questions for SOCA analysis
soca_questions = [
    "How confident are you in solving problems in the following subjects? (Rate each out of 10):\n- Physics\n- Chemistry\n- Mathematics",
    "Which specific topics or chapters in these subjects do you feel most confident about?",
    "Are there any topics or chapters you find particularly challenging? If yes, please list them.",
    "How do you manage your time while studying for JEE?",
    "What is your usual approach to solving multi-step or complex problems?",
    "Do you often get distracted while studying? If yes, how do you refocus?",
    "Describe your study schedule. Do you follow a consistent plan, or is it irregular?",
    "How do you balance coaching classes with self-study?",
    "How often do you take mock tests or solve previous years' question papers?",
]
# Function to ask SOCA questions interactively
def ask_soca_questions():
    answers = []
    print("Let's begin the SOCA analysis. Please answer the following questions:\n")
    for i, question in enumerate(soca_questions):
        print(f"Q{i + 1}: {question}")
        answer = input("Your Answer: ")
        answers.append({"question": question, "answer": answer})
    return answers
# Function to generate SOCA analysis
def generate_soca_analysis(answers):
    context_query = "Effective strategies for JEE preparation"
    context = retrieve_context(context_query)
    user_responses = "\n".join([f"Q: {item['question']}\nA: {item['answer']}" for item in answers])
    prompt = f"""
            You are an advanced assistant tasked with analyzing a student's preparation for JEE.
            Based on the following external context retrieved from reliable sources:
            {context}

            The student's input is as follows:
            {user_responses}

            Generate a detailed SCO (Strengths, Challenges, Opportunities) analysis and a tailored Action Plan for their JEE preparation.
            """

    # Generate response using the model
    stream = ollama.chat(
        model="mistral",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )
    response = ""
    print("\n\nSOCA Analysis:")
    for chunk in stream:
        print(chunk["message"]["content"], end="")
        response += chunk["message"]["content"]
    return response
# Main function
def main():
    print("Welcome to the AI-Driven JEE Preparation Assistant!")
    print("You can ask questions, request recommendations, or ask for an SOCA analysis.\n")
    
    while True:
        user_input = input("You: ")

        # Exit condition
        if user_input.lower() in ["exit", "quit"]:
            print("Assistant: Goodbye! Best of luck with your JEE preparation!")
            break

        # Check if the user wants an SOCA analysis
        elif "soca analysis" in user_input.lower():
            answers = ask_soca_questions()
            print("\nGenerating SOCA analysis...\n")
            soca_output = generate_soca_analysis(answers)
            print("\nSOCA Analysis Generated Successfully.")

        else:
            # Handle general queries and provide recommendations or insights
            context = retrieve_context(user_input)
            response = chat_with_model(context, user_input)
            print(f"Assistant: {response}")
# Chat with model function (as used in the main chatbot)
def chat_with_model(context, user_input):
    context_history = [
        {"role": "system", "content": "You are an AI assistant specialized in JEE preparation guidance."},
        {"role": "user", "content": user_input},
        {"role": "assistant", "content": "Here are some resources and suggestions to help you with your preparation."}
    ]
    # Generate response using the model
    stream = ollama.chat(
        model="mistral",
        messages=context_history,
        stream=True
    )
    response = ""
    for chunk in stream:
        response += chunk["message"]["content"]
    return response

# Run the program
if __name__ == "__main__":
    main()
