import requests
import pandas as pd
import json
import os
import math 
import re
import sys
import subprocess
import boto3
import pandas as pd
import sys
from botocore.config import Config


def extract_mathjax_from_image(prompt, image_url):
    """
    Call the OpenAI API to extract MathJax content from an image URL.
    """
    print("calling gpt using image----------------------")
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer sk-proj-Omi1OLajklrIffGp66SwT3BlbkFJuybtDxT4Y6CBMEzc0frk"  # Replace with your actual API key
    }
    payload = {
        "model": "gpt-4-turbo",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                        # "text": "If this is a math equation then give me the equation in mathjax format using dollar as mathjax delimiter and use double backslash to create a new line in mathjax. Only give output of the mathjax content and nothing else."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url,
                        },
                    }
                ]
            }
        ],
        "max_tokens": 2000
    }
    
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    
    if response.status_code == 200:
        response_data = response.json()
        # Extracting the MathJax formatted response
        mathjax_content = response_data['choices'][0]['message']['content']
        print(mathjax_content)
        return mathjax_content
    else:
        return "Error: " + response.text

def callChaptGPT2(input):
    MAX_TOKENS = 3000
    TEMPERATURE = 0.3
    model = "gpt-4-turbo"
    # model = "gpt-3.5-turbo"
    # apiKey = "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" //gpt-4 hanging
    # apiKey = "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" // gpt4 expired
    # apiKey = "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"//3.5
    apiKey = "sk-proj-Omi1OLajklrIffGp66SwT3BlbkFJuybtDxT4Y6CBMEzc0frk"
    url = "https://api.openai.com/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": input},
        ],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {apiKey}",
    }
    retry = True
    retry_attempt = 1
    while retry_attempt < 5:
        try:
            retry_attempt = retry_attempt + 1

            response = requests.post(url, json=payload, headers=headers)
            # Check if the response was successful
            response.raise_for_status()

            data = response.json()
            output = data["choices"][0]["message"]["content"].strip().strip("\"").strip("\'")
            print(output)
            return output
        except requests.exceptions.HTTPError as http_err:
            # This block catches HTTP errors
            print("HTTP Error:", http_err)
            print("Status Code:", response.status_code)
            try:
                print("Response Body:", response.json())  # Attempt to print JSON response body
            except ValueError:  # Includes simplejson.decoder.JSONDecodeError
                print("Response Text:", response.text)  # Fallback to raw text if JSON decoding fails
            # logging.exception("An HTTPError occurred in get_gpt4_response, ExtractData")
        except Exception as error:
            # logging.exception("An error occurred in get_gpt4_response, ExtractData")
            print(error)


def create_steps(Question):
    # text = Question
    # temp = "ImageGen"
    prompt = f"""A math question is delimited by *. The Question is:  {Question}
        Give steps to create an animation for this math question. The animation represents only the question, not its solution.
        Use the following approach. First, identify the individual objects from the question. Objects are specific figures, shapes, lines, or points. Each object should have only one shape, figure, line, or point. Create separate objects for separate figures, even if figures are same or identical.
        For each object that is identified, create a separate step. In the step describe the object and give it any relevant labels. For example, the labels for a triangle might be A, B, and C for its vertices. Add labels wherever possible. For circles, label the centers. For polygons, label the vertices. For line segments, label the end points. Similarly, add labels wherever you think it could be useful in order to understand the image. Do not include relationships between different objects in these steps.
        Next, identify any steps that have more than one object. If identified, split this step into two or more separate steps so that each step has only one object. This is done even if the objects are identical or similar.
        When creating objects, be specific about the dimensions. If given in the question, use them. If not given in the question, assume dimensions intelligently. For instance, if the question involves a circle, choose a radius length that would be at par with any other information in the question.
        Next, add steps that give information about the spatial relationship between the objects. Specify criteria to meet the relationship between objects based on information given in the question. For example, rotation or translation of objects, changing lengths of objects, etc. this should be taken or inferred from the question. Identify and perform actions on one object at a time, not together, unless otherwise required by the question. For example, if multiple conditions exist in the question, perform one action on one object, and then the next action in a separate step. If specific distances are needed, convert them into standard units. For example, if it specifies a square with side 9 cm and a circle with radius 1 meter, then you convert these into a square of side 9 units and a circle of radius 100 units.
        Next, make each step specific and granular. The steps should be like an algorithm that can help the AI create the image. These steps will be used by an AI agent to create the image. Infer information from the question to make the steps precise. For example, if a question includes a 5 sided regular polygon, then you can infer that the internal angle is 108 degrees and include this in your steps to make it more precise. If you have any inferences that you are confident about, include a step for them to help create an accurate figure or to check that the figure meets the conditions inferred.. Only include inferences that you are very sure and confident about.
        Next, check each step to make sure that it represents only the information presented in the question. The steps should not include information that is part of the solution process. The steps should only reflect the question. Remove steps that are part of the solution. This includes creating additional lines, boundaries, or labels for anything that is not part of the question.
        Next, Delete any step that is adding the question text to the image, as in a text box. The image does not need the question text.
        Next, edit the previous steps so that any labels being used match the labels (if used) in the solution to this problem. Ignore any  additional information given in the solution. Only look at labels being used, and if the generated steps have anything similar, edit the labels in our steps to match the labels used in the solution. Don’t add any new steps or any new information from the solution to our steps. The solution is used only for mapping labels. The solution is:
        Do not add scales to the image.
        When specific lengths or angles are mentioned in the question, they should also be explicitly mentioned in the image or animation. If lengths / angles are not mentioned in the question, do not add lengths or angles in the image. To display distances between two points, we used a dashed line, and added text beneath the dashed line to indicate the distance. the length does not need to be true, so do not alter the image based on the length. Just add the text as per information given in the question. The color of the dashed line and the text for displaying the distance should be the same.
        Return only your final steps, nothing else."""
    response = callChaptGPT2(prompt)
    return response

