import arcade
import math
import random
import time
import tournament_algorithms

WIN_WIDTH = 720  
WIN_HEIGHT = 480

RED_BOT_MODE = False
BLUE_BOT_MODE = False
TOURNAMENT_MODE = True
TOURNAMENT_AUTOSKIP = True

ALTERNATIVE_MAP = False

TIME_LIMIT = 20 #In seconds
TIME_SPEEDUP = 10 #If timeleft < TIME_SPEEDUP: Speed of bullets of the closest tank to the middle goes up

CONSOLE_DUMP = False
#PRINT_NAMES_IN_CONSOLE = True #Only usable if CONSOLE_DUMP == True

SCALE_OF_BIG_IMAGES = WIN_HEIGHT/1080
SCALE_OF_SMALL_IMAGES = SCALE_OF_BIG_IMAGES/3*6      #Rescaling graphics to match any resolution of screen
WALL_SIZE_IN_PIXELS = 48

INITIAL_TANK_SPEED = 1
INITIAL_BULLET_SPEED = 1
BOOSTED_BULLET_SPEED = 3
INITIAL_ROTATION_SPEED = 1
INITIAL_BULLET_COOLDOWN = 60       #In frames. Sec * 60
INITIAL_BULLET_MAX = 33

player1=None
player2=None

who_won=0

def distance(x1 , y1 , x2 , y2):
    #For calculating distace between two points, accessory function
    return math.sqrt(math.pow(x2 - x1, 2) +
                math.pow(y2 - y1, 2) * 1.0)
def dataGatherer(tank,cannon,bullet_list):
    #tank x/y, tank rotation, cannon rotation, tank velocity x/y, tank acceleration x/y, shoot cooldown, last 3 bullets (x/y, velocity x/y)
    #
    #
    data = dict()
    data["tank x"]=tank.center_x
    data["tank y"]=tank.center_y
    data["tank rotation"]=tank._angle
    data["tank velocity x"]=tank.velocity[0]
    data["tank velocity y"]=tank.velocity[1]
    data["cannon rotation"]=cannon._angle
    data["bullet cooldown"]=cannon.cooldown_left
    
    if len(bullet_list) > 0:
        data["bullet 1 x"]=bullet_list[0].center_x
        data["bullet 1 y"]=bullet_list[0].center_y
        data["bullet 1 velocity x"]=bullet_list[0].velocity[0]
        data["bullet 1 velocity y"]=bullet_list[0].velocity[1]
    if len(bullet_list) > 1:
        data["bullet 2 x"]=bullet_list[1].center_x
        data["bullet 2 y"]=bullet_list[1].center_y
        data["bullet 2 velocity x"]=bullet_list[1].velocity[0]
        data["bullet 2 velocity y"]=bullet_list[1].velocity[1]
    if len(bullet_list) > 2:
        data["bullet 3 x"]=bullet_list[2].center_x
        data["bullet 3 y"]=bullet_list[2].center_y
        data["bullet 3 velocity x"]=bullet_list[2].velocity[0]
        data["bullet 3 velocity y"]=bullet_list[2].velocity[1]
    return data
