import os
import openai

class Chat:

  def __init__(self):
    self.messages = []
  
  def addSystemContent(self, content):
    self.addMessage({"role": "system", "content": content})
  
  def addAssistantContent(self, content):
    self.addMessage({"role": "assistant", "content": content})
  
  def addUserContent(self, content):
    self.addMessage({"role": "user", "content": content})
  
  def addMessage(self, message):
    self.messages.append(message)
  
  def talk(self, content):
    self.addUserContent(content)
  
    response = openai.chat.completions.create(model="gpt-3.5-turbo",
                                              messages=self.messages,
                                              max_tokens=200,
                                              temperature=0)
  
    message = response.choices[0].message
    if message is not None:
      self.addMessage(message)
      return message.content
    else:
      return ""

try:
  openai.api_key = os.environ['OPENAI_API_KEY']
except KeyError:
  print("""Please setup an OPENAI_API_KEY secret.
  - get an openapi secret here:  https://platform.openai.com/account/api-keys
  - see here on how to setup a secret: https://docs.replit.com/programming-ide/workspace-features/storing-sensitive-information-environment-variables"""
        )
  os.exit(1)