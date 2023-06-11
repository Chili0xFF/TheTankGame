#Here, paste all of the functions of different tanks. Please make sure that only valid functions are present. If you need to paste functions here that are not playable, please see the 482 line in the main script
#For a script to be valid, it need to receive 3 variables (Information about ally tank, enemy tank, and current time) and return a list of commands for the tank to perform in current frame

def s23049(Me,Enemy,frames_left):
    response = ["forward","tank_right","cannon_left","shoot"]
    return response

def s27695(Me,Enemy,frames_left):
    response = ["tank_right","cannon_left","shoot"]
    return response
    
def s00001(Me,Enemy,frames_left):
    response = ["cannon_left","tank_left","shoot"]
    return response
def s00002(Me,Enemy,frames_left):
    response = ["tank_right","cannon_left"]
    return response

def s00003(Me,Enemy,frames_left):
    response = ["shoot"]
    return response