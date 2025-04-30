# Import necessary libraries

import json
import pandas as pd
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge import Rouge
import nltk
import code_bert_score



# Download necessary NLTK data
nltk.download("punkt", quiet=True)

# Define a class to evaluate QA performance using BLEU, ROUGE, and CodeBERT
class QAEvaluator:
    def __init__(self):
        # Initialize ROUGE scorer
        self.rouge = Rouge()
        # Smoothing function for BLEU score
        self.smooth = SmoothingFunction().method1

    # Main evaluation method
    def evaluate(self, qa_pairs):
        results = [] # Stores evaluation results for each QA pair
        predictions = [] # List of predicted answers
        references = [] # List of reference answers

        # Extract prediction, reference answer, and the question
        for qa in qa_pairs:
            prediction = qa.get("answer", "")
            reference = qa.get("reference", "")
            question = qa.get("question", "")

            predictions.append(prediction)
            references.append(reference)

            # Compute BLEU score with smoothing
            bleu = sentence_bleu(
                [reference.split()],
                prediction.split(),
                smoothing_function=self.smooth
            )
            # Compute ROUGE scores
            rouge_scores = self.rouge.get_scores(prediction, reference)[0]

            # Append result dictionary for this QA pair
            results.append({
                "question": question,
                "prediction": prediction,
                "reference": reference,
                "bleu": bleu,
                "rouge-1": rouge_scores["rouge-1"]["f"],
                "rouge-2": rouge_scores["rouge-2"]["f"],
                "rouge-l": rouge_scores["rouge-l"]["f"],
            })

            # Compute CodeBERT scores 
            pred_results =code_bert_score.score(cands=predictions, refs=references, lang='python')

             # Append CodeBERT score to each result
        for i, r in enumerate(results):
            r["codebert"] = pred_results[0][i]  # Extracting codebert score for each result

        return results

# #  Load JSON file
# with open("LLM_generated_v1.json", "r", encoding="utf-8") as f:
#     qa_pairs = json.load(f)

# # Instantiate evaluator and evaluate the QA pairs
# evaluator = QAEvaluator()
# results = evaluator.evaluate(qa_pairs)

# #  Print sample results 
# for r in results:
#     print("\nQ:", r["question"])
#     print("Prediction:", r["prediction"])
#     print("Reference:", r["reference"])
#     print("BLEU:", round(r["bleu"], 4), "| ROUGE-L:", round(r["rouge-l"], 4), "| CodeBert:", r["codebert"])

# #  Optional: Save to CSV
# pd.DataFrame(results).to_csv("qa_evaluation_results.csv", index=False)
# print("\nEvaluation saved to 'qa_evaluation_results.csv'")

