import boto3
import json
import time
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
import ipywidgets as ipw
from IPython.display import display, clear_output

def auth_opensearch(host,  # serverless collection endpoint, without https://
                    region,
                    service = 'aoss'):
    credentials = boto3.Session().get_credentials()
    auth = AWSV4SignerAuth(credentials, region, service)

    # create an opensearch client and use the request-signer
    os_client = OpenSearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        pool_maxsize=20,
        timeout=3000
    )
    return os_client


class ChatUX:
    """ 
    A chat UX using IPWidgets
    """
    def __init__(self, qa, retrievalChain = False):
        self.qa = qa
        self.name = None
        self.b=None
        self.retrievalChain = retrievalChain
        self.out = ipw.Output()


    def start_chat(self):
        print("Starting chat assistant")
        display(self.out)
        self.chat(None)


    def chat(self, _):
        if self.name is None:
            prompt = ""
        else: 
            prompt = self.name.value
        if 'q' == prompt or 'quit' == prompt or 'Q' == prompt:
            print("Thank you , that was a nice chat!")
            return
        elif len(prompt) > 0:
            with self.out:
                thinking = ipw.Label(value="Thinking...")
                display(thinking)
                try:
                    if self.retrievalChain:
                        result = self.qa.invoke({'question': prompt})
                    else:
                        out = self.qa.invoke({'question': prompt, "chat_history":self.qa.memory.chat_memory.messages }) #, 'history':chat_history})
                        result = out['answer']
                        source = out['source_documents'][0].metadata['page-link']
                except Exception as e:
                    print(e)
                    result = "No answer"
                thinking.value=""
                display(f"AI: {result}")
                display(f"Here is my source: {source}")
                self.name.disabled = True
                self.b.disabled = True
                self.name = None

        if self.name is None:
            with self.out:
                self.name = ipw.Text(description="You:", placeholder='q to quit')
                self.b = ipw.Button(description="Send")
                self.b.on_click(self.chat)
                display(ipw.Box(children=(self.name, self.b)))