def create_manim_code(Question, steps):
    input_file_path = "ManimDocShortened.txt"
    # Read the contents of the text file
    with open(input_file_path, encoding='utf8') as input_file:
        extracted_text = input_file.read()

    prompt = f"""Generate Manim code to create an image for the math question. While writing the code, make a class named \
        manim_image. The question is: {Question}
        Use the following instructions to help you generate the code. 
        The instructions are a step-by-step method to create the required image. 
        Steps: {steps}
        When positioning objects (shapes, lines, figures) relative to each other, write a method that moves that object until a criteria has been met. 
        Create checks to know when these criteria are met.
        Instructions to create an image for the given math question are:
        Return only the Manim code, nothing else. Keep the following in mind:
        1. For all labels, set font_size to 20.
        4. Use buff=0.1 for all labels
        5. When adding text, keep the text color to be YELLOW.
        6. Note that to figure out intersections of curves, you need to write a function. There are no inbuilt functions in Manim to get the intersection points
        7. Use Create instead of 'ShowCreation'.
        8. Make sure that all attributes and functions you used adhere to the manim documentation. If they do not adhere, correct the manim code. The documentation is: {extracted_text}
        9. Include from math import sqrt
        10. If some objects are too big and do not fit in the screen dimension, you should try and scaled down all objects. This can be done by using something like 'self.play(all_objects.animate.scale(0.5), run_time=2)' where you specify the scale as per the need of the image / animation.
        """
    response = callChaptGPT2(prompt)
    return response


def get_feedback_on_image(Question, steps, Code, image_url):
    prompt = f"""Here is a question and steps to generate an image for this question\
        Question: {Question} \n\
        Steps: {steps} \n\
        Now the manim code for this has been given as following: {Code}\n\
        this code creates the image as shown in the figure. \
        Check if the image generated correctly captures the Question if not give text feedback on what is wrong in the image, if the image correctly captures the question then return the word good-image. \
        If there is even a slightest mistake in the position of the figures or the image does not accurately represent the question or if the complete image is not visible and needs to be moved then give feedback on what needs to be changed to accurately represent the question.\
        """
    response = extract_mathjax_from_image(prompt, image_url)
    return response

def improve_code(question, feedback, code):
    prompt = f"""
    There is an issue with the following manim code given: {code}\n\
    The given code has to modified because there are some issues with the image that this code generates namely \
    Feedback: {feedback} \n \
    Inculcate this feedback and update the code given so that it accurately represents this scenario: {question} \
    In your final output give the updated manim code after making changes in the code as per the feedback, do not give any other text in your final output.
    """
    response = callChaptGPT2(prompt)
    return response

