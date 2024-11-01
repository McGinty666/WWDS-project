import tkinter as tk

class MapWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Map Window")
        
        # Define points with dummy coordinates
        self.point1 = (350000, 150000)
        self.point2 = (350500, 150500)
        
        # Initial coordinates for the draw box around the points
        self.left_easting = min(self.point1[0], self.point2[0])
        self.right_easting = self.left_easting + 1000
        self.top_northing = max(self.point1[1], self.point2[1]) + 1000
        self.bottom_northing = self.top_northing - 1000
        
        self.left_easting_bb = self.point1[0]
        self.right_easting_bb = self.point1[0]+1000
        self.top_northing_bb = self.point1[1]
        self.bottom_northing_bb = self.point1[1]+1000
        # Create canvas
        self.canvas = tk.Canvas(root, width=500, height=500, bg="white")
        self.canvas.grid(row=1, column=1, rowspan=3, columnspan=3)
        
        # Create a frame for the coordinates display
        self.coord_frame = tk.Frame(root)
        self.coord_frame.grid(row=1, column=4, rowspan=3)
        
        # Draw initial box and points
        self.draw_box()
        
        # Create buttons
        self.create_buttons()
        
        # Create labels for current coordinates
        self.create_labels()
    
    def draw_box(self):
        self.canvas.delete("all")
        
        # Draw the axes
        for i in range(0, 501, 50):
            self.canvas.create_line(i, 0, i, 500, fill="gray", dash=(2, 2))
            self.canvas.create_line(0, i, 500, i, fill="gray", dash=(2, 2))
            self.canvas.create_text(i, 10, text=f"{self.left_easting + i*20}", anchor="n")
            self.canvas.create_text(10, i, text=f"{self.top_northing - i*20}", anchor="w")
        
        # Draw the single 1000x1000 square within the blue box and display its coordinates
        x = self.left_easting_bb
        y = self.bottom_northing_bb
        self.canvas.create_rectangle((x - self.left_easting_bb) / 20,
                                     (self.top_northing_bb - (y + 1000)) / 20,
                                     ((x + 1000) - self.left_easting_bb) / 20,
                                     (self.top_northing_bb - y) / 20,
                                     outline="black", fill="blue", stipple="gray12")
        
        # Display coordinates of the square on the canvas
        self.canvas.create_text((x - self.left_easting_bb) / 20 + 5,
                                (self.top_northing - y) / 20 - 5,
                                text=f"({x}, {y})", anchor="nw", fill="white")
        self.canvas.create_text(((x + 1000) - self.left_easting_bb) / 20 - 5,
                                (self.top_northing - (y + 1000)) / 20 + 5,
                                text=f"({x + 1000}, {y + 1000})", anchor="se", fill="white")
        
        # Display coordinates of the square in the coord_frame
        tk.Label(self.coord_frame, text=f"({x}, {y})").grid(row=0, column=0)
        tk.Label(self.coord_frame, text=f"({x + 1000}, {y + 1000})").grid(row=0, column=1)
        
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
        
        # Add legend with coordinates of points
        self.canvas.create_rectangle(410, 458, 470, 494, outline="black", fill="white")
        self.canvas.create_oval(416, 464, 422, 470, outline="red", fill="red")
        self.canvas.create_text(426, 467, text=f"Point1: {self.point1}", anchor="w")
        self.canvas.create_oval(416, 476, 422, 482, outline="blue", fill="blue")
        self.canvas.create_text(426, 479, text=f"Point2: {self.point2}", anchor="w")
    
    def create_buttons(self):
        # Increase/Decrease right easting
        tk.Button(self.root, text="Increase Right Easting", command=self.increase_right_easting).grid(row=1, column=5)
        tk.Button(self.root, text="Decrease Right Easting", command=self.decrease_right_easting).grid(row=2, column=5)
        
        # Increase/Decrease left easting
        tk.Button(self.root, text="Increase Left Easting", command=self.increase_left_easting).grid(row=1, column=0)
        tk.Button(self.root, text="Decrease Left Easting", command=self.decrease_left_easting).grid(row=2, column=0)
        
        # Increase/Decrease top northing
        tk.Button(self.root, text="Increase Top Northing", command=self.increase_top_northing).grid(row=0, column=2)
        tk.Button(self.root, text="Decrease Top Northing", command=self.decrease_top_northing).grid(row=3, column=2)
        
        # Increase/Decrease bottom northing
        tk.Button(self.root, text="Increase Bottom Northing", command=self.increase_bottom_northing).grid(row=4, column=2)
        tk.Button(self.root, text="Decrease Bottom Northing", command=self.decrease_bottom_northing).grid(row=5, column=2)
    
    def create_labels(self):
        # Labels for current coordinates
        self.label_left_easting_bb = tk.Label(self.root, text=f"Left Easting: {self.left_easting}")
        self.label_left_easting_bb.grid(row=6, column=1)
        
        self.label_right_easting_bb = tk.Label(self.root, text=f"Right Easting: {self.right_easting}")
        self.label_right_easting_bb.grid(row=6, column=2)
        
        self.label_top_northing_bb = tk.Label(self.root, text=f"Top Northing: {self.top_northing}")
        self.label_top_northing_bb.grid(row=7, column=1)
        
        self.label_bottom_northing_bb = tk.Label(self.root, text=f"Bottom Northing: {self.bottom_northing}")
        self.label_bottom_northing_bb.grid(row=7, column=2)
    
    def update_labels(self):
        # Update labels with current coordinates
        self.label_left_easting_bb.config(text=f"Left Easting: {self.left_easting}")
        self.label_right_easting_bb.config(text=f"Right Easting: {self.right_easting}")
        self.label_top_northing_bb.config(text=f"Top Northing: {self.top_northing}")
        self.label_bottom_northing_bb.config(text=f"Bottom Northing: {self.bottom_northing}")
    

    def increase_right_easting(self):
        self.right_easting_bb += 1000
        self.draw_box()
        self.update_labels()
    
    def decrease_right_easting(self):
        if (self.right_easting_bb - self.left_easting_bb) > 1000:
            self.right_easting_bb -= 1000
            self.draw_box()
            self.update_labels()
    
    def increase_left_easting(self):
        self.left_easting_bb += 1000
        self.draw_box()
        self.update_labels()
    
    def decrease_left_easting(self):
        self.left_easting_bb -= 1000
        self.draw_box()
        self.update_labels()
    
    def increase_top_northing(self):
        self.top_northing_bb += 1000
        self.draw_box()
        self.update_labels()
    
    def decrease_top_northing(self):
        if (self.top_northing_bb - 1000) > (self.bottom_northing_bb + 1000):
            self.top_northing_bb -= 1000
            self.draw_box()
            self.update_labels()
    
    def increase_bottom_northing(self):
        if (self.bottom_northing_bb + 1000) < (self.top_northing_bb - 1000):
            self.bottom_northing_bb += 1000
            self.draw_box()
            self.update_labels()
    
    def decrease_bottom_northing(self):
        if (self.bottom_northing_bb - 1000) > 100000:
            self.bottom_northing_bb -= 1000
            self.draw_box()
            self.update_labels()
    

# Create the main window and run the application
root = tk.Tk()
app = MapWindow(root)
root.mainloop()
