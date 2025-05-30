# Import necessary libraries

import json
import pandas as pd
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge import Rouge
import nltk
import code_bert_score
import openai
from dotenv import load_dotenv
import os
import re 
from openai import OpenAI

load_dotenv()  # Loads variables from .env into environment

# Download necessary NLTK data
nltk.download("punkt", quiet=True)

# Define a class to evaluate QA performance using BLEU, ROUGE, and CodeBERT
class QAEvaluator:
    def __init__(self, model_name="gpt-4", use_llm_judge=True, use_ollama=False):
        # Initialize ROUGE scorer
        self.model_name = model_name
        self.use_llm_judge = use_llm_judge
        self.rouge = Rouge()
        # Smoothing function for BLEU score
        self.smooth = SmoothingFunction().method1
        # Create OpenAI/Ollama client
        if use_ollama:
            base_url = os.getenv("OLLAMA_BASE_URL")
            self.client = OpenAI(base_url=base_url, api_key="ollama")
        else:
            api_key = os.getenv("OPENAI_API_KEY")
            self.client = OpenAI(api_key=api_key)

    def ask_llm(self, question, prediction, reference):
        prompt = (
            f"Question: {question}\n"
            f"Predicted Answer: {prediction}\n"
            f"Reference Answer: {reference}\n\n"
            "Evaluate how well the predicted answer answers the question compared to the reference.\n"
            "Give a score between 1 (poor) and 5 (excellent) and explain briefly.\n"
            "Respond only with: Score: X\nExplanation: ..."
        )

        model_name = self.model_name

        # todo: parameterize by the 1. model, ollama  2. have a boolean for RUN LLM as Judge, by default TRUE and default to ollama 
        try:
            print("Calling LLM:", self.model_name)
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
            )
            reply = response.choices[0].message.content
            #reply = response.choices[0].message.content  # OpenAI style
            score_match = re.search(r"Score:\s*(\d+)", reply)
            score = int(score_match.group(1)) if score_match else None
            return score, reply

        except Exception as e:
            print("LLM Error:", type(e).__name__, "-", str(e))
            return None, "Error calling LLM"

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
            # todo: tweak it to accept any language , can we use code-bert-score on natural language 
            # Compute CodeBERT scores 
            pred_results =code_bert_score.score(cands=predictions, refs=references,lang="text")

             # Append CodeBERT score to each result
        for i, r in enumerate(results):
            r["codebert"] = pred_results[0][i]  # Extracting codebert score for each result
        
        if self.use_llm_judge:
            for r in results:
                score, explanation = self.ask_llm(r["question"], r["prediction"], r["reference"])
                r["llm_score"] = score
                r["llm_explanation"] = explanation

        return results


