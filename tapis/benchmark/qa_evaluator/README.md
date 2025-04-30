This is an evaluator module that computes the BLEU, Rouge and code-bert-scores for Tapis Q/A.
In order to run the script, cd into the comp-eng-benchmark/tapis/benchmark/qa_evaluator and run 
```
python scripts/run_evaluation.py

```
When the script runs successfully, you should see a qa_evaluation_results.csv in the outputs directory.
This csv file has output format for each question provided in the json file. 

question,prediction,reference,bleu,rouge-1,rouge-2,rouge-l,codebert

