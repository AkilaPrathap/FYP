from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS from flask_cors
import csv
from transformers import BertTokenizer, TFBertForQuestionAnswering
import numpy as np
from difflib import SequenceMatcher

app = Flask(__name__)
CORS(app)  # Apply CORS to your Flask app

# Load pre-trained BERT model for question answering
model = TFBertForQuestionAnswering.from_pretrained('bert-base-cased')

# Load tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-cased')

# Function to calculate similarity between two strings
def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

# Function to read QA pairs from a CSV file
def read_qa_pairs_from_csv(csv_file):
    qa_pairs = {}
    with open(csv_file, mode='r', newline='') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if len(row) >= 2:  # Check if the row has at least two elements (question and answer)
                qa_pairs[row[0]] = row[1]
    return qa_pairs


# Function to perform question answering
def answer_question(question, context, qa_pairs):
    # Preprocess input question
    question = question.lower()

    # Check if the question matches any predefined question with some level of similarity
    max_similarity = 0
    best_match = None
    for q in qa_pairs.keys():
        sim = similarity(question, q.lower())
        if sim > max_similarity:
            max_similarity = sim
            best_match = q

    # If a match with sufficient similarity is found, return the corresponding answer
    if max_similarity >= 0.5:  # Adjust the threshold as needed
        return qa_pairs[best_match]
    else:
        # Tokenize inputs
        input_ids = tokenizer.encode(question, context)
        token_type_ids = [0 if i <= input_ids.index(102) else 1 for i in range(len(input_ids))]
        input_ids = np.array([input_ids])
        token_type_ids = np.array([token_type_ids])

        # Get model prediction
        start_scores, end_scores = model.predict([input_ids, token_type_ids])

        # Find the tokens with the highest start and end scores
        answer_start = np.argmax(start_scores)
        answer_end = np.argmax(end_scores)

        # Get the answer span without the [CLS] token
        answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(input_ids[0][answer_start+1:answer_end+1]))

        return answer

@app.route('/ask', methods=['POST'])
def ask():
    if request.method == 'POST':
        data = request.get_json()
        question = data.get('question')
        context = "Car diagnostics context here..."  # Provide relevant car diagnostics information here
        qa_csv_file = 'dataset.csv'
        qa_pairs = read_qa_pairs_from_csv(qa_csv_file)
        answer = answer_question(question, context, qa_pairs)
        return jsonify({'answer': answer})
    else:
        return jsonify({'error': 'Method not allowed'}), 405

if __name__ == '__main__':
    app.run(port=5000)
