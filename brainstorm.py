from ollama import chat, ChatResponse
import yaml
import typing


def make_note_for_future_reference( note: str):
    """Make notes for future reference"""
    """
    Make any persistent notes to record your future plans and todos in any text format that is the most effective to be read back in later.
    Every call to this tool destroys any past notes recorded, so include everything you want for the next pass

    Args:
      note: The full message to be recorded for future reference
    """
    print(f"NOTE MADE: {note}")
    with open('note.txt', 'w') as notefile:
        notefile.write(note)
    return 'Success'

def list_game_material_ids() -> list:
    """Look up a list of the IDs for all the materials in the game"""
    """
    These IDs can be looked up using the read_game_material_info function to learn the specifics about each material

    Returns:
        A list of material IDs
    """

    # Read and parse the YAML file
    with open('materials.yaml', 'r') as file:
        data = yaml.safe_load(file)
    materials = data.get('materials', {})
    return materials.keys()

def read_game_material_info(material_id: str) -> dict:
    """Look up a specific material ID and return a dictionary of information about that material"""
    """
    Args:
        material_id: The string material ID to look up

    Returns:
        All of the recorded information about that material
    """

    with open('materials.yaml', 'r') as file:
        data = yaml.safe_load(file)
    materials = data.get('materials', {})
    return materials.get(material_id, {})

def write_game_material_info(material_id: str, material_info: dict):
    """Write a new economic material to the game database"""
    """
    Args:
        material_info: A dictionary of the new material ID and all of its properties in the same format as the ither exiting materials
    """

    print({ material_id: material_info})
    with open('materials.yaml', 'r') as file:
        data = yaml.safe_load(file)
    data['materials'].update( {material_id: material_info})
    with open('materials.yaml', 'w') as file:
        yaml.dump(data, file)
    return 'Success'



available_functions = {
  'list_game_material_ids': list_game_material_ids,
  'read_game_material_info': read_game_material_info,
  'make_note_for_future_reference': make_note_for_future_reference,
  'write_game_material_info': write_game_material_info,
}

messages = [{'role': 'user', 
             'content': """We need to develop additional economic materials and resources for a space RPG similar to the ones already listed in the game materials database that you can access with the provided tools.

Please come up with as many additional resources as you like, but check the existing materials to make sure your new suggestions match the same format as the existing materials.
We are looking for realism here, so focus on real world materials and devices and less on pretend elements or abstract concepts like wind extract or an ionized cloud or made up elements that don't exist. Write all of your new ideas to the database; we will review them and pick out the best ones later.

Pick one industry or supply chain to focus on and develop.
Any additional ideas or todo items to check on can be recorded as a note to yourself for the next pass over the list.
Also use the note to yourself for recording any plans for the formatting of items in the database and any industries which have already been covered or are still on your list to flesh out in later passes.
The note to yourself will be provided after this prompt if you have previously written one.

We also need to validate that all of the dependencies for each materail exists; don't worry about the facilities for crafting, we can make up as many of those as we need and we will flesh out their details later.
If a material already exists in the database but you feel that it's missing fields, feel free to overwrite it with the additional information that was missing.
"""
             }]
with open("note.txt", "r") as file_object:
    # Perform reading operations here
    content = file_object.read()
    if content:
        messages.append({'role': 'user', 'content': f'Note you left yourself from the last pass: {content}' })
        print (f'AIs note to self: {content}')

while True:
    try:
        response: ChatResponse = chat(
                model='qwen3:30b-a3b-thinking-2507-q4_K_M',
            messages=messages,
            tools = available_functions.values(),
            think=True,
        )
    except Exception as e:
        print(f" -- Caught an Exception: {e}")
        messages.append({'role': 'user', 'content': f"Caught an exception from the chat call: {e}"  })
        continue
    messages.append(response.message)
    print("Thinking: ", response.message.thinking)
    print("Content: ", response.message.content)
    if response.message.tool_calls:
        for tc in response.message.tool_calls:
            if tc.function.name in available_functions:
                print(f"Calling {tc.function.name} with arguments {tc.function.arguments}")
                try:
                    result = available_functions[tc.function.name](**tc.function.arguments)
                    print(f"Result: {result}")
                    # add the tool result to the messages
                    messages.append({'role': 'tool', 'tool_name': tc.function.name, 'content': str(result)})
                except Exception as e:
                    print(f" -- Caught an Exception: {e}")
                    messages.append({'role': 'tool', 'tool_name': tc.function.name, 'content': f"Caught an exception from the tool: {e}"  })
            else:
                print(f"Unknown function call: {tc}")
                messages.append({'role': 'tool', 'tool_name': tc.function.name, 'content': f"This is an unknown tool call, please check your syntax and spelling"  })
    else:
        # end the loop when there are no more tool calls
        break
    # continue the loop with the updated messages
    print('\n\n')
