from util import LanguageModel, PrefixedChatAdapter

API = 'lambda'  # or 'openai'
MAX_TOKEN = 100

lm_wrapper = LanguageModel(max_tokens=MAX_TOKEN, service=API)
custom_adapter = PrefixedChatAdapter()

def configure_dspy(dspy):
    dspy.configure(lm=lm_wrapper.lm, adapter=custom_adapter)