class GameWindow(arcade.Window):
    def __init__(self,width,height,title,color):
        super().__init__(width,height,title)
        arcade.set_background_color(color)
        
        #In order to start new game, we clear the entire scene and all the variables
        self.scene = None
        self.blue_tank = None
        self.red_tank = None
        
        self.setup()
    def setup(self):
            #Setting up scene and sprite lists
        self.scene = arcade.Scene()
        
        
        
        self.scene.add_sprite_list("Background")
        self.scene.add_sprite_list("Players")
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)
        self.scene.add_sprite_list("Cannons")
        self.scene.add_sprite_list("Red_Bullets")
        self.scene.add_sprite_list("Blue_Bullets")
        
        self.scene.add_sprite_list("End_screen")
        
        self.time_left = TIME_LIMIT*60
            #Spawning Blue Tank
        side = random.randint(0,1)
        
        self.blue_tank = arcade.Sprite("Assets/Tank_Blue.png", SCALE_OF_SMALL_IMAGES)
        self.blue_tank.center_x = (WIN_WIDTH/4) if side == 0 else (WIN_WIDTH/4)*(3*side)
        self.blue_tank.center_y = (WIN_HEIGHT/4)*random.randint(1,3)
        self.scene.add_sprite("Players", self.blue_tank)
        
        self.blue_cannon = arcade.Sprite("Assets/Blue_Cannon.png", SCALE_OF_SMALL_IMAGES)
        self.blue_cannon.center_x = self.blue_tank.center_x
        self.blue_cannon.center_y = self.blue_tank.center_y+5
        self.scene.add_sprite("Cannons", self.blue_cannon)
            #Setting up Blue variables
        self.blue_tank.button_forward = False
        self.blue_tank.button_backward = False
        self.blue_tank.button_left = False
        self.blue_tank.button_right = False
        self.blue_cannon.button_left = False
        self.blue_cannon.button_right = False
        self.blue_cannon.button_shoot = False
        
        self.blue_tank.mov_speed = INITIAL_TANK_SPEED
        self.blue_tank.rot_speed = INITIAL_ROTATION_SPEED
        self.blue_tank.spd_mod = 1
        self.blue_cannon.rot_speed = INITIAL_ROTATION_SPEED
        self.blue_cannon.cooldown_max = INITIAL_BULLET_COOLDOWN
        self.blue_cannon.cooldown_left = 0
        self.blue_cannon.bullets_max = INITIAL_BULLET_MAX
        self.blue_cannon.bullets_now = 0
        self.blue_cannon.bul_speed = INITIAL_BULLET_SPEED
        
            #Spawning Red Tank on the other side
        side+=1
        side%=2
        
        self.red_tank = arcade.Sprite("Assets/Tank_Red.png", SCALE_OF_SMALL_IMAGES)
        self.red_tank.center_x = (WIN_WIDTH/4) if side == 0 else (WIN_WIDTH/4)*(3*side)
        self.red_tank.center_y = (WIN_HEIGHT/4)*random.randint(1,3)
        self.scene.add_sprite("Players", self.red_tank)
        
        self.red_cannon = arcade.Sprite("Assets/Red_Cannon.png", SCALE_OF_SMALL_IMAGES)
        self.red_cannon.center_x = self.red_tank.center_x
        self.red_cannon.center_y = self.red_tank.center_y+5
        self.scene.add_sprite("Cannons", self.red_cannon)
            #Setting up Red variables
        self.red_tank.button_forward = False
        self.red_tank.button_backward = False
        self.red_tank.button_left = False
        self.red_tank.button_right = False
        self.red_cannon.button_left = False
        self.red_cannon.button_right = False
        self.red_cannon.button_shoot = False
        
        self.red_tank.mov_speed = INITIAL_TANK_SPEED
        self.red_tank.rot_speed = INITIAL_ROTATION_SPEED
        self.red_tank.spd_mod = 1
        self.red_cannon.rot_speed = INITIAL_ROTATION_SPEED
        self.red_cannon.cooldown_max = INITIAL_BULLET_COOLDOWN
        self.red_cannon.cooldown_left = 0
        self.red_cannon.bullets_max = INITIAL_BULLET_MAX
        self.red_cannon.bullets_now = 0
        self.red_cannon.bul_speed = INITIAL_BULLET_SPEED
        
        #Top&Bottom wall
        
        for x in range(0, WIN_WIDTH, WALL_SIZE_IN_PIXELS):
            wall = arcade.Sprite("Assets/Wall.png")
            wall.center_x = x+(WALL_SIZE_IN_PIXELS/2)
            wall.center_y = (WALL_SIZE_IN_PIXELS/2)
            self.scene.add_sprite("Walls", wall)
            wall2 = arcade.Sprite("Assets/Wall.png")
            wall2.center_x = x+(WALL_SIZE_IN_PIXELS/2)
            wall2.center_y = WIN_HEIGHT-(WALL_SIZE_IN_PIXELS/2)
            self.scene.add_sprite("Walls", wall2)
        for y in range(WALL_SIZE_IN_PIXELS,WIN_HEIGHT, WALL_SIZE_IN_PIXELS):
            wall = arcade.Sprite("Assets/Wall.png")
            wall.center_x = (WALL_SIZE_IN_PIXELS/2)
            wall.center_y = y+(WALL_SIZE_IN_PIXELS/2)
            self.scene.add_sprite("Walls",wall)
            wall2 = arcade.Sprite("Assets/Wall.png")
            wall2.center_x = WIN_WIDTH-(WALL_SIZE_IN_PIXELS/2)
            wall2.center_y = y+(WALL_SIZE_IN_PIXELS/2)
            self.scene.add_sprite("Walls",wall2)
            
        #Initialising physics engines for both players
        self.physics_engine_red = arcade.PhysicsEnginePlatformer(
            self.red_tank, gravity_constant = 0.0, walls=self.scene["Walls"]
        )
        self.physics_engine_blue = arcade.PhysicsEnginePlatformer(
            self.blue_tank, gravity_constant = 0.0, walls=self.scene["Walls"]
        )
        
        #Other variables
        self.playing = True
    def on_draw(self):
        self.clear()
        if TOURNAMENT_MODE:
            arcade.draw_text(str(player1[0].__name__),
                         -150,
                         WIN_HEIGHT-(WALL_SIZE_IN_PIXELS*2),
                         arcade.color.BLUE,
                         20 * 2,
                         width=WIN_WIDTH,
                         align="center")
            arcade.draw_text("vs",
                         0,
                         WIN_HEIGHT-(WALL_SIZE_IN_PIXELS*2),
                         arcade.color.BLACK,
                         20 * 2,
                         width=WIN_WIDTH,
                         align="center")
            arcade.draw_text(str(player2[0].__name__),
                         150,
                         WIN_HEIGHT-(WALL_SIZE_IN_PIXELS*2),
                         arcade.color.RED,
                         20 * 2,
                         width=WIN_WIDTH,
                         align="center")
        self.scene.draw()
        
    def on_update(self,delta_time):
        if self.playing:
            global who_won
            #Updating all the engines to move the sprites around
            self.physics_engine_red.update()
            self.physics_engine_blue.update()
            self.scene.update(["Blue_Bullets","Red_Bullets"])
            
            #Positioning cannons on tanks
                #BlueCannon
            self.blue_cannon.center_x = self.blue_tank.center_x
            self.blue_cannon.center_y = self.blue_tank.center_y
                #RedCannon
            self.red_cannon.center_x = self.red_tank.center_x
            self.red_cannon.center_y = self.red_tank.center_y
            
            #Gathering Data
            Blue_data = dataGatherer(self.blue_tank,self.blue_cannon,list(self.scene["Blue_Bullets"]))
            Red_data = dataGatherer(self.red_tank,self.red_cannon,list(self.scene["Red_Bullets"]))
            
            #Stoping tanks from moving
            self.red_tank.stop()
            self.blue_tank.stop()
            
            #Moving and shooting
            if TOURNAMENT_MODE:
                #BlueActions
                response = player1[0](Blue_data,Red_data,self.time_left)
                self.responseInterpreter(self.blue_tank,self.blue_cannon,"Blue_Bullets",response)
                
                #RedActions
                response = player2[0](Red_data,Blue_data,self.time_left)
                self.responseInterpreter(self.red_tank,self.red_cannon,"Red_Bullets",response)
                
            else:
                #BlueActions
                if BLUE_BOT_MODE:
                    response = blue_bot_algorithm(Blue_data,Red_data,self.time_left)
                    self.responseInterpreter(self.blue_tank,self.blue_cannon,"Blue_Bullets",response)
                else:
                    self.movement(self.blue_tank,self.blue_cannon)
                    self.shooting(self.blue_cannon,"Blue_Bullets")
                #RedActions
                if RED_BOT_MODE:
                    response = red_bot_algorithm(Red_data,Blue_data,self.time_left)
                    self.responseInterpreter(self.red_tank,self.red_cannon,"Red_Bullets",response)
                else:
                    self.movement(self.red_tank,self.red_cannon)
                    self.shooting(self.red_cannon,"Red_Bullets")
            
            #Colissions
                #Bullets with Walls
            for bullet in self.scene["Red_Bullets"]:
                wall_hit_list = arcade.check_for_collision_with_list(bullet,self.scene["Walls"])
                if wall_hit_list:
                    bullet.remove_from_sprite_lists()
                    self.red_cannon.bullets_now-=1
            for bullet in self.scene["Blue_Bullets"]:
                wall_hit_list = arcade.check_for_collision_with_list(bullet,self.scene["Walls"])
                if wall_hit_list:
                    bullet.remove_from_sprite_lists()
                    self.blue_cannon.bullets_now-=1
                #Tanks with Bullets
            Red_Got_Hit = arcade.check_for_collision_with_list(self.red_tank,self.scene["Blue_Bullets"])
            Blue_Got_Hit = arcade.check_for_collision_with_list(self.blue_tank,self.scene["Red_Bullets"])
            
            #Checking if anyone hit anyone
            if Blue_Got_Hit and Red_Got_Hit:
                self.end_screen("Assets/DRAW.png",SCALE_OF_BIG_IMAGES)
                self.playing=False
                
                who_won = 0
            elif Blue_Got_Hit:
                self.end_screen("Assets/RED_WON.png",SCALE_OF_BIG_IMAGES)
                self.playing=False
                who_won = 2
            elif Red_Got_Hit:
                self.end_screen("Assets/BLUE_WON.png",SCALE_OF_BIG_IMAGES)
                self.playing=False
                who_won = 1
            #Time section
            self.time_left-=1
            if self.time_left < TIME_SPEEDUP*60:
                red_distance = distance(self.red_tank.center_x,self.red_tank.center_y,WIN_WIDTH/2,WIN_HEIGHT/2)
                blue_distance = distance(self.blue_tank.center_x,self.blue_tank.center_y,WIN_WIDTH/2,WIN_HEIGHT/2)
                
                if self.time_left == 0:
                    if red_distance < blue_distance:
                        self.end_screen("Assets/RED_WON.png",SCALE_OF_BIG_IMAGES)
                        who_won = 2
                    elif blue_distance < red_distance:
                        self.end_screen("Assets/BLUE_WON.png",SCALE_OF_BIG_IMAGES)
                        who_won = 1
                    else:
                        self.end_screen("Assets/DRAW.png",SCALE_OF_BIG_IMAGES)
                        who_won = 0
                    self.playing=False
                else:
                    if red_distance < blue_distance:
                        self.red_cannon.bul_speed=BOOSTED_BULLET_SPEED
                        self.blue_cannon.bul_speed=INITIAL_BULLET_SPEED
                    elif blue_distance < red_distance:
                        self.blue_cannon.bul_speed=BOOSTED_BULLET_SPEED
                        self.red_cannon.bul_speed=INITIAL_BULLET_SPEED
                    else:
                        self.red_cannon.bul_speed=BOOSTED_BULLET_SPEED
                        self.blue_cannon.bul_speed=BOOSTED_BULLET_SPEED
                    
            
            
            if CONSOLE_DUMP:
                dataDump(Red_data,Blue_data,self.time_left)
        else:
            if TOURNAMENT_AUTOSKIP:
                arcade.pause(1.0)
                arcade.close_window()
    def on_key_press(self,symbol,modifiers):
        match symbol:
            #Blue Tank Controls
            case arcade.key.W:
                self.blue_tank.button_forward = True
            case arcade.key.S:
                self.blue_tank.button_backward = True
            case arcade.key.A:
                self.blue_tank.button_left = True
            case arcade.key.D:
                self.blue_tank.button_right = True
            #Blue Cannon Controls
            case arcade.key.C:
                self.blue_cannon.button_left = True
            case arcade.key.V:
                self.blue_cannon.button_right = True
            case arcade.key.SPACE:
                self.blue_cannon.button_shoot = True
            #Red Tank Controls
            case arcade.key.UP:
                self.red_tank.button_forward = True
            case arcade.key.DOWN:
                self.red_tank.button_backward = True
            case arcade.key.LEFT:
                self.red_tank.button_left = True
            case arcade.key.RIGHT:
                self.red_tank.button_right = True
            #Red Cannon Controls
            case arcade.key.PERIOD:
                self.red_cannon.button_left = True
            case arcade.key.SLASH:
                self.red_cannon.button_right = True
            case arcade.key.RSHIFT:
                self.red_cannon.button_shoot = True
    def on_key_release(self,symbol,modifiers):
        match symbol:
            #Blue Tank Controls
            case arcade.key.W:
                self.blue_tank.button_forward = False
            case arcade.key.S:
                self.blue_tank.button_backward = False
            case arcade.key.A:
                self.blue_tank.button_left = False
            case arcade.key.D:
                self.blue_tank.button_right = False
            #Blue Cannon Controls
            case arcade.key.C:
                self.blue_cannon.button_left = False
            case arcade.key.V:
                self.blue_cannon.button_right = False
            case arcade.key.SPACE:
                self.blue_cannon.button_shoot = False
            #Red Tank Controls
            case arcade.key.UP:
                self.red_tank.button_forward = False
            case arcade.key.DOWN:
                self.red_tank.button_backward = False
            case arcade.key.LEFT:
                self.red_tank.button_left = False
            case arcade.key.RIGHT:
                self.red_tank.button_right = False
            #Red Cannon Controls
            case arcade.key.PERIOD:
                self.red_cannon.button_left = False
            case arcade.key.SLASH:
                self.red_cannon.button_right = False
            case arcade.key.RSHIFT:
                self.red_cannon.button_shoot = False
            
            #Utilities
            case arcade.key.R:
                self.setup()
            case arcade.key.ESCAPE:
                arcade.close_window()
    def movement(self,tank,cannon):
        #Tank movement
        if tank.button_forward:
            tank.strafe(tank.mov_speed)
        if tank.button_backward:
            tank.strafe(-tank.mov_speed)
        if tank.button_left:
            tank.turn_left(tank.rot_speed)
        if tank.button_right:
            tank.turn_right(tank.rot_speed)
        #Cannon movement
        if cannon.button_left:
            cannon.turn_left(cannon.rot_speed)
        if cannon.button_right:
            cannon.turn_right(cannon.rot_speed)
    def shooting(self,cannon,sprite_list):
        #Tank shooting
        if cannon.cooldown_left == 0:
            if cannon.bullets_now < cannon.bullets_max and cannon.button_shoot:
                bullet = arcade.Sprite("Assets/Bullet.png", SCALE_OF_SMALL_IMAGES)
                bullet.center_x = cannon.center_x
                bullet.center_y = cannon.center_y
                bullet.turn_left(cannon.angle)
                bullet.strafe(cannon.bul_speed)
                self.scene.add_sprite(sprite_list,bullet)

                cannon.bullets_now+=1
                cannon.cooldown_left = cannon.cooldown_max
        else:
            cannon.cooldown_left -=1
    def end_screen(self,path,size):
        end_image = arcade.Sprite(path,size)
        end_image.center_x = WIN_WIDTH/2
        end_image.center_y = WIN_HEIGHT/2
        self.scene.add_sprite("END_SCREEN",end_image)
    def responseInterpreter(self,tank,cannon,sprite_list,response):
        #Tank movement
        if "forward" in response:
            tank.strafe(tank.mov_speed)
        if "backward" in response:
            tank.strafe(-tank.mov_speed)
        if "tank_left" in response:
            tank.turn_left(tank.rot_speed)
        if "tank_right" in response:
            tank.turn_right(tank.rot_speed)
        #Cannon movement
        if "cannon_left" in response:
            cannon.turn_left(cannon.rot_speed)
        if "cannon_right" in response:
            cannon.turn_right(cannon.rot_speed)
        #Shooting
        if cannon.cooldown_left == 0:
            if cannon.bullets_now < cannon.bullets_max and "shoot" in response:
                bullet = arcade.Sprite("Assets/Bullet.png", SCALE_OF_SMALL_IMAGES)
                bullet.center_x = cannon.center_x
                bullet.center_y = cannon.center_y
                bullet.turn_left(cannon.angle)
                bullet.strafe(cannon.bul_speed)
                self.scene.add_sprite(sprite_list,bullet)

                cannon.bullets_now+=1
                cannon.cooldown_left = cannon.cooldown_max
        else:
            cannon.cooldown_left -=1
