import json
import pandas as pd
from src.qa_evaluator.evaluator import QAEvaluator

def main():
    # Load JSON file
    with open("data/LLM_generated_v1.json", "r", encoding="utf-8") as f:
        qa_pairs = json.load(f)

    # Instantiate and run evaluator
    evaluator = QAEvaluator()
    results = evaluator.evaluate(qa_pairs)

    # Save results
    output_path = "outputs/qa_evaluation_results.csv"
    pd.DataFrame(results).to_csv(output_path, index=False)
    print(f"\nEvaluation completed. Results saved to '{output_path}'.")

    # Optional: Print sample
    for r in results[:3]:  # print only 3 for brevity
        print("\nQ:", r["question"])
        print("Prediction:", r["prediction"])
        print("Reference:", r["reference"])
        print("BLEU:", round(r["bleu"], 4), "| ROUGE-L:", round(r["rouge-l"], 4), "| CodeBERT:", r["codebert"])

if __name__ == "__main__":
    main()