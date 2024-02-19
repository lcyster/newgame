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

  if answer.startswith("@move"):
    if "@move" in answer:
      try:
        direction = str(answer.split("(")[1].split(")"))
        print(direction)
        next_location = getattr(location, direction)()[0]

      except (IndexError, AttributeError):
        prompt += "Always print a move command in the format move(direction).\n"
        continue

      if next_location is not None:
        location = next_location
        prompt += f"The player moves {direction}, to the {location.getName()}\n"

        for items in location.getThings():
          prompt += f" There is a {items.getDescription()} here.\n"

          if isinstance(item, Mob) and item.hostility():
            prompt += f" A {item.getName()} attacked you! It has {item.getDamage()} damage.\n"

        print(prompt, "\n")

      else:
        prompt += f"The player can't go {direction}\n"

    elif "@location" in answer or "@describe" in answer:
      prompt += location.getDescription(
      ) + "Only use the given information to describe the player's location."
      print("(debug: " + answer + " -> " + prompt + ")\n")

    elif "@find" or "@take" in answer:
      for item in location.getThings():
        print(item.getName())

      try:
        itemName = answer.split("(")[1].split(")")[0]
        print(itemName)
      except IndexError:
        prompt += "Take What?\n"
        continue

      item = location.findThings(itemName)
      if item is not None:
        location.removeThings(itemName)
        inventory.append(item)
        prompt += f"The {item} is taken from {location.getName()} and added to the player's inventory.\n"
      else:
        prompt += f"{item} is not found in {location.getName()}\n"

    elif "@checkInventory" in answer:
      prompt += "The player's inventory contains: \n"

      for item in inventory:
        prompt += (item)

    elif "@talk" in answer:
      try:
        characterName = answer.split("(")[1].split(")")[0]
        print(characterName)
      except IndexError:
        prompt += "What?\n"
        continue

    else:
      pass

  else:
    print("\033[1mNarrator:\033[0m ", answer, "\n")
    prompt += input("> ") + "\n"
    #prompt = player.talk(answer) + "\n" + toolbox.perform(prompt)
    print("> ", prompt)
    time.sleep(1.5)
