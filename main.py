from enum import IntEnum
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
import time
import re

from chat import Chat


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

  def __init__(self, name, species, description, location):
    self.name = name
    self.species = species
    self.description = description
    self.location = location
    self.inventory = []

  def getName(self):
    return self.name

  def getSpecies(self):
    return self.species

  def getDescription(self):
    return self.description

  def getInventory(self):
    prompt = f"{self.name} has the following items in their inventory: "
    for item in self.inventory:
      prompt += f"{item}, "


class Mob:
  #difference between mob and character: mob cannot speak; are enemies that can just fight. characters can interact w player
  def __init__(self, name, description, health, damage, hostility):
    self.name = name
    self.description = description
    self.health = health
    self.damage = damage
    self.hostility = hostility

  def getName(self):
    return self.name

  def getDescription(self):
    return self.description

  def getHealth(self):
    return self.health

  def getDamage(self):
    return self.damage


class Toolbox:

  def __init__(self):
    self.tools = []
    self.pattern = re.compile(
        r'@(?P<command_name>\w+)(\((?P<parameter>[^)]*)\))?')

  def perform(self, toolPrompt):
    print("Toolbox: ", toolPrompt, "\n")
    match = self.pattern.search(toolPrompt)
    response = ""

    if match:
      command = match.group('command_name')
      parameter = match.group('parameter')

      for tool in self.tools:
        if command == tool.getName():
          response = response + tool.perform(parameter) + "\n"

    return response

  def getTools(self):
    return self.tools

  def addTool(self, tool):
    self.tools.append(tool)


class HelpTool:

  def __init__(self, toolbox):
    self.toolbox = toolbox

  def getName(self):
    return "help"

  def getDescription(self):
    return "lists available tools."

  def perform(self, parameters):
    response = "The following are the available command. \n"
    for tool in toolbox.getTools():
      response += f"  @{tool.getName()}: {tool.getDescription()} \n"

    print("!! helpTool: " + response)
    return response


class MoveTool:

  def __init__(self):
    pass
  
  def getName(self):
    return "move(direction)"
  
  def getDescription(self):
    return "moves the player location in direction north, south, east or west."
  
  def perform(self, parameters):
    print("move:", parameters)
    return "you tried to move"




forest = Place(
    "Forest",
    "The player is in an oak forest. There is a shed to the north. There is a river to the south. There is a clearing to the east. There is a rock to the west.",
    None, None, None, None)
key = Item("key", "A small golden key used to unlock the door to the shed",
           "keys")
forest.addThings(key)

shed = Place(
    "Shed",
    "The player is standing right outside of a shed. There is a door. The door is locked shut. You cannot go through the door because it is locked shut. You cannot see inside because the door is locked shut. There is a forest to the south.",
    None, forest, None, None)
forest.setNorth(shed)
hoe = Item(
    "gardening hoe",
    "An old hoe used to garden crops, but can also be used as a weapon. Found inside the locked shed. Can only be seen and accessed after using the key.",
    "weapons")
shed.addThings(hoe)
#how do i make it so that the sword can only be found when you open the door and go inside the shed? can i make it so that

river = Place(
    "River",
    "The player is standing at the bank of a river. There is  forest to the north.",
    forest, None, None, None)
forest.setSouth(river)
boar = Mob("Boar", "A large, black aggressive boar", "15", "5", True)
river.addThings(boar)

clearing = Place(
    "Clearing",
    "The player is standing in the middle of a clearing filled with small flowers. To the west is a forest.",
    None, None, None, forest)
forest.setEast(clearing)
Lyra = Character("Lyra", "elf",
                 "An elven girl with white hair and pointed ears.", "clearing")
#how to make it so that the player can talk
#how to set as a thing in the location? should i just use addThings like i do with items or should i set it as something different?
clearing.addThings(Lyra)

rock = Place(
    "Rock",
    "The player is standing at the foot of a huge rock. There is a forest to the east.",
    None, None, forest, None)
forest.setWest(rock)

#chat setup
chat = Chat()
systemPrompt = """You are a narrator that understands the state of the game through commands. Talk to the player. Turn the player's requests into commands.

Commands are in the form @command(parameters). Where the brackets and parameters are optional if there are no parameters.

"""

location = forest
inventory = []

chat.addSystemContent(systemPrompt)
chat.addAssistantContent("@location")
chat.addUserContent(location.getName())
chat.addAssistantContent("Welcome the player and describe their location.")

player = Chat()
systemPrompt = "You are an adventuerer in a text based game. You are in a forest. You can move north, south, east, and west."
player.addSystemContent(systemPrompt)

prompt = "Use the @help command."
play = True
toolbox = Toolbox()

toolbox.addTool(HelpTool(toolbox))
toolbox.addTool(MoveTool())



while play:
  print(f"prompt: {prompt}")
  answer = chat.talk(prompt)
  print(f"answer: {answer}")
  
  if answer is None:
    print("(debug.no_answer -> what?)")
    prompt = "What?"
    continue

  prompt = ""
  prompt += toolbox.perform(answer) + "\n"

  print("\033[1mNarrator:\033[0m ", answer, "\n")
  prompt += input("> ") + "\n"
  print("> ", prompt)
  time.sleep(1.5)
