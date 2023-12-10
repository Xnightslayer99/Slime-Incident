import pygame, sys, math, random
from pygame.locals import QUIT
pygame.init()
DISPLAYSURF = pygame.display.set_mode((600, 450))
clock = pygame.time.Clock()
pygame.display.set_caption('Slime Incident')

# The game music
pygame.mixer.music.load('slime incident - camellia.mp3')
pygame.mixer.music.set_volume(0.05)
#pygame.mixer.music.play()

# initialize player
global i_frames
i_frames = 0
class Player:
  def __init__(self, image, speed, x, y, maxHp):
    self.speed = speed
    self.image = image
    self.width = 16
    self.height = 16
    self.x = x
    self.y = y
    self.pos = (self.x, self.y)
    self.maxHp = maxHp
    self.hp = maxHp
    self.pierce = 3
    self.diffMult = 1
    self.strength = 1
    self.basicShotCooldown = 300 #basic shot type
    self.basicShotCooldown_limit = self.basicShotCooldown #sets the limit to which the cooldown can be reset
        
    self.shotCooldown = self.basicShotCooldown * 2 #same as above
    self.shotCooldown_limit = self.shotCooldown #same as above

    #leveling system and stuff (woohoo)
    self.level = 0
    self.exp = 0
    self.exp_to_next_level = 10
    
 #sets up player movement
  def move(self, up=False, down=False, left=False, right=False):
    if right:
     self.x += self.speed
    if left:
     self.x -= self.speed
    if down:
     self.y += self.speed
    if up:
     self.y -= self.speed
      
 #take damage
  def damage(self, kind, amount, currentHp, i_frameCounter):
   if i_frameCounter < 1500:
     return True
   else:
     if kind == "d":
       currentHp -= amount
     if kind == "h":
       currentHp += amount
     self.hp = currentHp
     if self.hp > self.maxHp:
       self.hp = self.maxHp
     return 0

  def attemptShot(self, shotType):
    if shotType == "basic":
      if self.basicShotCooldown > self.basicShotCooldown_limit:
        self.basicShotCooldown = 0
        return True #you can shoot
      else:
        return False #you can't shoot

    if shotType == "burst":
      if self.shotCooldown > self.shotCooldown_limit:
        self.shotCooldown = 0
        return True #you can do a burst shot
      else:
        return False #you can't do a burst shot
  def calcXp(self):
    if self.exp >= self.exp_to_next_level: #leveling up
      self.level += 1
      self.exp_to_next_level = (self.level * 15)
  def changeLevelMods(self, burstUnlocked):
    if self.level % 2 == 1: #odd levels decrease basic shot cooldown
      self.basicShotCooldown_limit -= 5
      if self.basicShotCooldown_limit == 0:
        self.basicShotCooldown_limit = 5
    if burstUnlocked:
      if self.level % 2 == 0: #even levels decrease burst shot cooldown
        self.shotCooldown_limit -= 5
        if self.shotCooldown_limit == 0:
          self.shotCooldown_limit = 5
    if self.level % 3 == 0: #levels divisible by 3 increase hp
      self.maxHp += 2
      self.hp += self.maxHp//2
      if self.maxHp > 60:
        self.maxHp = 60
      if self.hp > self.maxHp:
        self.hp = self.maxHp
    if self.level % 5 == 0: #levels divisible by 5 increase pierce
      self.pierce += 1
    if self.level % 9 == 0: #levels divisible by 9 decrease burst shot cooldown
      self.shotCooldown_limit -= 15
      if self.shotCooldown_limit <= 0:
        self.shotCooldown_limit = 5
    if self.level % 10 == 0: #levels divisible by 10 increase difficulty multiplier
      self.diffMult += 1
    if self.level > 40: #levels above 40 decrease burst shot cooldown
      self.shotCooldown_limit -= 5
      if self.shotCooldown_limit <= 0:
        self.shotCooldown_limit = 5
    if self.level % 15 == 0: #levels divisible by 15 increase damage
      self.strength += 1
    if self.level >= 10:
      return True
