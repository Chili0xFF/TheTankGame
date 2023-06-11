import arcade
import math
import random
import time

BOT_RED_MODE = True
BOT_BLUE_MODE = False

ALTERNATIVE_MAP = False

TIME_LIMIT = 20 #In seconds
TIME_SPEEDUP = 10 #If timeleft < TIME_SPEEDUP: Speed of the closest tank to the middle goes up
MAX_NUMBER_OF_BALLS = 3    
COOLDOWN_BETWEEN_BALLS = 60   #In frames. Sec * 60

CONSOLE_DUMP = True
PRINT_NAMES_IN_CONSOLE = True #Only usable if CONSOLE_DUMP == True
#FILE_DUMP = False
#PRINT_NAMES_IN_FILE = False #Only usable if FILE_DUMP == True
#NEW_FILE = False            #Only usable if FILE_DUMP == True

WIDTH = 720  
HEIGHT = 480
METER = 16

SCALE_OF_BIMGIMAGES = HEIGHT/1080
SCALE_OF_SMALLIMAGES = SCALE_OF_BIMGIMAGES/3*6      #Rescaling graphics to match any resolution of screen
WALL_SIZE_IN_PIXELS = 48


ROTATION_SPEED = 3

RED_TANK_SPEED = 1
RED_BULLET_SPEED = 1
BLUE_TANK_SPEED = 1
BLUE_BULLET_SPEED = 1
SPEED_MULTIPLIER = 5
#For calculating distace between two points
def distance(x1 , y1 , x2 , y2):
    return math.sqrt(math.pow(x2 - x1, 2) +
                math.pow(y2 - y1, 2) * 1.0)

