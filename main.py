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
    self.things = []

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
    return self.things
  
  def addThings(self, thing):
    self.things.append(thing)
    return (f"{thing} dropped in {self.name}.")
  
  def removeThings(self, thing):
    if thing in self.things:
      self.things.remove(thing)
      return (f"{thing} removed from {self.name}.")
    else:
      return (f"{thing} not found in {self.name}.")

  def findThings(self, thingName):
    for thing in self.things:
      if thing.name == thingName:
        return thing
    return None

  def printInventory(self):
    if len(self.things) == 0:
      print("Inventory is empty.")
    elif len(self.things) >= 1:
      print("")

class Item:
  def __init__(self, name, description, category):
    self.name = name
    self.description = description
    self.category = category

  def getName(self):
    return self.name

  def getDescription(self):
    return self.description

class Character:
  def __init__(self, name, species, description):
    self.name = name
    self.species = species
    self.description = description

  def getName(self):
    #would it be confusing to write getName for both item and character?
    return self.name

  def getSpecies(self):
    return self.species

  def getDescription(self):
    return self.description

class Mob:
  #difference between mob and character: mob cannot speak; are enemies that can just fight. characters can interact w player
  def __init__(self, name, description, health, damage):
    self.name = name
    self.description = description
    self.health = health
    self.damage = damage

  def getName(self):
    return self.name

  def getDescription(self):
    return self.description

  def getHealth(self):
    return self.health

  def getDamage(self):
    return self.damage


forest = Place("Forest", "The player is in an oak forest. There is a shed to the north. There is a river to the south. There is a clearing to the east. There is a rock to the west.", None, None, None, None)
key = Item("key", "A small golden key used to unlock the door to the shed", "keys")
forest.addThings(key)

shed = Place("Shed", "The player is standing right outside of a shed. There is a door. The door is locked shut. You cannot go through the door because it is locked shut. You cannot see inside because the door is locked shut. There is a forest to the south.", None, forest, None, None)
forest.setNorth(shed)
hoe = Item("gardening hoe", "An old hoe used to garden crops, but can also be used as a weapon. Found inside the locked shed. Can only be seen and accessed after using the key.", "weapons")
shed.addThings(hoe)
#how do i make it so that the sword can only be found when you open the door and go inside the shed? can i make it so that 


river = Place("River", "The player is standing at the bank of a river. There is  forest to the north.",
forest, None, None, None)
forest.setSouth(river)
boar = Mob("Boar", "A large, black aggressive boar", "15", "5")
river.addThings(boar)

clearing = Place("Clearing", "The player is standing in the middle of a clearing filled with small flowers. To the west is a forest.", None, None, None, forest)
forest.setEast(clearing)

rock = Place("Rock", "The player is standing at the foot of a huge rock. There is a forest to the east.", None, None, forest, None)
forest.setWest(rock)

#chat setup
chat = Chat()
systemPrompt = """You are a narrator that understands the state of the game through commands. Talk to the player. Turn the player's requests into commands.

Print the commands on a line by itself. 

The command will intercept your reponse and provide a response you can relay to the user. Print the exact description of each location.


For example:
@move(north)

The following commands are available:
@move(direction) - This command changes the player's location. The action @move takes a parameter of direction. The available directions are north and south.
@describe - This command prints the exact description of each location.
@location - This command describes the players location
@find(item) - This command finds an item in the player's current location. The action @find takes a parameter of item.
@take(item) - This command takes an item from the player's current location and adds it to their inventory. The action @take takes a parameter of item.
@checkInventory - This command prints out the items in the player's inventory.

You can only respond to the user using the given information about each location. Do not make any information up.
"""

location = forest
inventory = []

chat.addSystemContent(systemPrompt)
chat.addAssistantContent("@location")
chat.addUserContent(location.getName())
chat.addAssistantContent("Welcome the player and describe their location.")

prompt = "Hi!"
play = True

while play:
  answer = chat.talk(prompt)
    
  if answer is None:
    print("(debug.no_answer -> what?)")
    prompt = "What?"
    continue
  
  elif answer.startswith("@"): 
    if "@move" in answer:
      try: 
        direction = answer.split("(")[1].split(")")
        print("@move reached ", direction)
        next_location = getattr(location, direction)()[0]
      except IndexError:  
        prompt = "What?"
        continue

      if next_location is not None:
        location = next_location
        prompt = f"The player moves {direction}, to the {location.getName()}"

        for items in location.getThings():
          prompt += f" There is a {items.getDescription()} here."

        print (prompt, "\n")
      else:
        prompt = f"The player can't go {direction}"
    
    elif "@location" in answer or "@describe" in answer:
      prompt = location.getDescription() + "Only use the given information to describe the player's location."
      print("(debug: " + answer + " -> " + prompt + ")")
    
    elif "@find" or "@take" in answer:
      for item in location.getThings():
        print(item.getName())
        
      try: 
        itemName = answer.split("(")[1].split(")")[0]
        print(itemName)
      except IndexError:  
        prompt = "What?"
        break

      item = location.findThings(itemName)
      if item is not None:
        location.removeThings(itemName)
        inventory.append(item)
        prompt = f"The {item} is taken from {location.getName()} and added to the player's inventory."
      else:
        prompt = f"{item} is not found in {location.getName()}"

    elif "@checkInventory" in answer:
      prompt = "The player's inventory contains: "
      
      for item in inventory:
        prompt += (item)
        
    else:
      pass
  
  else:
    print(answer)
    prompt = input("> ")