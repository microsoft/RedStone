#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
import time
import traceback
import tiktoken
import collections
from datetime import datetime
import openai
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider


class GPTAPI:
    def __init__(self, engine, endpoint, identity_id):
        """
        Detail setting method could refer to: https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/managed-identity
        The authentication methods include key-based method, cli-based method, identity-based method, etc.
        We use identity-based method, you could switch to other method.
        """
        self.keep_history = False
        self.user_QAs = collections.defaultdict(list)
        self.max_tokens_per_requests = 8192 - 800 - 192
        self.quato_tokens_per_minute = 120000#140000
        self.quato_requests_per_minute = 720#840
        self.last_minute = -1
        self.acc_tokens = 0
        self.acc_requests = 0

        try:
            self.enc = tiktoken.encoding_for_model("gpt-4")
        except:
            self.enc = None
        self.engine = engine
        self.endpoint = endpoint

        token_provider = get_bearer_token_provider(DefaultAzureCredential(managed_identity_client_id=identity_id), "https://cognitiveservices.azure.com/.default")
        self.client = AzureOpenAI(
            azure_endpoint=endpoint,
            azure_ad_token_provider=token_provider,
            #api_version="2024-02-15-preview",
            api_version="2024-08-01-preview",
            max_retries=0,
        )

    def switch_api(self, api_idx=-1):
        # TBD: not implemented yet. 
        pass

    def get_tokens(self, text):
        tokens = max(len(text.split()), len(text) // 4)
        return tokens

    def run(self, system, question, engine=None, uid=None, temperature=0.0, max_tokens=800):
        if engine is None:
            engine = self.engine
        
        if self.enc is None:
            return ""

        # question check.
        #if self.get_tokens(question) > self.max_tokens_per_requests:
        #    question = question[:self.max_tokens_per_requests * 4]
        tokens = self.enc.encode(question)
        tokens_len = len(tokens)
        if tokens_len > self.max_tokens_per_requests:
            offset = (tokens_len - self.max_tokens_per_requests) // 2
            cut_tokens = tokens[offset:offset+self.max_tokens_per_requests]
            question = self.enc.decode(cut_tokens)

        # system setting.
        messages = [{"role": "system", "content": system}]
        
        # chat setting.
        if self.keep_history:
            for Q, A in self.user_QAs[uid]:
                messages.append({"role": "user", "content": Q})
                messages.append({"role": "assistant", "content": A})
        messages.append({"role": "user", "content": question})

        # quato check.
        """
        while True:
            cur_minute = datetime.now().minute
            cur_tokens = self.get_tokens(str(messages))
            if self.last_minute != cur_minute:
                self.last_minute = cur_minute
                self.acc_tokens = 0
                self.acc_requests = 0
            if self.acc_requests + 1  < self.quato_requests_per_minute and self.acc_tokens + cur_tokens < self.quato_tokens_per_minute:
                self.acc_requests += 1
                self.acc_tokens += cur_tokens
                break
            time.sleep(1)
        """

        # robot running.
        try:
            response = self.client.chat.completions.create(
                model=engine,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                #top_p=0.95,
                #frequency_penalty=0,
                #presence_penalty=0,
                #stop=None
            )
            answer = response.choices[0].message.content
        # https://github.com/openai/openai-python/blob/main/openai/error.py
        except (openai.RateLimitError, openai.APITimeoutError, openai.APIConnectionError) as e:
            time.sleep(2)
            #seconds = int(str(e).split("Please retry after")[1].split("second")[0].strip())
            #time.sleep(seconds)
            #traceback.print_exc()
            self.switch_api()
            return self.run(system, question, engine, uid, temperature)
        except openai.BadRequestError as e:
            if e.code == "context_length_exceeded":
                try:
                    offset = len(question) // 8
                    return self.run(system, question[offset:-offset], engine, uid, temperature)
                except:
                    answer = ""
                    traceback.print_exc()
            if e.code == "content_filter":
                answer = ""
            else:
                answer = ""
                traceback.print_exc()
        except Exception as e:
            if response is not None and response.choices[0].finish_reason == "content_filter":
                answer = ""
            else:
                answer = ""
                traceback.print_exc()
        
        # update history chat.
        if self.keep_history:
            self.user_QAs[uid].append((question, answer))
            while len(self.user_QAs[uid]) > 10:
                self.user_QAs[uid].pop(0)
        
        return answer

if __name__ == "__main__":
    engine = "gpt-4"
    endpoint = "https://XXX.openai.azure.com/"# to be filled.
    identity_id = ""# to be filled.
    gpt_api = GPTAPI(engine, endpoint, identity_id)
    system = "You are my assistant"
    question = "give me a latex math formula"
    answer = gpt_api.run(system=system, question=question)
    print(answer)