class GameWindow(arcade.Window):
    def __init__(self,width,height,title,color):
        super().__init__(width,height,title)
        arcade.set_background_color(color)
        
        self.scene = None
        self.blue_tank = None
        self.red_tank = None
        
        self.setup()

    def setup(self):
        
        self.BLUE_WON = False
        self.RED_WON = False
        
        self.WhoIsWinning = "None";
        
        self.time_left_in_frames = TIME_LIMIT * 60
        self.scene = arcade.Scene()
        
        self.scene.add_sprite_list("BG")
        self.scene.add_sprite_list("Players")
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)
        self.scene.add_sprite_list("Cannons")
        self.scene.add_sprite_list("Red_Bullets")
        self.scene.add_sprite_list("Blue_Bullets")
        self.scene.add_sprite_list("END_SCREEN")
        
        self.BackGround = arcade.Sprite("Assets/BG.png",SCALE_OF_BIMGIMAGES)
        
        #randomising on which side the player will start
        side = random.randint(0,1)
        
        self.blue_tank = arcade.Sprite("Assets/Tank_Blue.png", SCALE_OF_SMALLIMAGES)
        self.blue_tank.center_x = (WIDTH/4) if side == 0 else (WIDTH/4)*(3*side)
        self.blue_tank.center_y = (HEIGHT/4)*random.randint(1,3)
        self.scene.add_sprite("Players", self.blue_tank)
        #depending on what rolled in the beginning, here we flop it to the other side, so that we have 1 player on each side
        side+=1
        side%=2
        self.blue_cannon = arcade.Sprite("Assets/Blue_Cannon.png", SCALE_OF_SMALLIMAGES)
        self.blue_cannon.center_x = self.blue_tank.center_x
        self.blue_cannon.center_y = self.blue_tank.center_y+5
        self.scene.add_sprite("Cannons", self.blue_cannon)
        
        self.red_tank = arcade.Sprite("Assets/Tank_Red.png", SCALE_OF_SMALLIMAGES)
        self.red_tank.center_x = (WIDTH/4) if side == 0 else (WIDTH/4)*(3*side)
        self.red_tank.center_y = (HEIGHT/4)*random.randint(1,3)
        self.scene.add_sprite("Players", self.red_tank)
        
        self.red_cannon = arcade.Sprite("Assets/Red_Cannon.png", SCALE_OF_SMALLIMAGES)
        
        self.red_cannon.center_x = self.red_tank.center_x
        self.red_cannon.center_y = self.red_tank.center_y+5
        self.scene.add_sprite("Cannons", self.red_cannon)
        
        #Top&Bottom wall
        
        for x in range(0, WIDTH, WALL_SIZE_IN_PIXELS):
            wall = arcade.Sprite("Assets/Wall.png")
            wall.center_x = x+(WALL_SIZE_IN_PIXELS/2)
            wall.center_y = (WALL_SIZE_IN_PIXELS/2)
            self.scene.add_sprite("Walls", wall)
            wall2 = arcade.Sprite("Assets/Wall.png")
            wall2.center_x = x+(WALL_SIZE_IN_PIXELS/2)
            wall2.center_y = HEIGHT-(WALL_SIZE_IN_PIXELS/2)
            self.scene.add_sprite("Walls", wall2)
        for y in range(WALL_SIZE_IN_PIXELS,HEIGHT, WALL_SIZE_IN_PIXELS):
            wall = arcade.Sprite("Assets/Wall.png")
            wall.center_x = (WALL_SIZE_IN_PIXELS/2)
            wall.center_y = y+(WALL_SIZE_IN_PIXELS/2)
            self.scene.add_sprite("Walls",wall)
            wall2 = arcade.Sprite("Assets/Wall.png")
            wall2.center_x = WIDTH-(WALL_SIZE_IN_PIXELS/2)
            wall2.center_y = y+(WALL_SIZE_IN_PIXELS/2)
            self.scene.add_sprite("Walls",wall2)
        #Alternative map
        if ALTERNATIVE_MAP:
            print("TBA")
        
        #Initialising physics engines for both players
        self.physics_engine_red = arcade.PhysicsEnginePlatformer(
            self.red_tank, gravity_constant = 0.0, walls=self.scene["Walls"]
        )
        self.physics_engine_blue = arcade.PhysicsEnginePlatformer(
            self.blue_tank, gravity_constant = 0.0, walls=self.scene["Walls"]
        )
        
        #Initialising all the button variables
        self.red_button_up = False
        self.red_button_down = False
        self.red_button_left = False
        self.red_button_right = False
        self.red_cannon_rotate_right = False
        self.red_cannon_rotate_left = False
        self.red_cannon_shoot = False
        self.red_cannon_rotation = 0
        self.red_ball_cooldown = 0
        self.red_ball_counter = 0
        
        self.blue_button_up = False
        self.blue_button_down = False
        self.blue_button_left = False
        self.blue_button_right = False
        self.blue_cannon_rotate_right = False
        self.blue_cannon_rotate_left = False
        self.blue_cannon_shoot = False
        self.blue_cannon_rotation = 0
        self.blue_ball_cooldown = 0
        self.blue_ball_counter = 0
        
        if CONSOLE_DUMP and PRINT_NAMES_IN_CONSOLE:
            print("red_x,red_y,red_rotation,red_cannonRotation,red_velocityX,red_velocityY,red_shootCooldown,red_turnLeft,red_turnRight,red_goForward,red_goBack,red_shoot,red_cannonLeft,red_cannonRight,red_bullet3_x,red_bullet3_y,red_bullet3_velocityX,red_bullet3_velocityY,red_bullet2_x,red_bullet2_y,red_bullet2_velocityX,red_bullet2_velocityY,red_bullet1_x,red_bullet1_y,red_bullet1_velocityX,red_bullet1_velocityY,blue_x,blue_y,blue_rotation,blue_cannonRotation,blue_velocityX,blue_velocityY,blue_shootCooldown,blue_turnLeft,blue_turnRight,blue_goForward,blue_goBack,blue_shoot,blue_cannonLeft,blue_cannonRight,blue_bullet3_x,blue_bullet3_y,blue_bullet3_velocityX,blue_bullet3_velocityY,blue_bullet2_x,blue_bullet2_y,blue_bullet2_velocityX,blue_bullet2_velocityY,blue_bullet1_x,blue_bullet1_y,blue_bullet1_velocityX,blue_bullet1_velocityY")
        
    def on_draw(self):
        self.clear()
        self.scene.draw()
        #self.sprite1.draw()
        
    def on_update(self,delta_time):
        #print(arcade.get_fps())
        #print(self.time_left_in_frames/60)
        #Log dumping
        if CONSOLE_DUMP or FILE_DUMP:
            #print(self.blue_tank.angle)
            log_dump(
            self.red_tank,self.red_cannon,self.scene["Red_Bullets"],self.red_ball_counter,self.red_button_up,self.red_button_down,self.red_button_left,self.red_button_right,self.red_cannon_rotate_left,self.red_cannon_rotate_right,self.red_cannon_shoot,self.red_cannon_rotation,self.red_ball_cooldown,self.blue_tank,self.blue_cannon,self.scene["Blue_Bullets"],self.blue_ball_counter,self.blue_button_up,self.blue_button_down,self.blue_button_left,self.blue_button_right,self.blue_cannon_rotate_left,self.blue_cannon_rotate_right,self.blue_cannon_shoot,self.blue_cannon_rotation,self.blue_ball_cooldown,self.time_left_in_frames)
        #If anyone won, don't play
        if not self.RED_WON and not self.BLUE_WON and self.time_left_in_frames>0:
            self.time_left_in_frames-=1
            self.physics_engine_red.update()
            self.physics_engine_blue.update()
            self.scene.update(["Blue_Bullets","Red_Bullets"])
        
            self.red_tank.stop()
            self.blue_tank.stop()
            
            if not BOT_RED_MODE:
                self.red_tank_gameplay(
                self.red_button_up,
                self.red_button_down,
                self.red_button_left,
                self.red_button_right,
                self.red_cannon_rotate_left,
                self.red_cannon_rotate_right,
                self.red_cannon_shoot
                )
            else:
                response = red_bot_algorithm(self.red_tank,self.blue_tank,list(self.scene["Red_Bullets"]),list(self.scene["Blue_Bullets"]),self.time_left_in_frames)
                self.red_button_up=False
                self.red_button_down=False
                self.red_button_left=False
                self.red_button_right=False
                self.red_cannon_rotate_left=False
                self.red_cannon_rotate_right=False
                self.red_cannon_shoot=False
                if "forward" in response:
                    self.red_button_up = True
                if "backward" in response:
                    self.red_button_down = True
                if "tank_rot_left" in response:
                    self.red_button_left = True
                if "tank_rot_right" in response:
                    self.red_button_right = True
                if "cannon_rot_left" in response:
                    self.red_cannon_rotate_left = True
                if "cannon_rot_right" in response:
                    self.red_cannon_rotate_right = True
                if "shoot" in response:
                    self.red_cannon_shoot = True
                self.red_tank_gameplay(
                self.red_button_up,
                self.red_button_down,
                self.red_button_left,
                self.red_button_right,
                self.red_cannon_rotate_left,
                self.red_cannon_rotate_right,
                self.red_cannon_shoot
                )
            if not BOT_BLUE_MODE:
                self.blue_tank_gameplay(
                self.blue_button_up,
                self.blue_button_down,
                self.blue_button_left,
                self.blue_button_right,
                self.blue_cannon_rotate_left,
                self.blue_cannon_rotate_right,
                self.blue_cannon_shoot
                )
            else:
                response = blue_bot_algorithm(self.blue_tank,self.red_tank,self.time_left_in_frames)
                self.blue_button_up=False
                self.blue_button_down=False
                self.blue_button_left=False
                self.blue_button_right=False
                self.blue_cannon_rotate_left=False
                self.blue_cannon_rotate_right=False
                self.blue_cannon_shoot=False
                if "forward" in response:
                    self.blue_button_up = True
                if "backward" in response:
                    self.blue_button_down = True
                if "tank_rot_left" in response:
                    self.blue_button_left = True
                if "tank_rot_right" in response:
                    self.blue_button_right = True
                if "cannon_rot_left" in response:
                    self.blue_cannon_rotate_left = True
                if "cannon_rot_right" in response:
                    self.blue_cannon_rotate_right = True
                if "shoot" in response:
                    self.blue_cannon_shoot = True
                self.blue_tank_gameplay(
                self.blue_button_up,
                self.blue_button_down,
                self.blue_button_left,
                self.blue_button_right,
                self.blue_cannon_rotate_left,
                self.blue_cannon_rotate_right,
                self.blue_cannon_shoot
                ) 
            
            #Positioning cannons on tanks
            #RedCannon
            self.red_cannon.center_x = self.red_tank.center_x
            self.red_cannon.center_y = self.red_tank.center_y+5
            #BlueCannon
            self.blue_cannon.center_x = self.blue_tank.center_x
            self.blue_cannon.center_y = self.blue_tank.center_y+5
            
            #Checking for all types of collisions
            #Bullets with Walls
            for bullet in self.scene["Red_Bullets"]:
                wall_hit_list = arcade.check_for_collision_with_list(bullet,self.scene["Walls"])
                if wall_hit_list:
                    bullet.remove_from_sprite_lists()
                    self.red_ball_counter-=1
            for bullet in self.scene["Blue_Bullets"]:
                wall_hit_list = arcade.check_for_collision_with_list(bullet,self.scene["Walls"])
                if wall_hit_list:
                    bullet.remove_from_sprite_lists()
                    self.blue_ball_counter-=1
            #Tanks with bullets
            red_tank_got_hit = arcade.check_for_collision_with_list(self.red_tank,self.scene["Blue_Bullets"])
            blue_tank_got_hit = arcade.check_for_collision_with_list(self.blue_tank,self.scene["Red_Bullets"])
            
            #Tanks with tanks WIP
            #Tu kiedyś będzie kod który powoduje remis, jak pan bóg pozwoli
            
            #Checking if anyone hit anyone
            if blue_tank_got_hit and red_tank_got_hit:
                self.RED_WON=True
                self.BLUE_WON=True
                self.end_screen("Assets/DRAW.png",SCALE_OF_BIMGIMAGES)
            elif blue_tank_got_hit:
                self.RED_WON = True
                self.end_screen("Assets/RED_WON.png",SCALE_OF_BIMGIMAGES)
            elif red_tank_got_hit:
                self.BLUE_WON = True
                self.end_screen("Assets/BLUE_WON.png",SCALE_OF_BIMGIMAGES)
            if self.time_left_in_frames/60<TIME_SPEEDUP:
                red_distance = distance(self.red_tank.center_x,self.red_tank.center_y,WIDTH/2,HEIGHT/2)
                blue_distance = distance(self.blue_tank.center_x,self.blue_tank.center_y,WIDTH/2,HEIGHT/2)
                #If timeout, closest to middle win
                if self.time_left_in_frames<=0:
                    if red_distance == blue_distance:
                        self.end_screen("Assets/DRAW.png",SCALE_OF_BIMGIMAGES)
                    elif red_distance < blue_distance:
                        self.end_screen("Assets/RED_WON.png",SCALE_OF_BIMGIMAGES)
                        self.RED_WON = True
                    else: 
                        self.end_screen("Assets/BLUE_WON.png",SCALE_OF_BIMGIMAGES)
                        self.BLUE_WON = True
                #This means we are in SPEEDUP limit
                else:
                    if red_distance == blue_distance:
                        self.WhoIsWinning = "None"
                    elif red_distance > blue_distance:
                        self.WhoIsWinning = "Blue"
                    else:
                        self.WhoIsWinning = "Red"
        
    def on_key_press(self,symbol,modifiers):
        #Red Tank Controls
        if symbol == arcade.key.UP:
            self.red_button_up = True
        if symbol == arcade.key.DOWN:
            self.red_button_down = True
        if symbol == arcade.key.LEFT:
            self.red_button_left = True
        if symbol == arcade.key.RIGHT:
            self.red_button_right = True
        #Red Cannon Controls
        if symbol == arcade.key.PERIOD:
            self.red_cannon_rotate_left = True
        if symbol == arcade.key.SLASH:
            self.red_cannon_rotate_right = True
        if symbol == arcade.key.RSHIFT:
            self.red_cannon_shoot = True
        
        #Blue Tank Controls
        if symbol == arcade.key.W:
            self.blue_button_up = True
        if symbol == arcade.key.S:
            self.blue_button_down = True
        if symbol == arcade.key.A:
            self.blue_button_left = True
        if symbol == arcade.key.D:
            self.blue_button_right = True
        #Blue Cannon Controls
        if symbol == arcade.key.C:
            self.blue_cannon_rotate_left = True
        if symbol == arcade.key.V:
            self.blue_cannon_rotate_right = True
        if symbol == arcade.key.SPACE:
            self.blue_cannon_shoot = True
            
        #Utilities
        if symbol == arcade.key.R:
            BLUE_WON = False
            RED_WON = False
            self.setup()
    def on_key_release(self,symbol,modifiers):
        #Red Tank Controls
        if symbol == arcade.key.UP:
            self.red_button_up = False
        if symbol == arcade.key.DOWN:
            self.red_button_down = False
        if symbol == arcade.key.LEFT:
            self.red_button_left = False
        if symbol == arcade.key.RIGHT:
            self.red_button_right = False
        #Red Cannon Controls
        if symbol == arcade.key.PERIOD:
            self.red_cannon_rotate_left = False
        if symbol == arcade.key.SLASH:
            self.red_cannon_rotate_right = False
        if symbol == arcade.key.RSHIFT:
            self.red_cannon_shoot = False
            
        #Blue Tank Controls
        if symbol == arcade.key.W:
            self.blue_button_up = False
        if symbol == arcade.key.S:
            self.blue_button_down = False
        if symbol == arcade.key.A:
            self.blue_button_left = False
        if symbol == arcade.key.D:
            self.blue_button_right = False
        #Blue Cannon Controls
        if symbol == arcade.key.C:
            self.blue_cannon_rotate_left = False
        if symbol == arcade.key.V:
            self.blue_cannon_rotate_right = False
        if symbol == arcade.key.SPACE:
            self.blue_cannon_shoot = False
    def shooting(self,x,y,rotation,sprite_list):
        bullet = arcade.Sprite("Assets/Bullet.png", SCALE_OF_SMALLIMAGES)
        bullet.center_x = x
        bullet.center_y = y
        bullet.turn_left(rotation)
        bullet.strafe(1)
        self.scene.add_sprite(sprite_list,bullet)
        return bullet
    def end_screen(self,image,size):
        END = arcade.Sprite(image,size)
        END.center_x = WIDTH/2
        END.center_y = HEIGHT/2
        self.scene.add_sprite("END_SCREEN", END)
    def blue_tank_gameplay(self,forward=False,backward=False,tank_rot_left=False,tank_rot_right=False,cannon_rot_left=False,cannon_rot_right=False,shoot=False):
        #Utilities
        if self.WhoIsWinning != "Blue":
            current_speed = BLUE_TANK_SPEED
        else:
            current_speed = BLUE_TANK_SPEED * SPEED_MULTIPLIER
        #Blue Tank Movement 
        if forward:
            self.blue_tank.strafe(current_speed)
        if backward:
            self.blue_tank.strafe(-current_speed)
        if tank_rot_left:
            self.blue_tank.turn_left(ROTATION_SPEED)
        if tank_rot_right:
            self.blue_tank.turn_right(ROTATION_SPEED)
        #Blue Cannon Movement
        if cannon_rot_left:
            self.blue_cannon_rotation+=ROTATION_SPEED
            self.blue_cannon.turn_left(ROTATION_SPEED)
        if cannon_rot_right:
            self.blue_cannon.turn_right(ROTATION_SPEED)
            self.blue_cannon_rotation-=ROTATION_SPEED
        #Blue Cannon Shooting
        if self.blue_ball_cooldown == 0:
            if self.blue_ball_counter < MAX_NUMBER_OF_BALLS:
                if shoot:
                    self.shooting(self.blue_cannon.center_x,self.blue_cannon.center_y,self.blue_cannon_rotation,"Blue_Bullets")
                    self.blue_ball_counter+=1
                    self.blue_ball_cooldown=COOLDOWN_BETWEEN_BALLS
        else:
            self.blue_ball_cooldown -= 1
            
    def red_tank_gameplay(self,forward=False,backward=False,tank_rot_left=False,tank_rot_right=False,cannon_rot_left=False,cannon_rot_right=False,shoot=False):
        #Utilities
        if self.WhoIsWinning != "Red":
            current_speed = RED_TANK_SPEED
        else:
            current_speed = RED_TANK_SPEED * SPEED_MULTIPLIER
        #Red Tank Movement
        if forward:
            self.red_tank.strafe(current_speed)
        if backward:
            self.red_tank.strafe(-current_speed)
        if tank_rot_left:
            self.red_tank.turn_left(ROTATION_SPEED)
        if tank_rot_right:
            self.red_tank.turn_right(ROTATION_SPEED)
        #Red Cannon Movement
        if cannon_rot_left:
            self.red_cannon_rotation+=ROTATION_SPEED
            self.red_cannon.turn_left(ROTATION_SPEED)
        if cannon_rot_right:
            self.red_cannon_rotation-=ROTATION_SPEED
            self.red_cannon.turn_right(ROTATION_SPEED)
        #Red Cannon Shooting
        if self.red_ball_cooldown == 0:
            if self.red_ball_counter < MAX_NUMBER_OF_BALLS:
                if shoot:
                    self.shooting(self.red_cannon.center_x,self.red_cannon.center_y,self.red_cannon_rotation,"Red_Bullets")
                    self.red_ball_counter+=1
                    self.red_ball_cooldown=COOLDOWN_BETWEEN_BALLS
        else:
            self.red_ball_cooldown-=1  
