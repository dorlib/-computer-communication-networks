CMAN_CHAR = 'C'
SPIRIT_CHAR = 'S'
PLAYER_CHARS = [CMAN_CHAR, SPIRIT_CHAR]
POINT_CHAR = 'P'
FREE_CHAR = 'F'
PASS_CHARS = [CMAN_CHAR, SPIRIT_CHAR, POINT_CHAR, FREE_CHAR]
WALL_CHAR = 'W'
MAX_POINTS = 40
POINT_CHAR = 'P'  # Define the character for points (you can change this as needed)
content = '' 
def load_map(file_path="map.txt"):
    global content
    with open(file_path, 'r') as map:
        content = map.read()
def clear_map(file_path="map.txt"):
    global content
    with open('output.txt', 'w') as map:
        map.write(content)# Define character constants
def update_map(prev_c_pos, prev_s_pos, new_c_pos, new_s_pos, points, 
                        rows=None, file_path="map.txt", collected_points=0, attempts=0, lives =0, overwritten_spot ='F'):
    # Define character to symbol mapping
    symbols = {
        WALL_CHAR: '🟫',
        FREE_CHAR: '🟦',
        CMAN_CHAR: '😊',
        SPIRIT_CHAR: '👻',
        POINT_CHAR: '🟩',
    }

    if rows is None:
        # First-time initialization: read the map and print it fully
        try:
            with open(file_path, 'r') as file:
                rows = [list(row) for row in file.read().strip().split('\n')]

            # Print the initial map
            for row in rows:
                rendered_row = ''.join(symbols.get(char, char) for char in row)
                print(rendered_row)

        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found.")
            return None, collected_points, attempts  # Return failure
    else:
        
        # Update points

        for (i, j), value in points.items():
            rows[i][j] = POINT_CHAR if value == 0 else FREE_CHAR
            
        # Update map: modify only the changed positions
        if prev_c_pos[0] >= 0:  # Clear previous Cman position
            rows[prev_c_pos[0]][prev_c_pos[1]] = FREE_CHAR

        if prev_s_pos[0] >= 0:  # Clear previous Spirit position
            rows[prev_s_pos[0]][prev_s_pos[1]] = overwritten_spot

        # Place Cman at new position
        rows[new_c_pos[0]][new_c_pos[1]] = CMAN_CHAR
        # Place Spirit at new position
        overwirtten_spot = rows[prev_s_pos[0]][prev_s_pos[1]]
        rows[new_s_pos[0]][new_s_pos[1]] = SPIRIT_CHAR
        
       

        # Clear the console and display the updated map with stats
        for row in rows:
            rendered_row = ''.join(symbols.get(char, char) for char in row)
            print(rendered_row)

    # Print stats
    print(f"\nPoints Collected: {collected_points}")
    print(f"Attempts: {attempts}")
    print(f"lives {lives}")

    return rows, overwritten_spot  # Return updated state













#overwritten_spot  # Return updated state



def read_map(path):
    """

    Reads map data and asserts that it is valid.

    Parameters:

    path (str): path to the textual map file

    """
    with open(path, 'r') as f:
        map_data = f.read()
        
        map_chars = set(map_data)
  
        assert map_chars.issubset({CMAN_CHAR, SPIRIT_CHAR, POINT_CHAR, WALL_CHAR, FREE_CHAR, '\n'}), "invalid char in map." 
        assert map_data.count(CMAN_CHAR) == 1, "Map needs to have a single C-Man starting point."
        assert map_data.count(SPIRIT_CHAR) == 1, "Map needs to have a single Spirit starting point."
        assert map_data.count(POINT_CHAR) == MAX_POINTS, f"Map needs to have {MAX_POINTS} score points."

        map_lines = map_data.split('\n')
        assert all(len(line) == len(map_lines[0]) for line in map_lines), "map is not square."
        assert len(map_lines) < 2**8, "map is too tall"
        assert len(map_lines[0]) < 2**8, "map is too wide"

        sbc = all(line.startswith(WALL_CHAR) and line.endswith(WALL_CHAR) for line in map_lines)
        tbc = map_lines[0] == WALL_CHAR*len(map_lines[0]) and map_lines[-1] == WALL_CHAR*len(map_lines[-1])
        bbc = map_lines[0] == WALL_CHAR*len(map_lines[0]) and map_lines[-1] == WALL_CHAR*len(map_lines[-1])
        assert sbc and tbc and bbc, "map border is open."

        return map_data
    

