# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 23:14:39 2024

@author: RMCGINT
"""

import tkinter as tk
 

class MapWindow:
    def __init__(self, parent, app):
        self.root = parent
        self.app = app
        self.root.title("Map Window")

        # Create a main frame to hold all widgets
        main_frame = tk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Define points with dummy coordinates
        self.point1 = (350500, 150500)
        self.site_coord = (350000, 150000)
        #self.point2 = self.site_coord
        self.site_id = 19505

        # Define points with dummy coordinates
        self.rounded_x = app.rounded_x
        self.rounded_y = app.rounded_y
        self.point1 = (self.rounded_x, self.rounded_y)
        self.actual_x = app.actual_x
        self.actual_y = app.actual_y
        self.site_coord = (self.actual_x, self.actual_y)
        self.point2 = self.site_coord
        self.site_id = app.site_id

        # Initial coordinates for the draw box around the points
        self.left_easting = self.point1[0] - 5000
        self.right_easting = self.left_easting + 5000
        self.top_northing = self.point1[1] -5000
        self.bottom_northing = self.top_northing - 5000

        self.left_easting_bb = self.point1[0]
        self.right_easting_bb = self.point1[0] + 1000
        self.top_northing_bb = self.point1[1] + 1000
        self.bottom_northing_bb = self.point1[1]

        # Canvas for map display
        self.canvas = tk.Canvas(main_frame, width=500, height=500, bg="white")
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Create a frame for the coordinates display
        self.coord_frame = tk.Frame(self.root)
        self.coord_frame.grid(row=1, column=4, rowspan=3)

        # Draw initial box and points
        self.draw_box()

        # Create buttons
        self.create_buttons()

        # Create labels for current coordinates
        self.create_labels()

        # Configure the root window to expand to fit the content
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
    
        # Create the "Set Rainfall Extents" button
        set_extents_button = tk.Button(main_frame, text="Set Rainfall Extents", command=self.set_rainfall_extents)
        set_extents_button.grid(row=1, column=0, padx=10, pady=10)
        
    
    def draw_box(self):
        self.canvas.delete("all")
        
        # Draw the axes
        for i in range(0, 501, 50):
            self.canvas.create_line(i, 0, i, 500, fill="gray", dash=(2, 2))
            self.canvas.create_line(0, i, 500, i, fill="gray", dash=(2, 2))
            self.canvas.create_text(i, 10, text=f"{self.left_easting + i*20}", anchor="n")
            self.canvas.create_text(10, i, text=f"{self.top_northing - i*20}", anchor="w")
        
        # Draw the blue box and display its coordinates
        x = self.left_easting_bb
        y = self.bottom_northing_bb
        self.canvas.create_rectangle((x - self.left_easting) / 20,
                                     (self.top_northing - (y + (self.top_northing_bb - y))) / 20,
                                     ((self.right_easting_bb) - self.left_easting) / 20,
                                     (self.top_northing - y) / 20,
                                     outline="black", fill="blue", stipple="gray12")
        
        # Display coordinates of the blue box on the canvas
        self.canvas.create_text((x - self.left_easting_bb) / 20 + 5,
                                (self.top_northing_bb - y) / 20 - 5,
                                text=f"({x}, {y})", anchor="nw", fill="white")
        self.canvas.create_text(((self.right_easting_bb) - self.left_easting_bb) / 20 - 5,
                                (self.top_northing_bb - (y + (self.top_northing_bb - y))) / 20 + 5,
                                text=f"({self.right_easting_bb}, {self.top_northing_bb})", anchor="sw", fill="white")
        
        # Display coordinates of the blue box in the coord_frame
        tk.Label(self.coord_frame, text=f"({x}, {y})").grid(row=0, column=0)
        tk.Label(self.coord_frame, text=f"({self.right_easting_bb}, {self.top_northing_bb})").grid(row=0, column=1)
        
        # Draw the points
        self.canvas.create_oval((self.point1[0] - self.left_easting) / 20 - 5,
                                (self.top_northing - self.point1[1]) / 20 - 5,
                                (self.point1[0] - self.left_easting) / 20 + 5,
                                (self.top_northing - self.point1[1]) / 20 + 5,
                                outline="red", fill="red", tags="point1")
        
        self.canvas.create_oval((self.point2[0] - self.left_easting) / 20 - 5,
                                (self.top_northing - self.point2[1]) / 20 - 5,
                                (self.point2[0] - self.left_easting) / 20 + 5,
                                (self.top_northing - self.point2[1]) / 20 + 5,
                                outline="blue", fill="blue", tags="point2")
        
        # Add legend with coordinates of points on the left side and make it longer
        legend_x_start = 10
        legend_y_start = 420
        legend_width = legend_x_start + 200
        legend_height = legend_y_start + 60
    
        self.canvas.create_rectangle(legend_x_start, legend_y_start, legend_width, legend_height, outline="black", fill="white")
        self.canvas.create_oval(legend_x_start + 6, legend_y_start + 6, legend_x_start + 12, legend_y_start + 12, outline="red", fill="red")
        self.canvas.create_text(legend_x_start + 16, legend_y_start + 9, text=f"near_corner: {self.point1}", anchor="w")
        self.canvas.create_oval(legend_x_start + 6, legend_y_start + 22, legend_x_start + 12, legend_y_start + 28, outline="blue", fill="blue")
        self.canvas.create_text(legend_x_start + 16, legend_y_start + 25, text=f"Site_ID{self.site_id}: {self.point2}", anchor="w")
    
    def create_buttons(self):
        # Increase/Decrease right easting
        tk.Button(self.root, text=">Increase Right Easting>", command=self.increase_right_easting).grid(row=1, column=5)
        tk.Button(self.root, text="<Decrease Right Easting<", command=self.decrease_right_easting).grid(row=2, column=5)
        
        # Increase/Decrease left easting
        tk.Button(self.root, text=">Increase Left Easting>", command=self.increase_left_easting).grid(row=1, column=0)
        tk.Button(self.root, text="<Decrease Left Easting<", command=self.decrease_left_easting).grid(row=2, column=0)
        
        # Increase/Decrease top northing
        tk.Button(self.root, text="^Increase Top Northing^", command=self.increase_top_northing).grid(row=0, column=2)
        tk.Button(self.root, text="VDecrease Top NorthingV", command=self.decrease_top_northing).grid(row=0, column=3)
        
        # Increase/Decrease bottom northing
        tk.Button(self.root, text="^Increase Bottom Northing^", command=self.increase_bottom_northing).grid(row=4, column=2)
        tk.Button(self.root, text="VDecrease Bottom NorthingV", command=self.decrease_bottom_northing).grid(row=5, column=2)

    
    def create_labels(self):
        # Labels for current coordinates
        self.label_left_easting_bb = tk.Label(self.root, text=f"Left Easting: {self.left_easting_bb}")
        self.label_left_easting_bb.grid(row=6, column=1)
        
        self.label_right_easting_bb = tk.Label(self.root, text=f"Right Easting: {self.right_easting_bb}")
        self.label_right_easting_bb.grid(row=6, column=2)
        
        self.label_top_northing_bb = tk.Label(self.root, text=f"Top Northing: {self.top_northing_bb}")
        self.label_top_northing_bb.grid(row=7, column=1)
        
        self.label_bottom_northing_bb = tk.Label(self.root, text=f"Bottom Northing: {self.bottom_northing_bb}")
        self.label_bottom_northing_bb.grid(row=7, column=2)
    
    def update_labels(self):
        # Update labels with current coordinates
        self.label_left_easting_bb.config(text=f"Left Easting: {self.left_easting_bb}")
        self.label_right_easting_bb.config(text=f"Right Easting: {self.right_easting_bb}")
        self.label_top_northing_bb.config(text=f"Top Northing: {self.top_northing_bb}")
        self.label_bottom_northing_bb.config(text=f"Bottom Northing: {self.bottom_northing_bb}")
    
    def increase_right_easting(self):
        self.right_easting_bb += 1000
        self.right_easting = self.right_easting_bb + 5000
        self.draw_box()
        self.update_labels()
    
    def decrease_right_easting(self):
        self.right_easting_bb -= 1000
        self.right_easting = self.right_easting_bb + 5000
        self.draw_box()
        self.update_labels()
    
    def increase_left_easting(self):
        self.left_easting_bb += 1000
        self.left_easting = self.left_easting_bb - 5000
        self.draw_box()
        self.update_labels()
    
    def decrease_left_easting(self):
        self.left_easting_bb -= 1000
        self.left_easting = self.left_easting_bb - 5000
        self.draw_box()
        self.update_labels()
    
    def increase_top_northing(self):
        self.top_northing_bb += 1000
        self.top_northing = self.top_northing_bb + 5000
        self.draw_box()
        self.update_labels()
    
    def decrease_top_northing(self):
        self.top_northing_bb -= 1000
        self.top_northing = self.top_northing_bb + 5000
        self.draw_box()
        self.update_labels()
    
    def increase_bottom_northing(self):
        self.bottom_northing_bb += 1000
        self.bottom_northing = self.bottom_northing_bb - 5000
        self.draw_box()
        self.update_labels()
    
    def decrease_bottom_northing(self):
        self.bottom_northing_bb -= 1000
        self.bottom_northing = self.bottom_northing_bb - 5000
        self.draw_box()
        self.update_labels()

    def set_rainfall_extents(self):
        # Make the variables available in the parent class
        self.root.destroy()    
        # Assuming 'app' is the parent class instance
        self.app.right_easting_bb = self.right_easting_bb
        self.app.left_easting_bb = self.left_easting_bb
        self.app.top_northing_bb = self.top_northing_bb
        self.app.bottom_northing_bb = self.bottom_northing_bb