def red_bot_algorithm(myTank,enemyTank,myBulletList,enemyBulletList,frames_left):
        #Here paste algorithm for red tank  #The system is simple. If you want your tank to do specific aciton in current frame, add keyword to the "response" list by using response.append("KEYWORD")
        
        #Keywords in response:
        #forward -> Moves tank ahead
        #backward -> Moves tank back
        #tank_rot_left -> Rotates tank to the left
        #tank_rot_right -> Rotates tank to the rights
        #cannon_rot_left -> Rotates cannon to the left
        #cannon_rot_right -> Rotates cannon to the rights
        #shoot -> Shoots, if amount of bullets is less than max and not on cooldown
        
        #Additional parameters:
        #myTank -> myTank arcade.Sprite object
        #enemyTank -> myTank arcade.Sprite object
        #myBulletList -> list of my bullets, in form of arcade.Sprite objects
        #enemyBulletList -> list of enemy bullets, in form of arcade.Sprite objects
        
        #For specific parameters of arcade.Sprite objects, please see https://api.arcade.academy/en/stable/api/sprites.html#arcade-sprite. There is plenty of different parameters, way too many for me to describe all of them here
        
        #frames_left -> time in frames before end of game. To get seconds, dividing this by 60
        response = ["forward","tank_rot_right","cannon_rot_left","shoot"]
        return response
