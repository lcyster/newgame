from collections.abc import ItemsView
from enum import IntEnum
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
  - see here on how to setup a secret: https://docs.replit.com/programming-ide/workspace-features/storing-sensitive-information-environment-variables"""
        )
  os.exit(1)


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
    temperature=0.9)

    message = response.choices[0].message
    self.addMessage(message)
    return message.content
      

class Place:

  def __init__(self, name, description, north, south, east, west):
    self.name = name
    self.description = description
    self._north = north
    self._south = south
    self._east = east
    self._west = west
    self.items = []
    self.inventory = []

  def getName(self):
    return self.name

  def getDescription(self):
    return self.description

  def north(self):
    return self._north

  def south(self):
    return self._south

  def east(self):
    return self._east

  def west(self):
    return self._west

  def setNorth(self, north):
    self._north = north

  def setSouth(self, south):
    self._south = south

  def setEast(self, east):
    self._east = east

  def setWest(self, west):
    self._west = west

  def getThings(self):
    return self.items
  
  def addItem(self, item):
    self.items.append(item)
    return (f"{ItemsView} added to {self.name}.")
  
  def removeItem(self, item):
    if item in self.items:
      self.items.remove(item)
      return (f"{item} removed from {self.name}.")
    else:
      return (f"{item} not found in {self.name}.")

  def takeItem(self, item):
    if item in self.items:
      self.items.remove(item)
      self.inventory.append(item)
      return (f"{item} taken from {self.name} and added into inventory.")
    else:
      return (f"{item} not found in {self.name}.")

  def findItem(self, item):
    if item in self.items:
      return True
    else:
      return False


#locations
forest = Place("Forest", "The player is in an oak forest. There is a small golden key in the forest. There is a shed to the north. There is a river to the south. There is a clearing to the east. There is a rock to the west.", None, None, None, None)
forest.addItem("key")
shed = Place("Shed", "The player is standing right outside of a shed. The only door in is  locked tightly shut. There is a forest to the south.", None, forest, None, None)
forest.setNorth(shed)
river = Place("River", "The player is standing at the bank of a river. There is  forest to the north.",
forest, None, None, None)
forest.setSouth(river)
clearing = Place("Clearing", "The player is standing in the middle of a clearing filled with small flowers. To the west is a forest.", None, None, None, forest)
forest.setEast(clearing)
rock = Place("Rock", "The player is standing at the foot of a huge rock. There is a forest to the east.", None, None, forest, None)
forest.setWest(rock)

#chat setup
chat = Chat()
systemPrompt = """You are a game master that understands the state of the game through commands. Talk to the player. Turn the player's requests into commands.

Print the commands on a line by itself. 

!!!CONFUSING FIX THIS PART!!!The command will intercept your reponse and provide a response you can relay to the user. Print the exact description of each location.


For example:
@move(north)

The following commands are available:
@move(direction) - This command changes the player's location. The action @move takes a parameter of direction. The available directions are north and south.
@describe - This command prints the exact description of each location.
@location - This command describes the players location
@find(item) - This command finds an item in the player's current location. The action @find takes a parameter of item.
@take(item) - This command takes an item from the player's current location and adds it to their inventory. The action @take takes a parameter of item.

You can only respond to the user using the given information about each location. Do not make any information up.
"""

location = forest

chat.addSystemContent(systemPrompt)
chat.addAssistantContent("@location")
chat.addUserContent(location.getName())

chat.addAssistantContent("Welcome the player and describe their location.")


prompt = "Hi"
play = True

while play:
  answer = chat.talk(prompt)
    
  if answer is None:
    print("(debug.no_answer -> what?)")
    prompt = "what?"
    continue
  elif answer.startswith("@"): 
    if "@move" in answer:
      print("@move reached")
      direction = answer.split("(")[1].split(")")[0]
      next_location = getattr(location, direction)()
      if next_location is not None:
        print("location moved")
        location = next_location
        prompt = f"The player moves {direction}, to the {location.getName()}"
      else:
        prompt = f"The player can't go {direction}"
    
    elif "@location" in answer or "@describe" in answer:
      prompt = location.getDescription() + "Only use the given information to describe the player's location."
      print("(debug: " + answer + " -> " + prompt + ")")
    
    elif "@find" in answer:
      item = answer.split("(")[1].split(")")[0]
      if location.findItem(item) is True:
        print("item found!!!!")
        prompt = f"The {item} is in {location.getName()}"
      elif location.findItem(item) is False:
        print("item not found!!!!!!")
        prompt = f"{item} is not found in {location.getName()}"
      
    elif "@take" in answer:
      item = answer.split("(")[1].split(")")[0]
      if location.findItem(item) is True:
        print("item taken!!!")
        location.takeItem(item)
        prompt = f"The {item} is taken from {location.getName()} and added to the player's inventory."
      elif location.findItem(item) is False:
        print("item not taken!!!!")
        prompt = f"{item} is not found in {location.getName()}"
          
    else:
      pass
  
  else:
    print(answer)
    prompt = input("> ")