#initialize projectile
class Projectile():
  def __init__(self, owner, image, speed, x, y, direction, pierce):
    self.image = image
    self.speed = speed
    self.owner = owner
    self.x = x
    self. y = y
    self.direction = direction
    self.pierce = pierce

  #sets up the movement
  def move(self, direction):
    if direction == 2: #right
      self.x += self.speed
    if direction == 6: #left
      self.x -= self.speed
    if direction == 0: #up
      self.y -= self.speed
    if direction == 4: #down
      self.y += self.speed
    if direction == 1: #up + right
      self.x  += self.speed
      self.y -= self.speed
    if direction == 3: #down + right
      self.x  += self.speed
      self.y += self.speed
    if direction == 5: #down + left
      self.x  -= self.speed
      self.y += self.speed
    if direction == 7: #up + left
      self.x  -= self.speed
      self.y -= self.speed

#creates an Enemy
class Enemy:
  def __init__(self, image, speed, x, y, kind, maxHp, i_frame):
    self.speed = speed
    self.image = image
    self.height = 16
    self.width = 16
    self.x = x
    self.y = y
    self.kind = kind
    self.maxHp = maxHp
    self.hp = maxHp
    self.i_frame = i_frame
  def move(self, x=0, y=0):
    if x == 1:
      self.x += self.speed
    if x == -1:
      self.x -= self.speed
    if y == 1:
      self.y += self.speed
    if y == -1:
      self.y -= self.speed

  #movement for the salt cube enemy type
  def saltCubeAi(self, player_x, player_y):
    x_weight = 0 #if negative, move left, else move right
    y_weight = 0 #if negative move down, else move up
    for i in range(10):
      if (player_x - self.x) < 0:
        x_weight -= 1
      if (player_x - self.x) > 0:
        x_weight += 1
    for i in range(10):
      if (player_y - self.y) < 0:
        y_weight -= 1
      if (player_y - self.y) > 0:
        y_weight += 1
    
    if x_weight > 0 and y_weight > 0:
      self.move(1, 1)
    if x_weight > 0 and y_weight < 0:
      self.move(1, -1)
    if x_weight < 0 and y_weight > 0:
      self.move(-1, 1)
    if x_weight < 0 and y_weight < 0:
      self.move(-1, -1)
    if y_weight == 0:
      if x_weight > 0:
        self.move(1, 0)
      if x_weight < 0:
        self.move(-1, 0)
    if x_weight == 0:
      if y_weight > 0:
        self.move(0, 1)
      if y_weight < 0:
        self.move(0, -1)

  #movement for the platter enemy
  def ctbAi(self, player_x, player_y, shot_cooldown):
    #change height and width values
    self.width = 32
    self.height = 32
    if shot_cooldown > 500:
      shot_cooldown = 0
    offset_range = 15 #for allowing the enemy to shoot horizontally and vertically
    
    #horizontal
    y_offsets = [int(self.y+i) for i in range(offset_range)]
    y_offsets += [int(self.y-i) for i in range(offset_range)]
    
    #vertical
    x_offsets = [int(self.x+i) for i in range(offset_range)]
    x_offsets += [int(self.x-i) for i in range(offset_range)]
    above = not(player_y > self.y)
    right = player_x > self.x
    sameY = player_y in y_offsets
    sameX = player_x in x_offsets
    rise = abs(player_y - self.y)
    run = abs(player_x - self.x)
    distanceToPlayer = math.sqrt(rise**2 + run**2)
    if distanceToPlayer > 80:
      if above:
        self.move(0, -1)
      if not above:
        self.move(0, 1)
      if right:
        self.move(1,0)
      if not right:
        self.move(-1, 0)
    else:
      if right and sameY and shot_cooldown == 0: # player is to the right
        projectiles.append(Projectile(self, droplet_ctb, 5, self.x + self.width//4, self.y + self.height//4, 2, 1))
        
      elif not right and sameY and shot_cooldown == 0: # player is to the left
        projectiles.append(Projectile(self, droplet_ctb, 5, self.x + self.width//4, self.y + self.height//4, 6, 1))
        
      elif sameX and above and shot_cooldown == 0: # player is above
        projectiles.append(Projectile(self, droplet_ctb, 5, self.x + self.width//4, self.y + self.height//4, 0, 1))
        
      elif sameX and not above and shot_cooldown == 0: #player is below
        projectiles.append(Projectile(self, droplet_ctb, 5, self.x + self.width//4, self.y + self.height//4, 4, 1))
        
      elif not right and not above and shot_cooldown == 0: # player is to the left and below
        projectiles.append(Projectile(self, droplet_ctb, 5, self.x + self.width//4, self.y + self.height//4, 5, 1))
        
      elif not right and above and shot_cooldown == 0: # player is to the left and above
        projectiles.append(Projectile(self, droplet_ctb, 5, self.x + self.width//4, self.y + self.height//4, 7, 1))
        
      elif right and not above and shot_cooldown == 0: # player is to the right and below
        projectiles.append(Projectile(self, droplet_ctb, 5, self.x + self.width//4, self.y + self.height//4, 3, 1))
        
      elif right and above and shot_cooldown == 0: # player is to the right and above
        projectiles.append(Projectile(self, droplet_ctb, 5, self.x + self.width//4, self.y + self.height//4, 1, 1))
      
      if shot_cooldown == 0:
        return 0

  def damage(self, kind, amount, currentHp):
    if self.i_frame < 250:
      return True
    else:
      if kind == "d":
        currentHp -= amount
      if kind == "h":
        currentHp += amount
      self.hp = currentHp
      if self.hp > self.maxHp:
        self.hp = self.maxHp
      return 0

#Makes the waves
def wave(enemies, enemies_to_spawn, spawn_verticies):
  saltcube = pygame.image.load('enemy-salt.png')
  ctb = pygame.image.load('enemy-platter.png')
  spawn_locations = [(200, 400), (343, 343), (400, 200), (343, 57), (200, 0), (57, 57), (0, 200), (57, 343)]
  if spawn_verticies == 8: #octogon
    for i in range(8):
      if enemies_to_spawn[i] == "saltCube":
        enemies.append(Enemy(saltcube, 1, spawn_locations[i][0] + 100, spawn_locations[i][1], enemies_to_spawn[i], 1*p.diffMult, 0))
      if enemies_to_spawn[i] == "ctb":
        enemies.append(Enemy(ctb, 1, spawn_locations[i][0] + 100, spawn_locations[i][1], enemies_to_spawn[i], 2*p.diffMult, 0))
        
  if spawn_verticies == 4: #square
    spawn_locations = [(343, 343), (343, 57), (57, 57), (57, 343)] #4 corners
    for i in range(0, 4):
      if enemies_to_spawn[i] == "saltCube":
        enemies.append(Enemy(saltcube, 1, spawn_locations[i][0] + 100, spawn_locations[i][1], enemies_to_spawn[i], 1*p.diffMult, 0))
      if enemies_to_spawn[i] == "ctb":
        enemies.append(Enemy(ctb, 1, spawn_locations[i][0] + 100, spawn_locations[i][1], enemies_to_spawn[i], 2*p.diffMult, 0))
        
  if spawn_verticies == 3: #triangle
    spawn_locations = [(200, 400), (373, 100), (27, 100)] #verticies
    for i in range(3):
      if enemies_to_spawn[i] == "saltCube":
        enemies.append(Enemy(saltcube, 1, spawn_locations[i][0] + 100, spawn_locations[i][1], enemies_to_spawn[i], 1*p.diffMult, 0))
      if enemies_to_spawn[i] == "ctb":
        enemies.append(Enemy(ctb, 1, spawn_locations[i][0] + 100, spawn_locations[i][1], enemies_to_spawn[i], 2*p.diffMult, 0))
      
#drawing the screen
def redraw(activeRoom, previousRoom):
  #if the player is over 400p to the right, send them to the left size, and vice versa
  if p.x > 600:
    p.x = 9
  elif p.x < 0:
    p.x = 591
  
  #if the player is too far up, send them to the bottom (failsafe)
  if p.y > 450:
    p.y = 9
  if p.y < 0:
    p.y = 441
  DISPLAYSURF.blit(pygame.transform.scale2x(background), (0,0))
  pygame.draw.rect(DISPLAYSURF, (112, 112, 112), rooms[activeRoom])
  DISPLAYSURF.blit(p.image, (p.x, p.y))
  hearts = []
  if p.hp % 2 == 1:
    for i in range(0, p.hp-1, 2):
      hearts.append(heart_full)
    hearts.append(heart_half)
  elif p.hp % 2 == 0:
    for i in range(0, p.hp, 2):
      hearts.append(heart_full)
  while len(hearts) < math.ceil(p.maxHp/2):
      hearts.append(heart_empty)
  #draws the hearts
  for i in range(math.ceil(p.maxHp/2)):
    try:
      if i == 0:
        DISPLAYSURF.blit(heart_empty, (2, 3))
        if (p.hp) % 2 == 1:
          DISPLAYSURF.blit(hearts[i], (2, 3))
        elif p.hp > 0:
          DISPLAYSURF.blit(heart_full, (2, 3))
      else:
        DISPLAYSURF.blit(heart_empty, (2+(i*16), 3))
        if (p.hp) % 2 == 1:
            DISPLAYSURF.blit(hearts[i], (2+(i*16), 3))
        elif p.hp > 0:
          if p.hp <= p.maxHp - 2:
            DISPLAYSURF.blit(hearts[i], (2+(i*16), 3))
          else:
            DISPLAYSURF.blit(hearts[i], (2+(i*16), 3))
    except:
      pass
  DISPLAYSURF.blits(((projectile.image, (projectile.x, projectile.y)) for projectile in projectiles))
  for enemy in enemies:
    if enemy.kind == "ctb":
      DISPLAYSURF.blit(pygame.transform.scale2x(enemy.image), (enemy.x, enemy.y-8))
    else:
      DISPLAYSURF.blit(enemy.image, (enemy.x, enemy.y))
  level = str(p.level)
  DISPLAYSURF.blit(font.render(level, True, (0, 0, 0)), (2, 30))
  pygame.display.update()

#room logic thing?
def roomLogic(activeRoom, previousRoom):
  print("starting: ", activeRoom, previousRoom)
  if activeRoom == 0 and previousRoom == 0:
    activeRoom, previousRoom = 1, 1
    
  elif activeRoom == 1 and previousRoom == 0:
    activeRoom, previousRoom = 2, 2
    
  elif previousRoom == 1 and activeRoom == 1:
    activeRoom, previousRoom = 2, 2
    
  elif activeRoom == 2 and previousRoom == 1:
    previousRoom = 2
    
  elif previousRoom == 2 and activeRoom == 2:
    activeRoom = 1
    
  elif previousRoom == 2 and activeRoom == 1:
    activeRoom, previousRoom = 0, 1
    
  elif previousRoom == 1 and activeRoom == 0:
    previousRoom, activeRoom = 0, 1
    
  return activeRoom, previousRoom
#room swapping
def swapRoom(activeRoom, previousRoom, rooms):
  if not rooms[activeRoom].contains(playerHitbox):
      if activeRoom == 0 and p.x < rooms[activeRoom].centerx:
        pass
            #p.x = rooms[activeRoom].x
      elif activeRoom == 2 and p.x > rooms[activeRoom].centerx:
        pass
          #p.x = rooms[activeRoom].width
      else:
        activeRoom, previousRoom = roomLogic(activeRoom, previousRoom)
      print("final: ", activeRoom, previousRoom)
      if p.x >= rooms[activeRoom].centerx:
        if activeRoom == 2:
          p.x = rooms[activeRoom].right-17
          if p.y < rooms[activeRoom].y:
            p.y = rooms[activeRoom].y + 17
          else:
            pass
        else:
          p.x, p.y = rooms[activeRoom].x + 17, rooms[activeRoom].y + 17
      else:
        if activeRoom == 0:
          p.x = rooms[activeRoom].x
        else:
          p.x, p.y = rooms[activeRoom].width - 17, rooms[activeRoom].height - 17
  return activeRoom, previousRoom

#image loading
player = pygame.image.load("player.png")
background = pygame.image.load("background.png")
droplet = pygame.image.load("droplet.png")
droplet_ctb = pygame.image.load('droplet-enemy.png')
heart_full, heart_half, heart_empty = pygame.image.load("heart-full.png"), pygame.image.load("heart-half.png"), pygame.image.load("heart-empty.png")
gameover = pygame.image.load("deathScreen.png")

#background initialization
DISPLAYSURF.blit(background, (0,0))

#shows background immediately
pygame.display.update()

#sets up enemies, player(and their hp), and projectiles
enemies = []
enemyChoices = ['saltCube', 'ctb']
p = Player(player, 3, 300, 225, 6)
projectiles = []
#Main loop
cooldown = 0
shot_cooldown = 0
ei_frames = 0
burstShotUnlocked = False
burstOnCooldown = True
basicOnCooldown = True
level_changed = False
current_level = p.level
previous_level = p.level
font = pygame.font.SysFont(None, 48)
rooms =[]
rooms.append(pygame.Rect((50, 50), (400, 300)))
rooms.append(pygame.Rect((25, 100), (200, 150)))
rooms.append(pygame.Rect((80, 200), (200, 200)))
activeRoom = 0
previousRoom = 0
while True:
  playerHitbox = pygame.Rect((p.x, p.y), (p.width, p.height))
  cooldown += 20
  if cooldown >= 400:
    cooldown = 0
  if basicOnCooldown:
    p.basicShotCooldown += 5
  if burstOnCooldown:
    p.shotCooldown += 5
  keys = pygame.key.get_pressed()
  #direction is added to avoid the projectile moving in the direction the player is constantly (that was a bug that happened, it was hilarious)
  global direction
  direction = 0
  if keys[pygame.K_l]:
    p.level += 1
  if keys[pygame.K_UP]:
    p.move(up=True)
    direction = 0
    if keys[pygame.K_LEFT]:
      p.move(left=True)
      direction = 7
    elif keys[pygame.K_RIGHT]:
      p.move(right=True)
      direction = 1
  elif keys[pygame.K_DOWN]:
    p.move(down=True)
    direction = 4
    if keys[pygame.K_LEFT]:
      p.move(left=True)
      direction = 5
    elif keys[pygame.K_RIGHT]:
      p.move(right=True)
      direction = 3
  elif keys[pygame.K_LEFT]:
    p.move(left=True)
    direction = 6
  elif keys[pygame.K_RIGHT]:
    p.move(right=True)
    direction = 2
  if keys[pygame.K_SPACE]:
    if p.attemptShot("basic") == True:
      projectiles.append(Projectile(p, droplet, 5, p.x + 4, p.y + 4, direction, p.pierce))
    else:
      basicOnCooldown = True
  if keys[pygame.K_c] and burstShotUnlocked:
      if p.attemptShot("burst") == True:
        for i in range(1, 9):
          projectiles.append(Projectile(p, droplet, 5, p.x + 4, p.y + 4, i-1, p.pierce))
      else:
        burstOnCooldown = True
  if keys[pygame.K_d] and cooldown == 0:
    p.damage("d", 1, p.hp, 1501)
  if keys[pygame.K_h]:
    p.damage("h", p.maxHp, p.hp, 1501)
  if keys[pygame.K_w]:
    verticies = random.choice([3, 4, 8])
    #wave(enemies, [random.choice(enemyChoices) for each in range(verticies)], verticies)
  #makes each projectile move in the correct direction
  for projectile in projectiles:
    projectile.move(projectile.direction)

  #do i-frame stuff and shot cooldown stuff
  i_frames += 20
  for enemy in enemies:
    enemy.i_frame += 20
  shot_cooldown += 20
  
  #checks if the projectiles hit the enemies
  for projectile in projectiles:
    enemies_hit = 0
    
    if projectile.owner == p: #checks if the projectile is owned by the player
      for enemy in enemies:
        if enemy.kind == "saltCube":
          if projectile.x > enemy.x - enemy.width and projectile.x < enemy.x + enemy.width and projectile.y > enemy.y - enemy.height and projectile.y < enemy.y + enemy.height:
            for i in range(projectile.pierce):
              if enemy.damage("d", p.strength, enemy.hp) == 0:
                enemy.i_frame = 0
                projectile.pierce -= 1
              try:
                if projectile.pierce == 0: #adds pierce
                  projectiles.remove(projectile)
                  break
                if enemy.hp <= 0:
                  p.exp += 1
                  enemies.remove(enemy)
                  break
              except:
                pass
        elif enemy.kind == "ctb":
          if projectile.x > enemy.x - enemy.width and projectile.x < enemy.x + enemy.width and projectile.y > (enemy.y-8) - enemy.height and projectile.y < (enemy.y-8) + enemy.height:
            for i in range(projectile.pierce):
              if enemy.damage("d", p.strength, enemy.hp) == 0:
                enemy.i_frame = 0
                projectile.pierce -= 1
              try:
                if projectile.pierce == 0: #adds pierce
                  projectiles.remove(projectile)
                  break
                if enemy.hp <= 0:
                  p.exp += 2
                  enemies.remove(enemy)
                  break
              except:
                pass
    elif projectile.owner in enemies: #since the owner is not the player, check if it is touching the player to apply damage
      if projectile.x > p.x - p.width and projectile.x < p.x + p.width and projectile.y > p.y - p.height and projectile.y < p.y + p.height:
        i_frames += 5 * clock.get_time()
        if p.damage("d", 1*p.diffMult, p.hp, i_frames) == 0:
          i_frames = 0
          continue
        try:
            projectiles.remove(projectile)
        except:
          pass
  #checks if enemies are touching the player
  for enemy in enemies:
    if enemy.kind == "saltCube":
      if p.x > enemy.x - enemy.width and p.x < enemy.x + enemy.width and p.y > enemy.y - enemy.height and p.y < enemy.y + enemy.height:
        i_frames += clock.get_time()
        if p.damage("d", 1*p.diffMult, p.hp, i_frames) == 0:
          i_frames = 0
  #do enemy movement
  for enemy in enemies:
    if enemy.kind == "saltCube":
      enemy.saltCubeAi(p.x, p.y)
    if enemy.kind == "ctb":
      if enemy.ctbAi(p.x, p.y, shot_cooldown) == 0:
        shot_cooldown = 0
  try:
    for i in range(len(projectiles)): #removes projectiles that are out of bounds
      if projectiles[i].x > 600 or projectiles[i].x < 0 or projectiles[i].y > 450 or projectiles[i].y < 0:
        projectiles.pop(i)
  except:
    pass
  if enemies == [] or (len(enemies) < p.level//3): #waves
    verticies = random.choice([3, 4, 8])
    #wave(enemies, [random.choice(enemyChoices) for each in range(verticies)], verticies)

  p.calcXp()
  current_level = p.level
  level_changed = (current_level != previous_level)
  if level_changed:
    if p.changeLevelMods(burstShotUnlocked) == True: # do levels
      burstShotUnlocked = True
  previous_level = current_level
  if p.hp <= 0: #player death
    DISPLAYSURF.blit(background, (0,0))
    DISPLAYSURF.blit(pygame.transform.scale2x(gameover), (0, 0))
    pygame.display.update()
    pygame.time.wait(2000)
    pygame.quit()
    quit()
  for event in pygame.event.get():
      if event.type == QUIT:
        pygame.quit()
        sys.exit()
  activeRoom, previousRoom = swapRoom(activeRoom, previousRoom, rooms)
  redraw(activeRoom, previousRoom)
  clock.tick(30)
          