def blue_bot_algorithm(myTank,enemyTank,frames_left):
        #Here paste algorithm for red tank  #The system is simple. If you want your tank to do specific aciton in current frame, add keyword to the "response" list by using response.append("KEYWORD")
        
        #Keywords in response:
        #forward -> Moves tank ahead
        #backward -> Moves tank back
        #tank_rot_left -> Rotates tank to the left
        #tank_rot_right -> Rotates tank to the rights
        #cannon_rot_left -> Rotates cannon to the left
        #cannon_rot_right -> Rotates cannon to the rights
        #shoot -> Shoots, if amount of bullets is less than max and not on cooldown
        
        #Additional parameters:
        #myTank -> myTank arcade.Sprite object
        #enemyTank -> myTank arcade.Sprite object
        #myBulletList -> list of my bullets, in form of arcade.Sprite objects
        #enemyBulletList -> list of enemy bullets, in form of arcade.Sprite objects
        
        #For specific parameters of arcade.Sprite objects, please see https://api.arcade.academy/en/stable/api/sprites.html#arcade-sprite. There is plenty of different parameters, way too many for me to describe all of them here
        
        #frames_left -> time in frames before end of game. To get seconds, dividing this by 60
        response = ["forward","tank_rot_left","cannon_rot_right","shoot"]
        return response