def dataDump(redData,blueData,time_left):
    print(redData)
    print(blueData)
    print(time_left)
def red_bot_algorithm(Me,Enemy,frames_left):
    response = ["forward","tank_right","cannon_left","shoot"]
    return response
def blue_bot_algorithm(Me,Enemy,frames_left):
    response = ["forward","tank_left","cannon_right","shoot"]
    return response

arcade.enable_timings()

if TOURNAMENT_MODE:
    theTanks = [func for func in dir(tournament_algorithms) if not func.startswith('__')]

    theTankFunctions = dict()
    for tank in theTanks:
        theTankFunctions[tank] = [getattr(tournament_algorithms,tank),0]

    for x in theTankFunctions:
        for y in theTankFunctions:
            if x == y:
                print("mirror, passing")
            else:
                player1 = theTankFunctions[x]
                player2 = theTankFunctions[y]
                GameWindow(WIN_WIDTH,WIN_HEIGHT,"THE TANK GAME by Chili0xFF", arcade.color.CADET_GREY)
                arcade.run()
                arcade.close_window()
                if who_won == 0:
                    print("Draw! Points were not awarded")
                else:
                    print("Player"+str(who_won)+" won!")
                    if who_won == 1:
                        theTankFunctions[x][1]+=1
                    elif who_won ==2:
                        theTankFunctions[y][1]+=1
    print("end of tournament")
    print("_________________")
    print("name   ||  points")
    for x in theTankFunctions:
        print(str(theTankFunctions[x][0].__name__)+" ||  "+str(theTankFunctions[x][1]))
else:
    GameWindow(WIN_WIDTH,WIN_HEIGHT,"THE TANK GAME by Chili0xFF", arcade.color.CADET_GREY)
    arcade.run()



#Game made by Chili0xFF. No rights reserved. For educational purposes only
#Please consider buying me coffee if you see me in the hallway: Grey hair, always tired. 
#If you ever use this project for literally any reason, please send me an email, it would be nice :>
#Thanks