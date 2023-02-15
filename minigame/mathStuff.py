import math
def normalize_vector(vector):
    if vector == [0, 0]:
        return [0, 0]    
      
    pythagoras = math.sqrt(vector[0]*vector[0] + vector[1]*vector[1])
    return (vector[0] / pythagoras, vector[1] / pythagoras)
