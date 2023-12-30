import os
from langchain.agents import load_tools
from pydantic.networks import EmailStr
import openai
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.chat_models.openai import ChatOpenAI
from langchain.tools import BaseTool, StructuredTool, Tool, tool
from langchain.chains.llm_math.base import LLMMathChain
from langchain.memory import ConversationBufferMemory

try:
  openai.api_key = os.environ['OPENAI_API_KEY']
except KeyError:
  print("""Please setup an OPENAI_API_KEY secret.
  - get an openapi secret here:  https://platform.openai.com/account/api-keys
  - see here on how to setup a secret: https://docs.replit.com/programming-ide/workspace-features/storing-sensitive-information-environment-variables""" )
  os.exit(1)

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

    response = openai.chat.completions.create(
      model = "gpt-3.5-turbo", 
      messages = self.messages,
      max_tokens = 200,
      temperature = 0.9)

    message = response.choices[0].message
    self.addMessage(message);

    print(message.content)

class Place:
  def __init__(self, description, north, south, east, west):
    self.description = description
    self._north = north
    self._south = south
    self._east = east
    self._west = west

  def getDescription (self):
    return self.description

  def north (self):
    return self._north

  def south (self):
    return self._south

  def east (self):
    return self._east

  def west (self):
    return self._west 
  
  def setNorth (self, north):
    self._north = north
    
  def setSouth (self, south):
    self._south = south

  def setEast (self, east):
    self._east = east

  def setWest (self, west):
    self._west = west

#i think i did this wrong bc i ran into an issue later on where nextLocation = location.north didnt exist?
forest = Place("You are in an oak forest. There is a shed to the north.", None, None, None, None)
shed = Place("You are inside of a shed. There is a forest to the south.", None, forest, None, None)
forest.setNorth(shed)

location = forest

chat = Chat()
systemPrompt = """You are a Dungeon Master for a Dungeons & Dragons game. You will be given a brief description of a place in the game. Write a quick paragraph about the place. If the player states to move towards an area, enter twice and then state the direction. For example:

direction: north"""

command = ""
prompt = forest.getDescription()


while command != "quit":
  
  chat.addSystemContent(systemPrompt)
  
  answer = chat.talk(prompt)

  command = input("> ")

  if "north" in command:
      nextLocation = shed
      location = nextLocation
      print("here.")

  #it doesn't use the tool no matter what
  def move(location, nextLocation): 
    nextLocation = forest.north
    location = nextLocation
    print(location.getDescription())

  move_tool = Tool.from_function(
      func=move, 
      name="Movement Tool",
      description="useful to move location"
  )


  
  
  prompt = location.getDescription() + command
  print("did not use tool", location.getDescription())