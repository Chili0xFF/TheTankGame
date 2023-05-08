import arcade
import math
import random

WIDTH = 720  
HEIGHT = 480
METER = 16


SCALE_OF_BIMGIMAGES = HEIGHT/1080
SCALE_OF_SMALLIMAGES = SCALE_OF_BIMGIMAGES/3*6      #Rescaling graphics to match any resolution of screen
WALL_SIZE_IN_PIXELS = 48
TIME_LIMIT = 20 #In seconds

BOT_RED_MODE = True
BOT_BLUE_MODE = True
ALTERNATIVE_MAP = False

MAX_NUMBER_OF_BALLS = 3    
COOLDOWN_BETWEEN_BALLS = 60   #In frames. Sec * 60

ROTATION_SPEED = 3

RED_TANK_SPEED = 1
RED_BULLET_SPEED = 1
BLUE_TANK_SPEED = 1
BLUE_BULLET_SPEED = 1

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
        
        self.time_left_in_frames = TIME_LIMIT * 60
        self.scene = arcade.Scene()
        
        self.scene.add_sprite_list("BG")
        self.scene.add_sprite_list("Players")
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)
        self.scene.add_sprite_list("Cannons")
        self.scene.add_sprite_list("Red_Bullets")
        self.scene.add_sprite_list("Blue_Bullets")
        self.scene.add_sprite_list("END_SCREEN")
        
        #bg = arcade.Sprite("Assets/BG.png",SCALE_OF_BIMGIMAGES)
        #bg.center_x = WIDTH/2
        #bg.center_y = HEIGHT/2
        #self.scene.add_sprite("BG",bg)
        
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
        
    def on_draw(self):
        self.clear()
        self.scene.draw()
        #self.sprite1.draw()
        
    def on_update(self,delta_time):
        #print(arcade.get_fps())
        
        #print(round(self.time_left_in_frames/60,2))
        #If timeout, closest to middle win
        if self.time_left_in_frames<=0:
            red_distance = distance(self.red_tank.center_x,self.red_tank.center_y,WIDTH/2,HEIGHT/2)
            blue_distance = distance(self.blue_tank.center_x,self.blue_tank.center_y,WIDTH/2,HEIGHT/2)
            if red_distance == blue_distance:
                self.end_screen("Assets/DRAW.png",SCALE_OF_BIMGIMAGES)
            else:
                self.end_screen("Assets/RED_WON.png",SCALE_OF_BIMGIMAGES) if red_distance < blue_distance else self.end_screen("Assets/BLUE_WON.png",SCALE_OF_BIMGIMAGES)
            
        
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
                red_tf=False
                red_tb=False
                red_tl=False
                red_tr=False
                red_cl=False
                red_cr=False
                red_s=False
                if "forward" in response:
                    red_tf = True
                if "backward" in response:
                    red_tb = True
                if "tank_rot_left" in response:
                    red_tl = True
                if "tank_rot_right" in response:
                    red_tr = True
                if "cannon_rot_left" in response:
                    red_cl = True
                if "cannon_rot_right" in response:
                    red_cr = True
                if "shoot" in response:
                    red_s = True
                self.red_tank_gameplay(
                red_tf,
                red_tb,
                red_tl,
                red_tr,
                red_cl,
                red_cr,
                red_s
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
                blue_tf=False
                blue_tb=False
                blue_tl=False
                blue_tr=False
                blue_cl=False
                blue_cr=False
                blue_s=False
                if "forward" in response:
                    blue_tf = True
                if "backward" in response:
                    blue_tb = True
                if "tank_rot_left" in response:
                    blue_tl = True
                if "tank_rot_right" in response:
                    blue_tr = True
                if "cannon_rot_left" in response:
                    blue_cl = True
                if "cannon_rot_right" in response:
                    blue_cr = True
                if "shoot" in response:
                    blue_s = True
                self.blue_tank_gameplay(
                blue_tf,
                blue_tb,
                blue_tl,
                blue_tr,
                blue_cl,
                blue_cr,
                blue_s
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
            
            #Checking if anyone won
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
        #Blue Tank Movement 
        if forward:
            self.blue_tank.strafe(BLUE_TANK_SPEED)
        if backward:
            self.blue_tank.strafe(-BLUE_TANK_SPEED)
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
        #Red Tank Movement
        if forward:
            self.red_tank.strafe(RED_TANK_SPEED)
        if backward:
            self.red_tank.strafe(-RED_TANK_SPEED)
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
def red_bot_algorithm(myTank,enemyTank,,myBulletList,enemyBulletList,frames_left):
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

GameWindow(WIDTH,HEIGHT,"THE TANK GAME by Chili0xFF", arcade.color.CADET_GREY)
arcade.enable_timings()

arcade.run()

#Game made by Chili0xFF. No rights reserved. For educational purposes only
#Please consider buying me coffee if you see me in the hallway: Grey hair, always tired. 
#Thanks