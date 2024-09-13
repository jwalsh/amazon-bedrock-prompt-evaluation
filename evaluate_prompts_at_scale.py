import json
from datetime import datetime
from test_evaluation_flow import evaluatePrompt

# Read prompts dataset file
promptsDataset = []
with open('prompts_dataset.jsonl') as f:
    for line in f:
        promptsDataset.append(json.loads(line))

# Configuration
flowEvalId = "your_flow_eval_id"
flowEvalAliasId = "your_flow_eval_alias_id"
modelInvokeId = "your_model_invoke_id"
modelEvalId = "your_model_eval_id"

if promptsDataset:
    results = []
    for i, j in enumerate(promptsDataset):
        print(f"{datetime.now().strftime('%H:%M:%S')} - Evaluating prompt {i+1} of {len(promptsDataset)}...")
        try:
            results.append(evaluatePrompt(j["input"], flowEvalId, flowEvalAliasId, modelInvokeId, modelEvalId))
        except Exception as e:
            print(f"Error evaluating prompt {i+1}: {e}")
            results.append({"error": str(e)})
    print("All prompts evaluated.")

# Review results
for i in results:
    print(json.dumps(i, indent=2, ensure_ascii=False))

# Visualize results (requires matplotlib)
import matplotlib.pyplot as plt
import numpy as np

scores = [result.get('prompt-score', 0) for result in results if 'prompt-score' in result]
labels = [f"Prompt {i+1}" for i in range(len(scores))]

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(labels, scores)
ax.set_title("Evaluation Scores", fontsize=14)
ax.set_xlabel("Prompts", fontsize=12)
ax.set_ylabel("Score", fontsize=12)
plt.xticks(rotation=45, fontsize=10)
ax.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
ax.axhline(y=80, color='r', linestyle='--', label='Passing threshold')
ax.legend(loc='upper right')
plt.savefig('evaluation_scores.png')
plt.close()

print("Evaluation scores chart saved as 'evaluation_scores.png'")
