def get_distance(input_string,data_string):
    """
    function to calculate the minimum edit distance between two strings
    :param input_string: string to be compared 
    :param data_string: string to be compared against (will be from the dataset)
    """
    input_string_length = len(input_string)
    data_string_length = len(data_string)

   
    """
    the algorithm is as follows:
    1. Create a 2D array of size (input_string_length + 1) x (data_string_length + 1)
    2. Initialize the first row and column of the array with indices
    3. min distance [0,i]= i+1 additions
    4. min distance [i,0]= i+1 deletions
    5. for indices other than first row and first collumn:
    min distance[i,j] = min(min_distance[i-1,j]+1 #deletion cost, min_distance[i,j-1]+1 # addition cost ,min_distance[i-1,j-1]+cost_substitution(input_string[i],data_string[j]) # substitution cost) 
    """
     # 2d array storing distances' values

    min_distance= [[0 for i in range(data_string_length+1)] for j in range(input_string_length+1)]

    # initialize first row:

    for i in range(data_string_length+1):
        min_distance[0][i]= i
    
    # first column:
    for i in range(input_string_length+1):
        min_distance[i][0]= i

    # rest of the matrix:

    for i in range(1,input_string_length+1):
        for j in range(1,data_string_length+1):
            min_distance[i][j] = min(          
                min_distance[i-1][j]+1  ,  #deletion cost
                min_distance[i][j-1]+1  ,   # addition cost
                min_distance[i-1][j-1] + substitution_cost(input_string[i-1], data_string[j-1]) ) # substitution cost


    return min_distance[input_string_length][data_string_length]

def substitution_cost(character1 , character2):

    """
    this function uses a heuristic to determine the cost of substitution
    if same characters , cost=0
    if different characters , cost= sqrt of ecludian distance between their place in the keyboard
    """
    if character1 == character2:
        return 0
    else:
        # QWERTY keyboard layout with letters, digits, and common punctuation
        keyboard = {
            # Row 0 (top row with numbers & symbols)
            '`': (0, 0), '~': (0, 0),
            '1': (0, 1), '!': (0, 1),
            '2': (0, 2), '@': (0, 2),
            '3': (0, 3), '#': (0, 3),
            '4': (0, 4), '$': (0, 4),
            '5': (0, 5), '%': (0, 5),
            '6': (0, 6), '^': (0, 6),
            '7': (0, 7), '&': (0, 7),
            '8': (0, 8), '*': (0, 8),
            '9': (0, 9), '(': (0, 9),
            '0': (0, 10), ')': (0, 10),
            '-': (0, 11), '_': (0, 11),
            '=': (0, 12), '+': (0, 12),

            # Row 1 (QWERTY row)
            'q': (1, 0), 'w': (1, 1), 'e': (1, 2), 'r': (1, 3), 't': (1, 4),
            'y': (1, 5), 'u': (1, 6), 'i': (1, 7), 'o': (1, 8), 'p': (1, 9),
            '[': (1, 10), '{': (1, 10),
            ']': (1, 11), '}': (1, 11),
            '\\': (1, 12), '|': (1, 12),

            # Row 2 (ASDF row)
            'a': (2, 0), 's': (2, 1), 'd': (2, 2), 'f': (2, 3), 'g': (2, 4),
            'h': (2, 5), 'j': (2, 6), 'k': (2, 7), 'l': (2, 8),
            ';': (2, 9), ':': (2, 9),
            "'": (2, 10), '"': (2, 10),

            # Row 3 (ZXCV row)
            'z': (3, 0), 'x': (3, 1), 'c': (3, 2), 'v': (3, 3), 'b': (3, 4),
            'n': (3, 5), 'm': (3, 6),
            ',': (3, 7), '<': (3, 7),
            '.': (3, 8), '>': (3, 8),
            '/': (3, 9), '?': (3, 9),
        }

        
        pos1 = keyboard.get(character1.lower(), (-1, -1))
        pos2 = keyboard.get(character2.lower(), (-1, -1))
        
        if pos1 == (-1, -1) or pos2 == (-1, -1):
            return float('inf') # characters not found in keyboard
        
        return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5
    


