import keyboard
def get_pressed_keys(keys_filter=None):
    """
    Returns a list of all pressed keys (lower case) at the time of the call.

    Parameters:
    keys_filter (list[str]): A list of specific keys to check. If omitted, every key is checked.

    Returns:
    list[str]: A list of currently pressed keys.
    """
    if keys_filter:
        # Filter only the keys from the provided list
        pressed_keys = [key for key in keys_filter if keyboard.is_pressed(key)]
    else:
        # Get all currently pressed keys
        pressed_keys = keyboard._pressed_events.keys()  # Internal method to get pressed keys
        pressed_keys = [key.lower() for key in pressed_keys]
    
    return pressed_keys

if __name__ == "__main__":
    while True:
        print (get_pressed_keys(['w', 'a', 's', 'd', 'q']))