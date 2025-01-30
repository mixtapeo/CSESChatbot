# Uses texts & bios from ResumesDownloader.py, interface with OpenAI GPT 4.0-Turbo, prints result & saves into GPTout.json.
# Removed docx and PDF features. Not needed.

from openai import OpenAI
import json
from docx import Document
import fitz  # PyMuPDF
import os
import numpy as np
from dotenv import load_dotenv
import os
import datetime
import time
import random

"""
How the program works:
    1. Loaded text is divided into chunks. (to not go over rate limit. upgrade openapi limit to level 2 for more)
    2. Message is sent as argument to chatgpt.
    3. conversation history is appended to conversation_history (to keep context / memory of previous conversation throughout chat)
    4. step 2. and 3. repeated until end.

Also has utility function of create_batch_summary to summarize all texts in one go.
"""


class GPT:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def extract_text_from_pdf(self, file_path):
        """
        Extract info from PDF files.
        """
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        except:
            # Handle errors (e.g., .docx detected)
            return self.extract_text_from_docx(file_path)

    def load_files(self, directory):
        """
        Made to parse texts for data. Try to extract file as a pdf.
        """
        content = []
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if filename.endswith(".pdf"):
                text = self.extract_text_from_pdf(file_path)
                content.append({"filename": filename, "text": text})
            elif filename.endswith(".txt"):
                text = ""
                content.append({"filename": filename, "text": text})
        return content

    def gpt_request(self, data, message, *conversation_history):
        """
        Send requests to GPT-4 with the provided chunks of text and conversation history.
        Args:
            message (str): The main user message or prompt.
            conversation_history (list): Previous conversation messages for context.
        """
        print("Loading...")
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a chatbot for CSES: Carleton Student Engineering Society provided with conversations history and help info. Help the user as needed.",
                },
                {"role": "system", "content": f"texts: {data}"},
                {
                    "role": "system",
                    "content": f"Conversation History: {conversation_history}",
                },
                {"role": "user", "content": message},
            ],
            stream=True,
        )
        reply = ""
        for chunk in completion:  # Streaming response
            if chunk.choices[0].delta.content is not None:
                reply += chunk.choices[0].delta.content
                print(chunk.choices[0].delta.content, end="")

        context = [reply, message]
        return context

    def summarize(self, batch_input_file):
        """
        Summarize given content.
        """
        print("Summarising")

        try:
            batch_input_file_id = batch_input_file.id

            # This request will return a Batch object with metadata about your batch:
            batch = GPT.client.batches.create(
                input_file_id=batch_input_file_id,
                endpoint="/v1/chat/completions",
                completion_window="24h",
                metadata={"description": "nightly eval job"},
            )

            # Get batch id from batch report above
            batch_id = batch[0]["id"]

            # Wait for batch to complete.
            while loop:
                batch = GPT.client.batches.retrieve(batch_id)
                if batch[0]["status"] == "completed":
                    loop = False
                if batch[0]["status"] == "failed":
                    raise Exception("Batch failed")
                # Wait 60 seconds before checking again
                datetime.time.sleep(60)

            file_response = GPT.client.files.content("file-xyz123")

        except Exception as e:
            print(e)

            # Save to file for debug
        with open("bot_knowledge_cache.txt", "w") as file:
            json.dump({f"GPTout": file_response.text}, file, indent=4)
            # json.dump({"content": content}, file, indent=4) # Debug: Compare input from files to output by GPT
        return file_response.text

    def create_batch_summary(self):
        def create_batch_file(content, request_id):
            """
            Create a batch file for the given content.
            """
            preamble = {
                "custom_id": request_id,
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {
                            "role": "system",
                            "content": "Summarize the following texts. Remove irrelevant information like formatting.",
                        },
                        {"role": "system", "content": content},
                    ],
                },
            }
            return preamble

        # # Adding as requried: request for each 'content'
        directory = os.path.join(os.getcwd(), "files")  # ./files
        texts = self.load_files(directory)
        open("batchrequest.jsonl", "w").close()  # Clear file

        print("Writing to file")
        for texts_text in texts:
            text = (texts_text["text"]).replace("\n", "")
            with open("batchrequest.jsonl", "a") as batchfile:
                # line = json.loads(total_text)
                # Random ID for request
                request_id = f"request-{random.randint(0, 200000)}"
                batchfile.write(json.dumps(create_batch_file(text, request_id)) + "\n")

        # Upload batch request to OpenAI
        batch_file = self.client.files.create(
            file=open("batchrequest.jsonl", "rb"), purpose="batch"
        )

        # Creating the batch job
        GPT_inst = GPT(os.getenv("OPENAI_API_KEY"))
        batch_job = GPT_inst.client.batches.create(
            input_file_id=batch_file.id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
        )

        # Wait for batch to complete.
        loop = True
        while loop:
            batch_job = self.client.batches.retrieve(batch_job.id)
            if batch_job.status == "completed":
                loop = False
            if batch_job.status == "failed":
                raise Exception("Batch failed")
            else:
                print(
                    f"Waiting for batch to complete. Current status: {batch_job.status}"
                )
                time.sleep(15)  # Wait 15 seconds before checking again

        # Retrieving and storing resulted content: Input file has raw output from OpenAI, outputfile has cleaned up content.
        result_file_id = batch_job.output_file_id
        result = GPT_inst.client.files.content(result_file_id).content
        temp_store = "textCacheTemp.txt"
        result_file_name = "bot_knowledge_cache.txt"

        open(temp_store, "wb").close()  # Clear file
        with open(temp_store, "wb") as file:
            file.write(result)

        # Prepare the output file
        open(result_file_name, "wb").close()  # Clear file

        with open(temp_store, "r") as input_file, open(
            result_file_name, "w"
        ) as output_file:
            for line in input_file:
                # Parse each line as JSON
                json_object = json.loads(line.strip())

                # Extract the desired content
                content = (
                    json_object.get("response", {})
                    .get("body", {})
                    .get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                )

                # Write the extracted content as a new JSON line
                if content:  # Ensure content exists
                    json_line = json.dumps({"content": content})
                    output_file.write(json_line + "\n")

        os.remove(temp_store)  # Remove temp file

        # Loading data from saved file
        results = []
        with open(result_file_name, "r") as file:
            for line in file:
                # Parsing the JSON string into a dict and appending to the list of results
                json_object = json.loads(line.strip())
                results.append(json_object)

        return results

    def refresh_summary(self):
        #? Can fix / implement. Can be used in the future for summarising site content
        # Path to local directory containing texts
        directory = os.path.join(os.getcwd(), "files")  # ./files
        texts = self.load_files(directory)
        text_text = [text["text"] for text in texts]

        GPT_inst = GPT(os.getenv("openai_api_key"))

        with open("bot_knowledge.txt", "w") as file:
            json.dump({"text": text_text}, file, indent=4)

        batch_input_file = GPT_inst.client.files.create(
            file=open((os.path.join(os.getcwd(), "bot_knowledge.txt")), "rb"),
            purpose="batch",
        )

        data = GPT_inst.summarize(batch_input_file)
        return data

    def start_request(self, message, data, conversation_history) -> list:
        """
        Process texts and handle conversation with GPT.
        1. Loads files as text into {texts}
        2. Summarize all text content to optimize tokens sent. Stored in textCache.json.
        3. Send user message & summarized json to GPT for response.
        """
        # Get the response from GPT, add to conversation history.

        context = self.gpt_request(data, message, conversation_history)
        reply, message = context

        conversation_history.append({"role": "user", "content": message})
        conversation_history.append({"role": "assistant", "content": reply})

        # Save the response to a JSON file
        with open("GPTout.json", "a") as file:
            json.dump(
                {
                    f"GPTout {datetime.datetime.strptime(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), '%Y-%m-%d %H:%M')}": reply,
                    "Context": conversation_history
                },
                file,
                indent=4,
            )
            file.write("\n")
        return conversation_history

    def user_start(self):
        """
        User interface for starting the program.
        """
        # Load textCache.jsonl data
        with open("bot_knowledge_cache.txt") as f:
            data = f.readlines()

        # Loop forever
        stop = True
        conversation_history = []
        while stop:
            message = input("Enter prompt: ")
            # returns context
            conversation_history += self.start_request(
                message, data, conversation_history
            )


def dev_start():
    App = GPT(os.getenv("OPENAI_API_KEY"))

    # OpenAI API client + other initializations
    print("Waking up GPT...")
    load_dotenv()

    # Summarise texts / files
    # inp = input(
    #     "Refresh summary table? [Might make reuslts more accurate, but will take longer] y/n: "
    # )
    # if inp in ("y", "Y"):
    #     data = App.refresh_summary()
    #     print("Summary cache refreshed.")
    # else:
    if os.path.isfile("bot_knowledge.txt"):
        with open("bot_knowledge.txt", encoding='utf-8') as f:
            data = f.readlines()
            print("Loaded previous data.")
    else:
        data = []
        print("No previous data. Starting without knowledge.")

    # Loop forever
    stop = True
    conversation_history = []
    while stop:
        message = input("\nEnter prompt: ")
        # returns context
        conversation_history += App.start_request(message, data, conversation_history)


if __name__ == "__main__":
    dev_start()
