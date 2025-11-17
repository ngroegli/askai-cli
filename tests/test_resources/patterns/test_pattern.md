# Test Pattern

## Purpose
A simple test pattern for unit testing purposes.

## Inputs
- question: The question to answer
- detail_level: Level of detail (basic, detailed, comprehensive)

## Pattern Content

You are a helpful AI assistant for testing purposes.

When given a question: {{ question }}

Please provide a {{ detail_level }} answer that includes:
- A direct response to the question
- Any relevant context
- A brief summary

Format your response clearly and concisely.

## Outputs
- response: The formatted answer
- confidence: High/Medium/Low confidence level

## Example

Input:
```
question: "What is Python?"
detail_level: "basic"
```

Output:
```
Python is a high-level programming language known for its readability and versatility.

Context: Python was created by Guido van Rossum and is widely used in web development, data science, and automation.

Summary: Python is a popular, easy-to-learn programming language.

Confidence: High
```
