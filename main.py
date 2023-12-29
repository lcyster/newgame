import os
import openai
from langchain.agents import load_tools

class Chat:
  def __init__(self):
    self.messages = []

  def addSystemContent(self, content):
    self.addMessage({"role": "system", "content": content})

  def addAssistentContent(self, content):
    self.addMessage({"role": "assistant", "content": content})

  def addUserContent(self, content):
    self.addMessage({"role": "user", "content": content})

  def addMessage(self, message):
    self.messages.append(message)

  def talk(self, content):
    self.addUserContent(content)

    response = openai.ChatCompletion.create(
      model = "gpt-3.5-turbo", 
      messages = self.messages,
      max_tokens = 200,
      temperature = 0.9)

    message = response.choices[0].message
    self.addMessage(message);

    print(message.content)

class Place:
  def __init__(self, description):
    self.description = description


forest = Place("You are in a forest")




chat = Chat()
systemPrompt = """"You are a Dungeon Master for a Dungeons & Dragons game. You will be given a brief description of a place in the game. Write a quick paragraph about the place."""

prompt = systemPrompt + str(forest)

chat.addSystemContent(prompt)
chat.talk(prompt)

print("hi")