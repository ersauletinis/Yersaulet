
import pygame, random, json, os, sys, math
pygame.init(); pygame.mixer.init()
 
SW, SH = 480, 720
screen = pygame.display.set_mode((SW, SH))
pygame.display.set_caption("Road Racer")
clock = pygame.time.Clock()
 
BLACK=(0,0,0); WHITE=(255,255,255); GRAY=(80,80,80); DGRAY=(40,40,40)
YELLOW=(255,220,0); RED=(220,50,50); GREEN=(50,200,80); BLUE=(50,120,255)
ORANGE=(255,140,0); LGRAY=(160,160,160); ROAD=(55,55,55); GRASS=(34,139,34)
 
FB=pygame.font.SysFont("Arial",52,bold=True)
FM=pygame.font.SysFont("Arial",30,bold=True)
FS=pygame.font.SysFont("Arial",20)
FT=pygame.font.SysFont("Arial",16)
 
LB_FILE="leaderboard.json"
RL,RR=70,410; RW=RR-RL; LW=RW//3
LANE=[RL+LW*i+LW//2 for i in range(3)]
CW,CH=50,86
 
def _img(f,w,h,flip=False):
    if os.path.exists(f):
        try:
            i=pygame.image.load(f).convert_alpha()
            i=pygame.transform.scale(i,(w,h))
            return pygame.transform.flip(i,False,True) if flip else i
        except: pass
    return None
 
CAR_IMGS=[_img(f,CW,CH) for f in ["TSIS3/images/NPC4.jpg","TSIS3/images/NPC1.jpg","TSIS3/images/NPC2.jpg"]]
TRAFFIC_IMG=next((_img(f,CW,CH,True) for f in ["TSIS3/images/NPC4.jpg","TSIS3/images/NPC1.jpg","TSIS3/images/NPC2.jpg"] if os.path.exists(f)),None)
CAR_COL=[(220,50,50),(50,120,255),(255,220,0)]
CAR_NAME=["Red Racer","Blue Bullet","Yellow Flash"]
 
def _snd(f):
    if os.path.exists(f):
        try: return pygame.mixer.Sound(f)
        except: pass
SFX={n:_snd(f) for n,f in [("coin","TSIS3/sounds/coin.mp3"),("crash","TSIS3/sounds/crash.mp3")]}
 
def play(n):
    if SFX.get(n): SFX[n].play()
 
def music(f):
    if os.path.exists(f):
        try: pygame.mixer.music.load(f); pygame.mixer.music.play(-1)
        except: pass
 
def draw_car(s,x,y,i,a=255):
    img=CAR_IMGS[i] if i<len(CAR_IMGS) else None
    if img:
        t=img.copy(); t.set_alpha(a); s.blit(t,(x-CW//2,y-CH//2))
    else:
        r=pygame.Rect(x-CW//2,y-CH//2,CW,CH)
        pygame.draw.rect(s,CAR_COL[i%3],r,border_radius=8)
        pygame.draw.rect(s,WHITE,r,2,border_radius=8)
 
def draw_road(s):
    s.fill(GRASS)
    pygame.draw.rect(s,(100,60,30),(0,0,RL,SH))
    pygame.draw.rect(s,(100,60,30),(RR,0,SW-RR,SH))
    pygame.draw.rect(s,ROAD,(RL,0,RW,SH))
    for lx in [RL+LW,RL+LW*2]:
        for y in range(0,SH,60): pygame.draw.rect(s,LGRAY,(lx-2,y,4,30))
 
def txt(s,text,f,col,cx,cy):
    r=f.render(text,True,col); s.blit(r,r.get_rect(center=(cx,cy)))
 
def load_lb():
    if os.path.exists(LB_FILE):
        try:
            with open(LB_FILE) as f: return json.load(f)
        except: pass
    return []
 
def save_lb(e):
    with open(LB_FILE,"w") as f: json.dump(sorted(e,key=lambda x:-x["score"])[:10],f)
 
class Btn:
    def __init__(self,t,cx,cy,w=220,h=48):
        self.t=t; self.r=pygame.Rect(cx-w//2,cy-h//2,w,h)
    def draw(self,s,mx,my):
        c=(80,80,80) if self.r.collidepoint(mx,my) else (45,45,45)
        pygame.draw.rect(s,c,self.r,border_radius=9)
        pygame.draw.rect(s,WHITE,self.r,2,border_radius=9)
        txt(s,self.t,FM,WHITE,self.r.centerx,self.r.centery)
    def hit(self,pos): return self.r.collidepoint(pos)
 
def sc_name(cur=""):
    name=cur; blink=0
    ok=Btn("Start",SW//2,SH//2+80)
    while True:
        clock.tick(60); blink+=1; mx,my=pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit()
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_BACKSPACE: name=name[:-1]
                elif e.key in(pygame.K_RETURN,pygame.K_KP_ENTER):
                    if name.strip(): return name.strip()
                elif len(name)<14: name+=e.unicode
            if e.type==pygame.MOUSEBUTTONDOWN and ok.hit((mx,my)) and name.strip():
                return name.strip()
        draw_road(screen)
        pygame.draw.rect(screen,DGRAY,(60,SH//2-110,SW-120,240),border_radius=12)
        txt(screen,"Your Name",FM,YELLOW,SW//2,SH//2-60)
        box=pygame.Rect(80,SH//2-18,SW-160,40)
        pygame.draw.rect(screen,GRAY,box,border_radius=7)
        pygame.draw.rect(screen,YELLOW,box,2,border_radius=7)
        txt(screen,name+("|" if blink%40<20 else ""),FM,WHITE,SW//2,SH//2+2)
        ok.draw(screen,mx,my); pygame.display.flip()
 
def sc_settings(cfg):
    back=Btn("Back",SW//2,SH-70)
    bsnd=Btn("",SW//2,210,260,46); bdif=Btn("",SW//2,275,260,46)
    cbs=[Btn(CAR_NAME[i],SW//2,360+i*60,240,48) for i in range(3)]
    while True:
        clock.tick(60); mx,my=pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit()
            if e.type==pygame.MOUSEBUTTONDOWN:
                if back.hit((mx,my)): return cfg
                if bsnd.hit((mx,my)): cfg["sound"]=not cfg["sound"]
                if bdif.hit((mx,my)): cfg["diff"]={"Easy":"Normal","Normal":"Hard","Hard":"Easy"}[cfg["diff"]]
                for i,b in enumerate(cbs):
                    if b.hit((mx,my)): cfg["car"]=i
        draw_road(screen)
        pygame.draw.rect(screen,DGRAY,(25,90,SW-50,SH-160),border_radius=12)
        txt(screen,"Settings",FB,YELLOW,SW//2,140)
        bsnd.t=f"Sound: {'ON' if cfg['sound'] else 'OFF'}"; bdif.t=f"Diff: {cfg['diff']}"
        bsnd.draw(screen,mx,my); bdif.draw(screen,mx,my)
        txt(screen,"Car:",FS,WHITE,SW//2,330)
        for i,b in enumerate(cbs):
            b.draw(screen,mx,my); draw_car(screen,RL-18,360+i*60,i)
            if cfg["car"]==i: pygame.draw.rect(screen,YELLOW,b.r,3,border_radius=9)
        back.draw(screen,mx,my); pygame.display.flip()
 
def sc_lb():
    back=Btn("Back",SW//2,SH-55); lb=load_lb()
    while True:
        clock.tick(60); mx,my=pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit()
            if e.type==pygame.MOUSEBUTTONDOWN and back.hit((mx,my)): return
        draw_road(screen)
        pygame.draw.rect(screen,DGRAY,(20,55,SW-40,SH-115),border_radius=12)
        txt(screen,"Top 10",FB,YELLOW,SW//2,100)
        for i,e in enumerate(lb[:10]):
            col=YELLOW if i==0 else(LGRAY if i<3 else WHITE)
            s=FS.render(f"{i+1}. {e['name'][:11]:<12} {e['score']:<7} {e['dist']}m",True,col)
            screen.blit(s,(40,140+i*44))
        back.draw(screen,mx,my); pygame.display.flip()
 
def sc_over(name,score,dist,coins):
    lb=load_lb(); lb.append({"name":name,"score":score,"dist":int(dist)}); save_lb(lb)
    retry=Btn("Retry",SW//2,SH//2+50); menu=Btn("Main Menu",SW//2,SH//2+110)
    while True:
        clock.tick(60); mx,my=pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit()
            if e.type==pygame.MOUSEBUTTONDOWN:
                if retry.hit((mx,my)): return "retry"
                if menu.hit((mx,my)): return "menu"
        draw_road(screen)
        pygame.draw.rect(screen,DGRAY,(40,SH//2-160,SW-80,320),border_radius=14)
        txt(screen,"GAME OVER",FB,RED,SW//2,SH//2-110)
        for i,(l,v) in enumerate([("Score",score),("Dist",f"{int(dist)}m"),("Coins",coins)]):
            txt(screen,f"{l}: {v}",FM,WHITE,SW//2,SH//2-40+i*42)
        retry.draw(screen,mx,my); menu.draw(screen,mx,my); pygame.display.flip()
 
def sc_menu(cfg):
    play_b=Btn("Play",SW//2,310); lb_b=Btn("Leaderboard",SW//2,375)
    set_b=Btn("Settings",SW//2,440); q_b=Btn("Quit",SW//2,505)
    music("menu_music.ogg"); sy=0
    while True:
        clock.tick(60); mx,my=pygame.mouse.get_pos(); sy=(sy+4)%60
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit()
            if e.type==pygame.MOUSEBUTTONDOWN:
                if play_b.hit((mx,my)): pygame.mixer.music.stop(); return "play"
                if lb_b.hit((mx,my)): sc_lb()
                if set_b.hit((mx,my)): cfg=sc_settings(cfg)
                if q_b.hit((mx,my)): pygame.quit(); sys.exit()
        draw_road(screen)
        for y in range(-60+sy,SH+60,60):
            for lx in [RL+LW,RL+LW*2]: pygame.draw.rect(screen,LGRAY,(lx-2,y,4,30))
        txt(screen,"ROAD RACER",FB,YELLOW,SW//2,170)
        draw_car(screen,SW//2,255,cfg["car"])
        for b in [play_b,lb_b,set_b,q_b]: b.draw(screen,mx,my)
        pygame.display.flip()
 
DCFG={"Easy":(4.0,130,190,3),"Normal":(5.5,85,140,2),"Hard":(7.5,55,95,1)}
FINISH=2000
TC=[(220,50,50),(50,50,220),(50,180,80),(180,80,220),(220,150,50)]
 
def run(name,cfg):
    spd,t_int,o_int,lives=DCFG[cfg["diff"]]; ci=cfg["car"]; snd=cfg["sound"]
    px=float(LANE[1]); py=float(SH-110); tl=1
    score=coins=0; dist=0.0
    traffic=[]; obs=[]; coin_l=[]; pu_l=[]
    tt=to=tc2=tp=0
    apu=None; shield=False; nitro_end=0; flash=0
 
    music("game_music.ogg")
 
    class Obj:
        def __init__(self,lane,y,kind,w,h,col):
            self.lane=lane; self.x=float(LANE[lane]); self.y=float(y)
            self.kind=kind; self.w=w; self.h=h; self.col=col; self.alive=True
            self.spd=random.uniform(1.5,3) if kind=="tc" else 0
            self.born=pygame.time.get_ticks()
        def rect(self): return pygame.Rect(self.x-self.w//2,self.y-self.h//2,self.w,self.h)
        def update(self,s):
            self.y+=s*(0.6 if self.kind=="tc" else 1)+self.spd
            if self.kind=="pu" and pygame.time.get_ticks()-self.born>7000: self.alive=False
        def draw(self,s):
            r=self.rect()
            if self.kind=="tc":
                if TRAFFIC_IMG:
                    img=TRAFFIC_IMG.copy()
                    t=pygame.Surface((CW,CH),pygame.SRCALPHA); t.fill((*self.col,70))
                    img.blit(t,(0,0),special_flags=pygame.BLEND_RGBA_ADD); s.blit(img,(r.x,r.y))
                else:
                    pygame.draw.rect(s,self.col,r,border_radius=6)
                    pygame.draw.rect(s,WHITE,r,2,border_radius=6)
            elif self.kind=="obs":
                pygame.draw.rect(s,ORANGE,r,border_radius=4)
                pygame.draw.rect(s,WHITE,r,2,border_radius=4)
                txt(s,"!!",FT,BLACK,r.centerx,r.centery)
            elif self.kind=="coin":
                t2=pygame.time.get_ticks()/300
                rr=self.w//2+int(math.sin(t2)*2)
                pygame.draw.circle(s,YELLOW,(int(self.x),int(self.y)),rr)
                pygame.draw.circle(s,(200,160,0),(int(self.x),int(self.y)),rr,2)
            elif self.kind=="pu":
                d={"NITRO":(ORANGE,"N"),"SHIELD":(BLUE,"S"),"REPAIR":(GREEN,"R")}[self.col]
                pygame.draw.rect(s,d[0],r,border_radius=6); pygame.draw.rect(s,WHITE,r,2,border_radius=6)
                txt(s,d[1],FT,WHITE,r.centerx,r.centery)
 
    while True:
        clock.tick(60)
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit()
            if e.type==pygame.KEYDOWN:
                if e.key in(pygame.K_LEFT,pygame.K_a) and tl>0: tl-=1
                if e.key in(pygame.K_RIGHT,pygame.K_d) and tl<2: tl+=1
        if pygame.mouse.get_pressed()[0]:
            mx,_=pygame.mouse.get_pos()
            if mx<RL+LW and tl>0: tl-=1
            elif mx>RL+LW*2 and tl<2: tl+=1
 
        tx=LANE[tl]; ms=14
        if abs(px-tx)<ms: px=tx
        elif px<tx: px+=ms
        else: px-=ms
 
        nitro=(pygame.time.get_ticks()<nitro_end)
        es=spd*(1+int(dist//300)*0.08)*(1.8 if nitro else 1)
        dist+=es*0.05; score+=1
        if dist>=FINISH:
            pygame.mixer.music.stop(); score+=500
            return sc_over(name,score,dist,coins)
 
        tt+=1;to+=1;tc2+=1;tp+=1
        dens=max(1,int(dist//400))
        if tt>t_int//dens:
            tt=0; l=random.randint(0,2); traffic.append(Obj(l,-CH,"tc",CW,CH,random.choice(TC)))
        if to>o_int:
            to=0; l=random.randint(0,2)
            if not(l==tl and any(abs(o.y-py)<120 for o in obs)):
                obs.append(Obj(l,-30,"obs",44,22,None))
        if tc2>55:
            tc2=0; l=random.randint(0,2); coin_l.append(Obj(l,-20,"coin",24,24,None))
        if tp>190 and apu is None:
            tp=0; l=random.randint(0,2)
            pu_l.append(Obj(l,-30,"pu",28,28,random.choice(["NITRO","SHIELD","REPAIR"])))
 
        for o in traffic+obs+coin_l+pu_l: o.update(es)
        traffic=[o for o in traffic if o.y<SH+80 and o.alive]
        obs=[o for o in obs if o.y<SH+80 and o.alive]
        coin_l=[o for o in coin_l if o.y<SH+80 and o.alive]
        pu_l=[o for o in pu_l if o.y<SH+80 and o.alive]
 
        pr=pygame.Rect(px-CW//2+5,py-CH//2+5,CW-10,CH-10)
        for c in coin_l:
            if pr.colliderect(c.rect()):
                c.alive=False; coins+=1; score+=20
                if snd: play("coin")
        for p in pu_l:
            if pr.colliderect(p.rect()) and apu is None:
                p.alive=False; k=p.col
                if k=="NITRO": apu="NITRO"; nitro_end=pygame.time.get_ticks()+4000
                elif k=="SHIELD": apu="SHIELD"; shield=True
                elif k=="REPAIR": lives=min(lives+1,DCFG[cfg["diff"]][3])
 
        flash=max(0,flash-16)
        if flash==0:
            for o in traffic+obs:
                if pr.colliderect(o.rect()):
                    o.alive=False; flash=800
                    if shield: shield=False; apu=None
                    else:
                        lives-=1
                        if snd: play("crash")
                        if lives<=0:
                            pygame.mixer.music.stop()
                            return sc_over(name,score,dist,coins)
 
        if apu=="NITRO" and not nitro: apu=None
        if apu=="SHIELD" and not shield: apu=None
 
        draw_road(screen)
        for o in obs+traffic+coin_l+pu_l: o.draw(screen)
        if shield: pygame.draw.circle(screen,BLUE,(int(px),int(py)),CW,3)
        show=flash==0 or(flash//100)%2==0
        if show: draw_car(screen,int(px),int(py),ci)
 
        pygame.draw.rect(screen,(0,0,0),(0,0,SW,46))
        screen.blit(FS.render(f"Score:{score}  Coins:{coins}",True,YELLOW),(6,6))
        screen.blit(FS.render(f"{int(dist)}/{FINISH}m",True,WHITE),(SW//2-45,6))
        for i in range(lives): pygame.draw.circle(screen,RED,(SW-15-i*20,14),7)
        if shield: screen.blit(FT.render("SHIELD",True,BLUE),(SW-60,28))
        if apu=="NITRO":
            rem=max(0,(nitro_end-pygame.time.get_ticks())/1000)
            pygame.draw.rect(screen,ORANGE,(4,SH-26,SW-8,20),border_radius=5)
            screen.blit(FT.render(f"NITRO {rem:.1f}s",True,WHITE),(10,SH-24))
 
        pygame.display.flip()
 
def main():
    cfg={"sound":True,"car":0,"diff":"Normal"}; pname=""
    while True:
        if sc_menu(cfg)=="play":
            if not pname: pname=sc_name()
            r="retry"
            while r=="retry": r=run(pname,cfg)
 
main()