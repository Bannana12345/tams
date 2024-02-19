

from flask import Flask, request, Response
import requests
import time
import random
import string

app = Flask(__name__)

# Hardcoded model ID
MODEL_ID = "666150205269367046"

@app.route('/generate-image')
def generate_image():
    try:
        # Extract parameters from the query string
        prompt = request.args.get('prompt')

        # Define the API endpoint
        api_endpoint = "https://ap-east-1.tensorart.cloud/v1/jobs"

        # Define the request payload
        payload = {
            "request_id": "".join(random.choices(string.ascii_lowercase + string.digits, k=10)),
            "stages": [
                {
                    "type": "INPUT_INITIALIZE",
                    "inputInitialize": {
                        "seed": -1,
                        "count": 1
                    }
                },
                {
                    "type": "DIFFUSION",
                    "diffusion": {
                        "width": 1024,
                        "height": 1024,
                        "prompts": [
                            {
                                "text": prompt
                            }
                        ],
                        "steps": 35,
                        "sd_model": MODEL_ID,
                        "clip_skip": 0,
                        "cfg_scale": 7
                    }
                }
            ],
            "engine": "TAMS_V1"
        }

        # Headers
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer c079efc01ace4884adea506bce50eb1d'  # Replace with your actual API key
        }

        # Send POST request to create a job
        response = requests.post(api_endpoint, json=payload, headers=headers)

        # Extract the job ID from the response
        job_id = response.json()['job']['id']

        # URL for accessing the job details
        job_details_url = f'{api_endpoint}/{job_id}'

        while True:
            # Send GET request to access job details
            job_details_response = requests.get(job_details_url, headers=headers)

            # Check if the job status is SUCCESS
            if job_details_response.json()['job']['status'] == 'SUCCESS':
                break

            # Wait for a few seconds before checking again
            time.sleep(5)

        # Extract the image URL from the job details response
        image_url = job_details_response.json()['job']['successInfo']['images'][0]['url']

        # Send GET request to download the image
        image_response = requests.get(image_url)

        # Check if the request was successful
        if image_response.status_code == 200:
            # Return the image data as response
            return Response(image_response.content, mimetype='image/jpeg')
        else:
            return "Failed to download the image.", 500
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

if __name__ == "__main__":
    app.run()
