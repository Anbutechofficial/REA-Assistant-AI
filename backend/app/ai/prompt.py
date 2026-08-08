def build_prompt(question, retrieved_docs):
    """
    Create the prompt for the LLM.

    Parameters:
        question (str): User's question
        retrieved_docs (list): Top matching properties

    Returns:
        str: Prompt
    """

    context = ""

    for i, doc in enumerate(retrieved_docs, start=1):
        context += f"Property {i}:\n"
        context += doc["text"]
        context += "\n\n"

    prompt = f"""
You are a helpful Real Estate Assistant supporting English and Tanglish (Tamil written in English/Latin alphabet).

Answer the user's question using ONLY the property information provided below. Understand questions posed in either English or Tanglish accurately.

FORMATTING REQUIREMENTS:
When listing properties, format each property clearly line-by-line in this exact structure:

Property 1
Property Name: <name>
Price: <price_lakhs> lakhs
Sqft: <area_sqft>
BHK: <bhk>

Property 2
Property Name: <name>
Price: <price_lakhs> lakhs
Sqft: <area_sqft>
BHK: <bhk>

Example:
Property 1
Property Name: rwd corniche
Price: 440.0 lakhs
Sqft: 2600
BHK: 3

Property 2
Property Name: ceebros the atlantic
Price: 445.0 lakhs
Sqft: 1975
BHK: 3

Make sure each field (Property Name, Price, Sqft, BHK) is on a NEW line. Do NOT combine properties into a single line or separate them with asterisks. Include "lakhs" after the price value.

If the answer is not available in the provided properties, say:
"I couldn't find a suitable property based on the available data."

==========================
Available Properties
==========================

{context}

==========================
User Question
==========================

{question}

==========================
Answer
==========================
"""

    return prompt
