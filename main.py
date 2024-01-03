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

  def __init__(self, description, north, south, east, west):
    self.description = description
    self._north = north
    self._south = south
    self._east = east
    self._west = west

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


#locations

forest = Place(
    "The player is in an oak forest. There is a shed to the north. There is a river to the south. There is a clearing to the east. There is a rock to the west.",
    None, None, None, None)
shed = Place("The player is inside of a shed. There is a forest to the south.",
             None, forest, None, None)
forest.setNorth(shed)
river = Place(
    "The player is standing at the bank of a river. There is  forest to the north.",
    forest, None, None, None)
forest.setSouth(river)
clearing = Place(
    "The player is standing in the middle of a clearing filled with small flowers. To the west is a forest.",
    None, None, None, forest)
forest.setEast(clearing)
rock = Place(
    "The player is standing at the foot of a huge rock. There is a forest to the east.",
    None, None, forest, None)
forest.setWest(rock)

location = forest

chat = Chat()
systemPrompt = """You are a game master that understands the state of the game through commands. Talk to the player understand there request and turn it into commands that will send you information about the game state. When you have the game state relay it back to the user in plain english.

State a commands on a line by itself. The command will intercept your reponse and provide a response you can relay to the user

For example:
@move(north)

The following commands are available:
@move(direction) - This command changes the player's location. The action @move takes a parameter of direction. The available directions are north and south.
@describe - This command describes the player's surroundings.
@location - This command describes the players location
"""

chat.addSystemContent(systemPrompt)
chat.addAssistantContent("@location")
chat.addUserContent(location.getDescription())

chat.addAssistantContent("Welcome the player and describe thier location")

prompt = "Hi"
play = True
while play:
  answer = chat.talk(prompt)
    
  if answer is None:
    print("(debug.no_answer -> what?)")
    prompt = "what?"
    continue
  elif answer.startswith("@"):  
      
    if "@move(north)" in answer:
      nextLocation = forest.north()
      if nextLocation is not None:
        location = nextLocation
        prompt = "The player moves north."
      else:
        prompt = "The player can't go that way."
    elif "@move(south)" in answer:
        nextLocation = forest.south()
        if nextLocation is not None:
          location = nextLocation
          prompt = "The player moves south."
        else:
          prompt = "The player can't go that way."
    elif "@location" in answer:
      prompt = location.getDescription()
    elif "@describe" in answer:
      prompt = location.getDescription()
        
    print("(debug: " + answer + " -> " + prompt + ")")
  else:
    print(answer)
    prompt = input("> ")

