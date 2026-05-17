import json
import os
import pygame
import random
import tkinter
import time
from PIL import Image, ImageTk


WIDTH = 800
HEIGHT = 800
pygame.init()
screen = None
screen1 = None
all_colors = [(r, g, b) for r in range(0, 256, 32) for g in range(0, 256, 32) for b in range(0, 256, 64)]
used_colors = set()
attempt = 1
image_list = []
cluster_color_map = {}

x_margins = (-5000, 5000)
y_margins = (-5000, 5000)


def display_image(frame_pos, label, frame_list):
    img = Image.open(frame_list[int(frame_pos) - 1])
    tk_img = ImageTk.PhotoImage(img)
    label.config(image=tk_img)
    label.image = tk_img

def display_slider(frame_list):
    root = tkinter.Tk()
    root.title(f"Clusterization results")
    root.geometry(f"{WIDTH}x{HEIGHT}")
    
    img = Image.open(frame_list[0])
    tk_img = ImageTk.PhotoImage(img)
    label = tkinter.Label(root, image = tk_img)
    
    slider = tkinter.Scale(root, from_= 1, to = len(frame_list), orient = "horizontal", command = lambda frame_pos: display_image(frame_pos, label, frame_list))
    

    label.pack(side = "top", expand = True)
    slider.pack(side = "bottom", fill = "x")

    root.mainloop()

def illustrate(pr_points):
    global used_colors, attempt, image_list, cluster_color_map
    used_colors_in_frame = set()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    screen.fill((255, 255, 255))
    # clusters = [cr_info_global[cluster_name] for cluster_name in list(cr_info_global.keys())]
    
    for name, cluster in cr_info_global.items(): # Iterate over names and clusters
        color = None
        
        # 1. Check persistence: Has this cluster name been seen and colored before?
        if name in cluster_color_map:
            color = cluster_color_map[name]
        
        # 2. Check for new clusters OR if the color was a temporary color (attempt 1)
        if color is None:
            # Get a new, unused color for this new cluster
            color = get_color(used_colors_in_frame)
            
            # 3. Store color permanently for this cluster name
            cluster_color_map[name] = color
            
        # 4. Mark this color as used in the current frame
        used_colors_in_frame.add(color)
        
        points = cluster[1]
        for p in range(len(points)):
            x, y = pr_points[points[p]]
            
            x = int((x - x_margins[0]) / (x_margins[1] - x_margins[0]) * WIDTH)
            y = int((y - y_margins[0]) / (y_margins[1] - y_margins[0]) * HEIGHT)
            y = HEIGHT - y
            
            pygame.draw.circle(screen, color, (x, y), 5)
    pygame.display.flip()
    pygame.image.save(screen, f"frame_{attempt}.png")
    image_list.append(f"frame_{attempt}.png")
    attempt += 1

def get_color(used_colors_in_frame):
    global all_colors
    
    # Filter out colors used in this frame
    available = [c for c in all_colors if c not in used_colors_in_frame]
    
    if not available:
        # If all 256 colors are used in the current frame, we must reuse one.
        # This only happens if you have > 256 final clusters. 
        # For simplicity and to prevent the ValueError crash, we'll reuse a random color.
        print("Warning: All unique colors exhausted for the current frame. Reusing colors.")
        return random.choice(all_colors) 
        
    color = random.choice(available)
    return color

def render_map(pr_points):
    screen1 = pygame.display.set_mode((WIDTH, HEIGHT))
    screen1.fill((255, 255, 255))
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        for i in range(len(pr_points)):
            point = pr_points[i]

            # Scale x and y to screen
            x = int((point[0] - x_margins[0]) / (x_margins[1] - x_margins[0]) * WIDTH)
            y = int((point[1] - y_margins[0]) / (y_margins[1] - y_margins[0]) * HEIGHT)
            y = HEIGHT - y
            
            pygame.draw.circle(screen1, (0, 0, 0), (x, y), 4)
        pygame.display.flip()

def append_new(cr_info):
    global cr_info_global
    cig_keys = list(cr_info_global.keys())
    if(len(cig_keys) == 0):
        cr_info_global = cr_info
        return
    cif_keys = list(cr_info.keys())
    for cr in cig_keys:
        if(cr in cif_keys):
            cr_info[cr][0][3] = cr_info_global[cr][0][3]
    cr_info_global = cr_info


def illustrate_succession(cr_infol, pr_points):
    global cr_info_global
    for cr_info in cr_infol:
        # append_new(cr_info)
        cr_info_global = cr_info
        illustrate(pr_points)

pr_points = None
with open("pr_points.json", "r") as file:
    pr_points = json.load(file)
print("Loaded pr_points!")
cr_info_global = {}
cr_infol = []
cr_infos = None
ctr = 0
while True:
    try:
        with open(f"cr_info{ctr}.json", "r") as file:
            cr_infos = json.load(file)
            cr_infol.append(cr_infos)
    except FileNotFoundError:
        break    
    ctr += 1
print("Loaded cr_infos!")
    
        
render_map(pr_points)
illustrate_succession(cr_infol, pr_points)
display_slider(image_list)