def run_command(command:str)->bool:
    # Run the command and capture the output
    result = subprocess.run(command, shell=True, capture_output=True, text=True)                                                                            
    # Print the output
    # for i in range(len(result.stdout)-2):
    #     if result.stdout[i:i+3] == 'YES': #'YES' means that the manim code does not use 3D coordinates.
    #         return True
    # return False
    print("Result----------",result)
    return result

def upload_file_to_s3(file_path, bucket_name, object_name, aws_access_key_id, aws_secret_access_key):
    my_config = Config(
        region_name = 'ap-northeast-1',
        signature_version = 'v4',
        retries = {
            'max_attempts': 5,
            'mode': 'standard'
        }
    )
    
    s3 = boto3.client('s3', config=my_config, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    # Upload file to S3 with public-read ACL
    try:
        s3.upload_file(file_path, bucket_name, object_name, ExtraArgs={'ACL': 'public-read'})
    except Exception as error:
        print(error)
        return None
    # Generate public URL
    object_url = f"https://{bucket_name}.s3.amazonaws.com/{object_name}"
    return object_url

def save_code_to_file(code, filename='manim_code.py'):
    """
    Saves the generated Manim code to a file.
    """
    if code is None:
        print("No code provided.")
        return None
    
    start_index = code.find("```python")  # Find the start of the code block
    if start_index != -1:
        end_index = code.find("```", start_index + len("```python"))  # Find the end of the code block
        if end_index != -1:
            code_block = code[start_index + len("```python"):end_index]  # Extract the code block
            code_block = code_block.strip()  # Remove leading and trailing whitespace
            with open(filename, 'w') as file:
                file.write(code_block)  # Write the code block to the file
            print("Code has been saved to", filename)
            return filename
    print("No code block found in input.")
    return None


def execute_manim(filename):
    """
    Executes the Manim script to generate an animation.
    Command assumes Manim is installed and `manim` command is available.
    """
    # Example command to run a Manim script and generate an mp4 file in the output directory
    command = f"manim -s -ql {filename}"
    result = run_command(command)
    if result.returncode == 0:
        print("Manim script executed successfully")
        return True,None
    else:
        print("Error in executing Manim script:", result.stderr)
        return False,result

def gen_image_n_upload(code):
    # Save the generated code to a file
    filename = save_code_to_file(code)

    # Execute the Manim script
    for i in range(0,2):
        state, result = execute_manim(filename)
        if state:
            # Get the current working directory
            curr_dir = os.getcwd()

            # Path to the directory where the files are expected to be
            manim_dir = os.path.join(curr_dir, 'media/images/manim_code')

            # List all files in the current directory
            files = os.listdir(manim_dir)


            # Filter files to find those that contain 'manim_image' and end with '.png'
            manim_files = [file for file in files if 'manim_image' in file and file.endswith('.png')]

            # Check if any matching files were found and assign the first one to 'output_file'
            if manim_files:
                output_file = os.path.normpath(os.path.join(manim_dir, manim_files[0]))
                print(f"Found file: {output_file}")
            else:
                print("No matching files found.")
            # curr_dir = os.getcwd()
            # # Path to the output file generated by Manim, adjust the path and filename as necessary
            # output_file = os.path.normpath(os.path.join(curr_dir,'media/images/manim_code/manim_image_ManimCE_v0.18.0.post0.png'))  # Ensure this path matches the output from Manim

            # Parameters for S3 upload
            bucket_name = 'manimnioclass'
            object_name = os.path.basename(output_file)
            aws_access_key_id = 'AKIA3S4H4Y22RBEQHAUV'
            aws_secret_access_key = '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'

            # Upload the file to S3
            url = upload_file_to_s3(output_file, bucket_name, object_name, aws_access_key_id, aws_secret_access_key)
            if url:
                print("File uploaded successfully. URL:", url)
                return url
            else:
                print("Failed to upload file.")
        else:
            final_code = improve_code(question,result,code)
            filename = save_code_to_file(final_code)
            print("Manim execution failed")
    return None

def main(question):
    steps = create_steps(question)
    code = create_manim_code(question, steps)
    print(code)
    
    url = gen_image_n_upload(code)

    feedback = get_feedback_on_image(question,steps,code,url)
    
    if 'good-image' not in feedback.lower():
        final_code = improve_code(question,feedback,code)
        url = gen_image_n_upload(final_code)
    return url

# Example usage
question = "2 Circles with radius 2 and 4 are touching each other externally"
# question = "number of times the 2 graphs given by y=x^2 and y=sinx intersect between [0,4]"
main(question)