def log_dump(red_tank,red_cannon,red_bullets,red_bullets_counter,red_forward,red_back,red_t_left,red_t_right,red_c_left,red_c_right,red_isShooting,red_cannon_rotation,red_ball_cooldown,blue_tank,blue_cannon,blue_bullets,blue_bullets_counter,blue_forward,blue_back,blue_t_left,blue_t_right,blue_c_left,blue_c_right,blue_isShooting,blue_cannon_rotation,blue_ball_cooldown,frames_left):
    #List of data
    red_x =                 red_tank.center_x
    red_y =                 red_tank.center_y
    red_rotation =          red_tank.angle%360
    red_cannonRotation =    red_cannon.angle%360
    red_velocityX =         red_tank.change_x
    red_velocityY =         red_tank.change_y
    red_shootCooldown =     red_ball_cooldown
    
    red_turnLeft =          red_t_left
    red_turnRight =         red_t_right
    red_goForward =         red_forward
    red_goBack =            red_back
    red_shoot =             red_isShooting
    red_cannonLeft =        red_c_left
    red_cannonRight =       red_c_right
    
    if  red_bullets_counter == 3:
        red_bullet3_x =         red_bullets[2].center_x
        red_bullet3_y =         red_bullets[2].center_y
        red_bullet3_velocityX = red_bullets[2].change_x
        red_bullet3_velocityY = red_bullets[2].change_y
    else:
        red_bullet3_x =         0
        red_bullet3_y =         0
        red_bullet3_velocityX = 0
        red_bullet3_velocityY = 0
    if  red_bullets_counter > 1:
        red_bullet2_x =         red_bullets[1].center_x
        red_bullet2_y =         red_bullets[1].center_y
        red_bullet2_velocityX = red_bullets[1].change_x
        red_bullet2_velocityY = red_bullets[1].change_y
    else:
        red_bullet2_x =         0
        red_bullet2_y =         0
        red_bullet2_velocityX = 0
        red_bullet2_velocityY = 0
    if  red_bullets_counter > 0:
        red_bullet1_x =         red_bullets[0].center_x
        red_bullet1_y =         red_bullets[0].center_y
        red_bullet1_velocityX = red_bullets[0].change_x
        red_bullet1_velocityY = red_bullets[0].change_y
    else:
        red_bullet1_x =         0
        red_bullet1_y =         0
        red_bullet1_velocityX = 0
        red_bullet1_velocityY = 0
    
    red_data = (red_x,red_y,red_rotation,red_cannonRotation,red_velocityX,red_velocityY,red_shootCooldown,red_turnLeft,red_turnRight,red_goForward,red_goBack,red_shoot,red_cannonLeft,red_cannonRight,red_bullet3_x,red_bullet3_y,red_bullet3_velocityX,red_bullet3_velocityY,red_bullet2_x,red_bullet2_y,red_bullet2_velocityX,red_bullet2_velocityY,red_bullet1_x,red_bullet1_y,red_bullet1_velocityX,red_bullet1_velocityY)
    
    blue_x =                 blue_tank.center_x
    blue_y =                 blue_tank.center_y
    blue_rotation =          blue_tank.angle%360
    blue_cannonRotation =    blue_cannon.angle%360
    blue_velocityX =         blue_tank.change_x
    blue_velocityY =         blue_tank.change_y
    blue_shootCooldown =     blue_ball_cooldown

    blue_turnLeft =          blue_t_left
    blue_turnRight =         blue_t_right
    blue_goForward =         blue_forward
    blue_goBack =            blue_back
    blue_shoot =             blue_isShooting
    blue_cannonLeft =        blue_c_left
    blue_cannonRight =       blue_c_right
    
    if  blue_bullets_counter == 3:
        blue_bullet3_x =         blue_bullets[2].center_x
        blue_bullet3_y =         blue_bullets[2].center_y
        blue_bullet3_velocityX = blue_bullets[2].change_x
        blue_bullet3_velocityY = blue_bullets[2].change_y
    else:
        blue_bullet3_x =         0
        blue_bullet3_y =         0
        blue_bullet3_velocityX = 0
        blue_bullet3_velocityY = 0
    if  blue_bullets_counter > 1:
        blue_bullet2_x =         blue_bullets[1].center_x
        blue_bullet2_y =         blue_bullets[1].center_y
        blue_bullet2_velocityX = blue_bullets[1].change_x
        blue_bullet2_velocityY = blue_bullets[1].change_y
    else:
        blue_bullet2_x =         0
        blue_bullet2_y =         0
        blue_bullet2_velocityX = 0
        blue_bullet2_velocityY = 0
    if  blue_bullets_counter > 0:
        blue_bullet1_x =         blue_bullets[0].center_x
        blue_bullet1_y =         blue_bullets[0].center_y
        blue_bullet1_velocityX = blue_bullets[0].change_x
        blue_bullet1_velocityY = blue_bullets[0].change_y
    else:
        blue_bullet1_x =         0
        blue_bullet1_y =         0
        blue_bullet1_velocityX = 0
        blue_bullet1_velocityY = 0
    
    blue_data = (blue_x,blue_y,blue_rotation,blue_cannonRotation,blue_velocityX,blue_velocityY,blue_shootCooldown,blue_turnLeft,blue_turnRight,blue_goForward,blue_goBack,blue_shoot,blue_cannonLeft,blue_cannonRight,blue_bullet3_x,blue_bullet3_y,blue_bullet3_velocityX,blue_bullet3_velocityY,blue_bullet2_x,blue_bullet2_y,blue_bullet2_velocityX,blue_bullet2_velocityY,blue_bullet1_x,blue_bullet1_y,blue_bullet1_velocityX,blue_bullet1_velocityY,frames_left/60)
    
    #Actually writing stuff out
    if CONSOLE_DUMP:
        print(red_data+blue_data)
GameWindow(WIDTH,HEIGHT,"THE TANK GAME by Chili0xFF", arcade.color.CADET_GREY)
arcade.enable_timings()

arcade.run()

#Game made by Chili0xFF. No rights reserved. For educational purposes only
#Please consider buying me coffee if you see me in the hallway: Grey hair, always tired. 
#Thanks