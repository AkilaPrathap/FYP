from transformers import BertForQuestionAnswering, BertTokenizer
from bert_score import score

# Define a list of model names
model_names = ["bert-base-uncased",
               "bert-large-uncased",
               "bert-base-cased",
               "bert-large-cased",
               "bert-base-multilingual-uncased",
               "bert-base-multilingual-cased",
               "bert-large-uncased-whole-word-masking-finetuned-squad"]

# Example question and context
question = "What is the capital of France?"
context = "France is a country located in Europe. Its capital is Paris."

# Initialize dictionaries to store BERTScore results
precision_scores = {}
recall_scores = {}
f1_scores = {}

# Loop through each model name
for model_name in model_names:
    # Load pre-trained model and tokenizer
    model = BertForQuestionAnswering.from_pretrained(model_name)
    tokenizer = BertTokenizer.from_pretrained(model_name)

    # Tokenize inputs
    inputs = tokenizer(question, context, return_tensors="pt")

    # Perform question answering
    outputs = model(**inputs)
    start_scores = outputs.start_logits
    end_scores = outputs.end_logits

    # Get the answer span
    start_index = start_scores.argmax(dim=1).item()
    end_index = end_scores.argmax(dim=1).item() + 1
    answer = tokenizer.convert_tokens_to_string(
        tokenizer.convert_ids_to_tokens(inputs["input_ids"][0][start_index:end_index]))

    # Calculate BERTScore
    refs = [context]
    hyps = [answer]
    precision, recall, f1 = score(hyps, refs, lang="en", verbose=False)

    # Store BERTScore results
    precision_scores[model_name] = precision.mean()
    recall_scores[model_name] = recall.mean()
    f1_scores[model_name] = f1.mean()

# Print BERTScore results for each model
for model_name in model_names:
    print(f"Model: {model_name}")
    print(f"BERTScore Precision: {precision_scores[model_name]:.4f}")
    print(f"BERTScore Recall: {recall_scores[model_name]:.4f}")
    print(f"BERTScore F1 score: {f1_scores[model_name]:.4f}")
    print()


