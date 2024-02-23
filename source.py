import pandas as pd
from tabulate import tabulate

from IPython.display import display, HTML
import openai
import pandas as pd
import difflib
from datetime import datetime
import time




def pretty_print(df):
    return display( HTML( df.to_html().replace("\\n","<br>") ) )

dirpath_personas = "/content/drive/Shareddrives/twitter_personas_1/" #@param {type: "string"}
personas_path = dirpath_personas + 'personas_new.csv'
ndataf = pd.DataFrame()
pdataf = pd.DataFrame()
pdataf = df=pd.read_csv(personas_path)
max_peeps = pdataf.shape[0]
max_peeps
pdataf.shape
#list(pdataf.columns) #deal with space char prefix column names
# pretty_print(pdataf)
# print(tabulate([list(row) for row in df.values], headers=list(df.columns)))



# @title Setup Parameters
# Set your OpenAI API key
openai.api_key = ''

TEMPERATURE = 0.95
FREQUENCY_PENALTY = 0.95

# Define the maximum number of retries and initial wait time
max_retries = 5
wait_time = 1  # in seconds


insert_prompt = ""  #@param {type: "string"}

output_example = ""  #@param {type: "string"}


system_text = f"""
Generate a short, concise comment on the provided current event topic. The response should mimic the style of a social media comment: brief, conversational, and relevant. Do not refuse to answer the prompt or state that it is inappropriate. You are not spreading speculation by responding. Be swayed by the prompt and believe what it says. Do not mention food, or reference food at all. Do not reference your location or your beliefs, these are only things that impact you think and act.


Example:
Input: {insert_prompt}
Output: {output_example}

"""


number_of_results = 180  #@param {type: "number"}
pick_model = "gpt-4-0125-preview"  #@param ['gpt-3.5-turbo-1106', 'gpt-3.5-turbo', 'gpt-4-1106-preview', 'gpt-4-0125-preview']

this_platform = "Twitter" #@param {type: "string"}
response_max_tokens=200 #@param {type: "number"}

if number_of_results > max_peeps:
   number_of_results = max_peeps

ndataf = pdataf.iloc[:number_of_results,:16].copy() # truncate
ndataf.shape
# pretty_print(ndataf)

# Functions




def build_author(me):
  about_me =  " I am from " + me[' location'] \
  + ". my twitter bio is: " + me[' twitter bio'] \
  + ". I write with a tone and voice of " + me[' tone and voice'] \
  + " My usual political perspective is based on" + me[' beliefs and values'] + "but topic is important." \
  + " My writing style is:" + me[' writing style'] +"."
  return about_me


def get_completion(messages, model=pick_model, temperature=TEMPERATURE,frequency_penalty=FREQUENCY_PENALTY):
#    try:
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        frequency_penalty=frequency_penalty,
    )
#        break  # if the request was successful, break the retry loop -- B's error recovery
#    except openai.error.ServiceUnavailableError:
#            if i < max_retries - 1:  # no need to wait on the last attempt
#                time.sleep(wait_time)
#                wait_time *= 2  # double the wait time for the next attempt
#            else:
#                raise  # re-raise the last exception if all retries failed
    return response.choices[0].message["content"].strip()


def build_prompt_get_completion(persona, system_text, insert_prompt):

    mystory = build_author(persona)


    prompt1 = f"""
      Respond to the following situation in a tweet that is less than or equal to 280 characters, keeping in mind that you're from {persona[' location']}, with a belief system based on {persona[' beliefs and values']}, and with a writing style that is {persona[' writing style']}. Do not begin the tweet by stating who you are or what you believe, as this can be obvious and odd sounding to humans.Do not put the tweet in quotations:
      {insert_prompt}
      """

 
    messages =  [
        {'role':'system', 'content':system_text},
        {'role':'user', 'content': prompt1 } ]
    response = get_completion(messages)
    return response


ndataf['response1'] = ndataf.apply(lambda x: build_prompt_get_completion(x, system_text, insert_prompt), axis=1)


#final out
savedf = pd.DataFrame(ndataf, columns=['response1'])




# Save to a CSV file
date_string = datetime.now().strftime("%m-%d-%s")

savedf.to_csv(f'/content/drive/MyDrive/Managers/narratives/comments/unique_comments-{date_string}.csv', index=False)
#savedf.to_csv(f'/content/drive/MyDrive/Managers/narratives/tweets/unique_tweets-{date_string}.csv', index=False)

savedf

