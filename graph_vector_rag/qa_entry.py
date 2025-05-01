# Warning control
import warnings
warnings.filterwarnings("ignore")
from chat_with_graph import *
import textwrap

qa_chain = qa_with_source("sentences")
#qa_chain = qa_with_source1("sentences")

questions=["How do you get a Tapis Token?",
            "Give me PySDK for Tapis Token",
            "Give me CURL command for Tapis Token",
             "What is a Tapis Site?"
            "What is a Tapis JWT and what is its primary function in the Tapis ecosystem?",
            "How to list tenants in Tapis using a Python client?",
            "How to list tenants in Tapis using cURL?"
          ]
questions_answers=[]
for question in questions:
    response = qa_chain.invoke(question)
    #response = qa_chain.invoke({"input":question})
    
    
    #questions_answers.append({"response":response})
    #questions_answers.append({"response":{"question":response['input'], "answer":response['answer']}})
    questions_answers.append({"response":{"question":response['question'], "answer":response['answer'], "source":response["sources"]}})
    print("Question: " + question + "\n")
    print(textwrap.fill(response['answer'], 100)) 
    print("\n")
#print(questions_answers)