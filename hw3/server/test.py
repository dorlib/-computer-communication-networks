
from cman_game import Player, Direction, Game


def set_points(bytes_list):
    """
    Converts a byte list representation of points back into a dictionary
    of (i, j) -> value pairs where 1 represents a point and 0 represents no point.
    """
    global board_width, board_height, points
    value = 0
    for i, byte in enumerate(bytes_list):
        value |= (byte << (8 * (4 - i)))
    # Convert the byte string into a bit string
    bit_list = list(bin(value)[2:])

    points_list =  sorted(points.keys(), key=lambda x: (x[0], x[1]))
    # Rebuild the points dictionary
    points = {point: int(bit) for point, bit in zip(points_list, bit_list)}
    return points

if __name__ == "__main__":
    points = Game("map.txt").points # initial value of points
    
    l = [0,0,128,0,0]
    #print(points)
    set_points(l)
    print(points)
    