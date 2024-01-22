import pygame
import numpy as np
import random

from diagram import Diagram

from knot_functions import clean_k_arc, xco_arc, arc_xoco, xabo_xco
from knot_functions import circles_crd_cds, random_knot

pygame.init()

width = 960
aspect_ratio = 9/16
winsize = (width, round(width*aspect_ratio))
win = pygame.display.set_mode(winsize, pygame.RESIZABLE)
pygame.display.set_caption('Game')

pygame.scrap.init()
text_rect = pygame.Rect(0,0,0,0)
text_active = False
user_text = ''
base_font = pygame.font.Font(None, 0)

bg_color = (125, 125, 125)
white = (255, 255, 255)
black = (0, 0, 0)
red = (125, 25, 25)

smooth_l = Diagram()
arc = Diagram()
smooth_r = Diagram()

knot_buttons = [None, None, None]

xco_i = xco_arc(clean_k_arc('[[5,2],[1,3],[2,4],[3,5],[4,1]]'))

def new_knot(i):
    if i==0:
        Diagram.n -= 1
    elif i==2:
        Diagram.n += 1

    if Diagram.n>4:
        define_knot(random_knot(Diagram.n))
    else:
        Diagram.n+=1

def define_knot(xco):
    global k_xco, cross_rc, ab_crossings
    k_xco = xco
    cross_rc = np.argwhere(k_xco==3)
    ab_crossings=np.array([random.randint(0,1) for _ in range(len(cross_rc))])

    update_knots()

def update_knots():
    arc.xabo = k_xco  

    smooth_l.xabo = xabo_xco(k_xco, 4+ab_crossings)
    smooth_l.circles_crd_cds = circles_crd_cds(smooth_l.xabo)
    
    smooth_r.xabo = xabo_xco(k_xco, 5-ab_crossings)
    smooth_r.circles_crd_cds = circles_crd_cds(smooth_r.xabo)

    Diagram.n = k_xco.shape[0]

    window_resized()

def resize_grids(winsize):
    g_size, g_margin = winsize[0]/3, winsize[0]/24
    sq_size = g_size/Diagram.n
    g_coord_y = (winsize[1] - g_size)/2
    
    smooth_l.grid_size, smooth_r.grid_size = g_size, g_size
    smooth_l.sqr_size, smooth_r.sqr_size = sq_size, sq_size
    arc.grid_size, arc.sqr_size = g_size/2, sq_size/2
    
    smooth_l.grid_coords = (0+g_margin, g_coord_y)
    smooth_r.grid_coords = (winsize[0]-(g_size+g_margin), g_coord_y)
    arc.grid_coords = (g_size+2*g_margin, (winsize[1] - arc.grid_size)/2)

def resize_buttons(winsize):
    size = arc.grid_size/3
    x0, y = arc.grid_coords[0], arc.grid_coords[1]-size
    for i in range(3):
        x_i = x0 + size*i
        knot_buttons[i] = pygame.Rect(x_i, y, size, size)

def draw_buttons():
    k_b_border = int(np.ceil(knot_buttons[0].size[0]*.01))
    for i in range(3):
        pygame.draw.rect(win, white, knot_buttons[i])
        pygame.draw.rect(win, bg_color, knot_buttons[i], k_b_border)
        

def draw_texts():
    pygame.draw.rect(win, white, text_rect)
    text_border = round(pygame.display.get_window_size()[1] * 0.01)
    col = black if text_active else bg_color
    pygame.draw.rect(win, col, text_rect, text_border)

    text_surface = base_font.render(user_text, True, black)
    text_w, text_h = text_surface.get_rect().size
    text_pos = text_rect.centerx-text_w*.5, text_rect.centery-text_h*.5
    win.blit(text_surface, text_pos)
    
    k_coords = str(arc_xoco(k_xco)).replace('\n', '')
    text_surface = base_font.render(k_coords, True, black)
    text_w, text_h = text_surface.get_rect().size
    text_posx = text_rect.centerx-text_w*.5
    text_posy = text_rect.centery-text_h*.5-text_rect.h
    win.blit(text_surface, (text_posx, text_posy))


def draw_window():
    win.fill(bg_color)

    smooth_l.draw_grid(win)
    arc.draw_grid(win)
    smooth_r.draw_grid(win)

    arc.draw_arc(win)
    smooth_r.draw_smooth(win)
    smooth_l.draw_smooth(win)

    #smooth_r.test_draw(win)

    draw_texts()
    draw_buttons()
    
    pygame.display.update()


def window_resized():
    global base_font
    
    winwidth = pygame.display.get_window_size()[0]
    if winwidth != pygame.display.get_desktop_sizes()[0][0]:
        winsize = (winwidth, winwidth*aspect_ratio)
        pygame.display.set_mode(winsize, pygame.RESIZABLE)

    winsize = pygame.display.get_window_size()
    resize_grids(winsize)
    resize_buttons(winsize)

    text_rect.size = (winsize[0], winsize[1]*.08)
    text_rect.topleft = (0, winsize[1]-text_rect.size[1])

    base_font = pygame.font.Font(None, int(text_rect.size[1]*.8))

    
def mouse_clicked(pos):
    global text_active
    
    if text_rect.collidepoint(pos):
        text_active = True
    else:
        text_active = False

    l_gs, r_gs = smooth_l.grid_size, smooth_r.grid_size
    left = pygame.Rect(smooth_l.grid_coords, (l_gs,l_gs))
    right = pygame.Rect(smooth_r.grid_coords, (r_gs,r_gs))
    if left.collidepoint(pos) or right.collidepoint(pos):
        if left.collidepoint(pos):
            click_rc = smooth_l.grid_r_c(pos)
        elif right.collidepoint(pos):
            click_rc = smooth_r.grid_r_c(pos)

        if k_xco[click_rc]==3:
            click_cross_n = np.where(np.all(cross_rc==click_rc, axis=1))[0][0]
            ab_crossings[click_cross_n] = (ab_crossings[click_cross_n]+1)%2
            update_knots()

    for i in range(3):
        if knot_buttons[i].collidepoint(pos):
            new_knot(i)
    

def main():
    global user_text
    
    define_knot(xco_i)
    
    run = True
    while run:
        draw_window()
        
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button==1:
                    mouse_clicked(event.pos)
                    
            elif event.type == pygame.KEYDOWN:
                if text_active:
                    if event.mod & pygame.KMOD_CTRL and event.key==pygame.K_v:
                        clipboard = pygame.scrap.get(pygame.SCRAP_TEXT)
                        user_text += clipboard.decode('utf-8')[:-1]
                    elif event.key == pygame.K_BACKSPACE:
                        user_text = user_text[:-1]
                    elif event.key == pygame.K_DELETE:
                        user_text = ''
                    elif event.key == pygame.K_RETURN:
                        if user_text!='':
                            k_arc = clean_k_arc(user_text)
                            if type(k_arc)!=type(None):
                                define_knot(xco_arc(k_arc))
                                user_text = ''
                    else:
                        user_text += event.unicode
                        
            elif event.type == pygame.WINDOWRESIZED:
                window_resized()
            elif event.type == pygame.QUIT:
                run = False
                
    pygame.quit()


if __name__=='__main__':
    main()
