from flask import Flask
from flask import request, jsonify
from openai import OpenAI
import base64
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

client = OpenAI(api_key=OPENAI_API_KEY)

user_prompt = """You are a dermatologist and an expert in analyzing images related to skin diseases working 
                   for a very reputed hospital. You will be provided with images with skin diseases and you 
                   need to identify the any skin disease or health issues. You need to generate the result in 
                   a detailed manner. Write all the findings, next steps, recommendation, etc. You only need 
                   to respond if the image is related to a human body and health issues. You must have to 
                   answer but also write a disclaimer saying that "Consult with a Doctor before making any 
                   decisions. Remember, if certain aspects are not clear from the image, it's okay to state 
                   'Unable to determine based on the provided image. If the given image does not have any 
                   disease, then give the response 'Unable to determine based on the provided image'."""


def analyze_image(image_data, question):
    messages = [{"role": "user", "content": [{"type": "text", "text": user_prompt}]}]

    messages[0]["content"].append(
        {
            "type": "image_url", 
            "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
            })
    
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",

         messages=messages,

          max_tokens=4096)

    return response.choices[0].message.content


@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        image_file = request.files['image']

        if image_file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        image_data = base64.b64encode(image_file.read()).decode('utf-8')

        question = user_prompt

        response = analyze_image(image_data, question)

        return jsonify({'response': response})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run()
