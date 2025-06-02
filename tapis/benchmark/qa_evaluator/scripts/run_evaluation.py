import json
import pandas as pd
import sys
import os 
sys.path.append(os.path.curdir)
print(f"python path: {sys.path}")

from src.qa_evaluator.evaluator import QAEvaluator

def main():
    # Load JSON file
    with open("config.json", "r", encoding="utf-8") as cfg:
        config = json.load(cfg)

    # Extract config values
    use_ollama = config.get("use_ollama", True)
    use_llm_judge = config.get("use_llm_judge", True)
    model_name = config["model_name_ollama"] if use_ollama else config["model_name_openai"]
    qa_sets_path = config['qa_sets_path']

    with open(qa_sets_path, "r", encoding="utf-8") as f:
        qa_pairs = json.load(f)

    # Instantiate and run evaluator
    evaluator = QAEvaluator(model_name=model_name, 
                            use_llm_judge=use_llm_judge, 
                            use_ollama=use_ollama)    
    results = evaluator.evaluate(qa_pairs)

    # Save results
    output_path = "outputs/qa_evaluation_results_jfs.csv"
    pd.DataFrame(results).to_csv(output_path, index=False)
    print(f"\nEvaluation completed. Results saved to '{output_path}'.")

    # Optional: Print sample
    for r in results[:3]:  # print only 3 for brevity
        print("\nQ:", r["question"])
        print("Prediction:", r["prediction"])
        print("Reference:", r["reference"])
        print("BLEU:", round(r["bleu"], 4), "| ROUGE-L:", round(r["rouge-l"], 4), "| CodeBERT:", r["codebert"])
        # Uncomment this line for getting LLM score
        #print("BLEU:", round(r["bleu"], 4), "| ROUGE-L:", round(r["rouge-l"], 4), "| CodeBERT:", r["codebert"],"| LLM_as_judge:", r["llm_score"])

  


if __name__ == "__main__":
    main()