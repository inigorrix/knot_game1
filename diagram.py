import numpy as np
import pygame

bg_color = (200, 200, 200)
white = (255, 255, 255)
black = (0, 0, 0)
red = (125, 25, 25)

colors = [
    (0,0,255),
    (0,255,0),
    (255,0,0),
    (200,200,0),
    (255,0,255),
    (0,255,255)
    ]


class Diagram:
    n = 5

    def __init__(self):
        self.xabo = np.zeros((self.n, self.n), dtype=np.int8)
        self.grid_coords = (0, 0)
        self.grid_size = 0
        self.sqr_size = 0
        self.circles_crd_cds = []
        

    def draw_grid(self, win):
        gpx, gpy, gs = self.grid_coords[0], self.grid_coords[1], self.grid_size
        pygame.draw.rect(win, white, (gpx, gpy, gs, gs))

        x0, x1 = self.grid_coords[0], self.grid_coords[0]+self.grid_size
        y0, y1 = self.grid_coords[1], self.grid_coords[1]+self.grid_size        
        for i in range(1, self.n):
            px = self.grid_coords[0] + (self.grid_size*i/self.n)
            py = self.grid_coords[1] + (self.grid_size*i/self.n)
            pygame.draw.line(win, bg_color, (px, y0), (px, y1))
            pygame.draw.line(win, bg_color, (x0, py), (x1, py))


    def draw_arc(self, win):
        w = int(np.ceil(.1*self.sqr_size))
        
        # draw vertical lines
        for i in range(self.n):
            col = self.xabo[:, i]
            y = np.where((col==1) | (col==2))[0]
            pos1, pos2 = self.sqr_pos(i, y[0]), self.sqr_pos(i, y[1])
            pygame.draw.line(win, black, pos1, pos2, w)

        # draw horizontal lines
        for j in range(self.n):
            row = self.xabo[j, :]
            x, x3 = np.where((row==1)|(row==2))[0], np.where(row==3)[0]
            pos1 = self.sqr_pos(x[0], j)
            gap = .25
            for k in x3:
                pos2 = self.sqr_pos(k-gap, j)
                pygame.draw.line(win, black, pos1, pos2, w)
                pos1 = self.sqr_pos(k+gap, j)
                
            pos2 = self.sqr_pos(x[1], j)
            pygame.draw.line(win, black, pos1, pos2, w)


    def draw_smooth(self, win):
        w = int(np.ceil(.1*self.sqr_size))
        c_coords, c_codes = self.circles_crd_cds

        for i in range(len(c_coords)):
            circle, codes = c_coords[i], c_codes[i]
            col = colors[i%len(colors)]
            for j in range(len(circle)):
                y0, y1 = circle[j-1][0], circle[j][0]
                x0, x1 = circle[j-1][1], circle[j][1]
                if codes[j-1]:
                    if y0==y1:
                        v = abs(y0-circle[j-2][0])/(y0-circle[j-2][0])
                        h = abs(x1-x0)/(x1-x0)
                        x0 += 0.5*h
                        if v==1 and h==1: q = 1
                        elif v==1 and h==-1: q = 2
                        elif v==-1 and h==1: q = 4
                        elif v==-1 and h==-1: q = 3
                        
                    elif x0==x1:
                        h = abs(x0-circle[j-2][1])/(x0-circle[j-2][1])
                        v = abs(y1-y0)/(y1-y0)
                        y0 += 0.5*v
                        if h==1 and v==1: q = 3
                        elif h==1 and v==-1: q = 2
                        elif h==-1 and v==1: q = 4
                        elif h==-1 and v==-1: q = 1
                        
                    
                if codes[j]:
                    if y0==y1: x1 -= 0.5*(abs(x1-x0)/(x1-x0))
                    elif x0==x1: y1 -= 0.5*(abs(y1-y0)/(y1-y0))
                
                pos1 = self.sqr_pos(x0, y0)
                pos2 = self.sqr_pos(x1, y1)
                pygame.draw.line(win, col, pos1, pos2, w)
                ###########
                
                if codes[j-1]:
                    # cambiar por draw_smooth_crossing
                    pos = self.sqr_pos(circle[j-1][1],circle[j-1][0])
                    draw_smooth_crossing(win, q, pos, self.sqr_size, col, w)
                    #draw90arc(win, pos1, self.sqr_size/2, q, col, w)
                    
        
            
    def sqr_pos(self, i, j):
        x = self.grid_coords[0] + (i+.5)*self.sqr_size
        y = self.grid_coords[1] + (j+.5)*self.sqr_size
        return (x, y)

    def grid_r_c(self, pos):
        gc, gs, n = self.grid_coords, self.grid_size, self.n
        column = int((pos[0]-gc[0])/(gs/n))
        row = int((pos[1]-gc[1])/(gs/n))
        return row, column
            
    def test_draw(self, win):
        winsize = pygame.display.get_window_size()
        draw_corner(win, (100, 100), 100, 1, black, 5)

        draw_smooth_crossing(win, 4, (200,200), 100, black, 5)





