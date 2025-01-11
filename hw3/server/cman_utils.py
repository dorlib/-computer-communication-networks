import pynput, time, msvcrt
import struct 
import keyboard

name_to_opcode = {
    'join': b"\x00",
    'movement': b"\x01", 
    'quit':b"\x0F", 
    "update_state":b"\x80", 
    "end": b"\x8F", 
    "error": b"\xFF"
}

messages = {
        b'\x00': {
            "OPCODE": b"\x00",
            "ROLE": b"\x00",
            "format_string": "BB", 
           # "name": 'join'
        },
        b"\x01": { #movement
            "OPCODE": b"\x01",
            "DIRECTION": b"\x00",
            "format_string": "BB",
       #     "name": 'movement'
        },
        b"\x0F": {
            "OPCODE": b'\x0F',
            "format_string": "B", 
            #"name": 'quit'
        },
        b"\x80": {
            "OPCODE": b"\x80",
            "FREEZE": b"\x00",
            "C_COORDS": [b"\xFF", b"\xFF"],
            "S_COORDS": [b"\xFF", b"\xFF"],
            "ATTEMPTS": b"\x00",
            "COLLECTED": [b"\x00", b"\x00", b"\x00", b"\x00", b"\x00"],
            "format_string": "BB2B2BB5B"
            #"name": "update_state"
        },
        b"\x8F": {
            "OPCODE": b"\x8F",
            "WINNER": [b"\x00", b"\x00"],
            "S_SCORE": [b"\x00", b"\x00"],
            "C_SCORE": b"\x00",
            "format_string": "B2B2BB"
            #"name": "end"
        },
        b"\xFF": {
            "OPCODE": b"\xFF",
            "DATA": [b"\x00", b"\x00", b"\x00", b"\x00", b"\x00", b"\x00", b"\x00", b"\x00", b"\x00", b"\x00", b"\x00"],
            "format_string": "B11B"
            #"name": "error"
        }
    }



def pack_message(message_name):
    # Ensure the message exists        
    try: 
        message = messages[message_name]
    except KeyError:
        raise ValueError(f"Unknown message name: {message_name}")

    format_string = message["format_string"]

    # Flatten the dictionary values dynamically
    values = []
    for key, value in message.items():
        if key == "format_string":
            continue
        
        if isinstance(value, bytes):
            int_value = int.from_bytes(value, byteorder='big')
            values.append(int_value)  # Convert byte to integer
        elif isinstance(value, list):
            # If the value is a list, unpack each element in the list
            values.extend([item if isinstance(item, int) else int.from_bytes(item, byteorder='big') for item in value])
        else: 
            values.append(value)
    # Pack the message
    packed_message = struct.pack(format_string, *values)
    
    return packed_message

def unpack_message(packed_message):
    # Unpack the message to get the opcode (first byte)
    opcode = chr(packed_message[0]).encode('latin1')
    
    # Ensure the opcode exists in the messages dictionary
    if opcode not in messages:
        raise ValueError(f"Unknown opcode: {opcode}")
    
    message = messages[opcode]
    format_string = message["format_string"]
    
    # Unpack the message using the format string
    unpacked_values = struct.unpack(format_string, packed_message)
    
    # Prepare a dictionary to store the unpacked values
    unpacked_message = {}
    idx = 0
    
    # Iterate through the keys and unpack the values
    for key, value in message.items():
        if key == "format_string":
            continue
        if isinstance(value, list):
            # Handle list: Assign a slice of unpacked values to the key
            list_length = len(value)  # Length of the expected list
            unpacked_message[key] = list(unpacked_values[idx:idx + list_length])
            idx += list_length
        else:
            if key == "OPCODE":
                unpacked_message[key] = chr(unpacked_values[idx]).encode('latin1')
            # Handle single values
            else:
                unpacked_message[key] = unpacked_values[idx]
            idx += 1

    return unpacked_message


def _flush_input():
    try:
        while msvcrt.kbhit():
            msvcrt.getch()
    except ImportError:
        import sys, termios
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)
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
    time.sleep(0.06)
    return pressed_keys


def clear_print(*args, **kwargs):
    """

    Clears the terminal before calling print()

    """
    print("\033[H\033[J", end="")
    print(*args, **kwargs)
