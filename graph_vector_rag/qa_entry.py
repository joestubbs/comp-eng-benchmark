# Warning control
import warnings
warnings.filterwarnings("ignore")
from chat_with_graph import *
# import textwrap4


qa_chain = qa_with_source("sentences")
#qa_chain = qa_with_source1("sentences")

# Open config Read questions from a file:
with open("../tapis/benchmark/qa_evaluator/config.json", "r", encoding="utf-8") as cfg:
    config = json.load(cfg)
qa_sets_path = config['qa_sets_path']
qa_sets_output_path = qa_sets_path.split(".json")[0] + "-tapis-llm-out.json"

print(f"Reading input from file: {qa_sets_path}")
with open(qa_sets_path, "r", encoding="utf-8") as f:
    qa_sets = json.load(f)

questions_answers=[]
for qa in qa_sets:
    question = qa.get("question", "")
    response = qa_chain.invoke(question)
    answer = response["answer"]
    qa["answers"] = answer 
    questions_answers.append(qa)

# write the outputs to a file
print(f"Writing output to file: {qa_sets_output_path}")
with open(qa_sets_output_path, 'w') as f:
    json.dump(questions_answers, f)




# Hard coded questions ---
# questions=["How do you get a Tapis Token?",
#             # "Give me PySDK for Tapis Token",
#             # "Give me CURL command for Tapis Token",
#             #  "What is a Tapis Site?"
#             # "What is a Tapis JWT and what is its primary function in the Tapis ecosystem?",
#             # "How to list tenants in Tapis using a Python client?",
#             # "How to list tenants in Tapis using cURL?"
#           ]

# for question in questions:
#     response = qa_chain.invoke(question)
#     questions_answers.append({"response":{"question":response['question'], "answer":response['answer'], "source":response["sources"]}})
#     print("Question: " + question + "\n")
#     print(textwrap.fill(response['answer'], 100)) 
#     print("\n")
#print(questions_answers)