def draw90arc(win, pos, radius, quadrant, color, width, resolution=7):
    d_angle = np.pi*.5/resolution
    i_angle = np.pi*.5 * (quadrant-1)
    points = np.zeros((resolution+1, 2))
    for i in range(resolution+1):
        points[i, 0] = np.cos(i_angle + d_angle*i) * radius
        points[i, 1] = -np.sin(i_angle + d_angle*i) * radius

    points += pos

    pygame.draw.lines(win, color, False, points, width)


def draw_smooth_crossing(win, q, pos, size, col, w):
    radius = size * .5
    x = pos[0]+radius if q==1 or q==4 else pos[0]-radius
    y = pos[1]+radius if q==3 or q==4 else pos[1]-radius
    quadrants = [1,2,3,4]
    quadrant = quadrants[q-3]
    draw90arc(win, (x, y), radius, quadrant, col, w)
        
    '''
    x0, x1 = pos[0] - radius, pos[0] + radius
    y0, y1 = pos[1] - radius, pos[1] + radius
    if ab.lower()=='a':
        draw90arc(win, (x1, y0), radius, 3, col1, 5)
        draw90arc(win, (x0, y1), radius, 1, col2, 5)
    elif ab.lower()=='b':
        draw90arc(win, (x0, y0), radius, 4, col1, 5)
        draw90arc(win, (x1, y1), radius, 2, col2, 5)
    '''


def draw_corner(win, pos, size, quadrant, col, width):
    x, y = np.zeros(5), np.zeros(5)
    for i in range(5):
        x[i] = pos[0] + size*(-.5 + i/4)
        y[i] = pos[1] + size*(-.5 + i/4)
    if quadrant==1:
        pygame.draw.line(win, col, (x[2], y[0]), (x[2], y[1]), width)
        pygame.draw.line(win, col, (x[3], y[2]), (x[4], y[2]), width)
        draw90arc(win, (x[3], y[1]), size*.25, 3, col, width)
    elif quadrant==2:
        pygame.draw.line(win, col, (x[2], y[0]), (x[2], y[1]), width)
        pygame.draw.line(win, col, (x[0], y[2]), (x[1], y[2]), width)
        draw90arc(win, (x[1], y[1]), size*.25, 4, col, width)
    elif quadrant==3:
        pygame.draw.line(win, col, (x[2], y[3]), (x[2], y[4]), width)
        pygame.draw.line(win, col, (x[0], y[2]), (x[1], y[2]), width)
        draw90arc(win, (x[1], y[3]), size*.25, 1, col, width)
    elif quadrant==4:
        pygame.draw.line(win, col, (x[2], y[3]), (x[2], y[4]), width)
        pygame.draw.line(win, col, (x[3], y[2]), (x[4], y[2]), width)
        draw90arc(win, (x[3], y[3]), size*.25, 2, col, width)
