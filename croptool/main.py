import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
# binding
# file prompting
# box drawing

class croptool:
    def __init__(self) -> None:
        # init window
        self.root = tk.Tk()
        self.root.title("Image Viewer")
        self.canvas = tk.Canvas(self.root)
        self.canvas.pack(fill = "both", expand = True)

        # fields
        self.is_draw = False
        self.input_paths = []
        self.output_path = ""
        self.x1, self.x2, self.y1, self.y2 = 0, 0, 0, 0
        # tracking user input
        self.canvas.bind('<Motion>', self.motion)
        self.canvas.bind('<Button-1>', self.toggle_draw)
        self.canvas.bind('<MouseWheel>', self.zoom)
        self.canvas.bind('<ButtonPress-2>', lambda event: self.canvas.scan_mark(event.x, event.y))
        self.canvas.bind("<B2-Motion>", lambda event: self.canvas.scan_dragto(event.x, event.y, gain=1))

        self.root.bind('<Control-o>', self.get_input_paths)
        self.root.bind('<Control-s>', self.get_output_path)
        self.root.bind('<Return>', self.crop)
        

        # menu loop
        self.root.mainloop()

    
    def toggle_draw(self, event: tk.Event):
        print(event.x, event.y)
        if not self.is_draw:
            self.is_draw = True
            self.x1 = event.x
            self.y1 = event.y
        else:
            self.is_draw = False
            self.x2 = event.x
            self.y2 = event.y
                
            
        
    def motion(self, event: tk.Event):
        if self.is_draw:
            self.canvas.delete("crop_rect")
            self.canvas.create_rectangle(self.x1, self.y1, event.x, event.y, outline="red", tag="crop_rect")
            self.root.update()
        
    def crop(self, event: tk.Event):
        if self.can_crop():
            self.pil_image.crop((min(self.x1, self.x2), min(self.y1, self.y2), max(self.x1, self.x2), max(self.y1, self.y2))).show()
            self.load_next_image()
        else:
            print('throw some error')

        
    def load_next_image(self):
        self.canvas.delete("all")
        path = self.input_paths.pop(0)
        self.root.title(path)
        self.pil_image = Image.open(path)
        self.tk_image = ImageTk.PhotoImage(self.pil_image)
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        img_width, img_height = self.tk_image.width(), self.tk_image.height()
        x = (canvas_width - img_width) / 2
        y = (canvas_height - img_height) / 2
            
        self.canvas.create_image(x, y, anchor=tk.NW, image=self.tk_image)
        
        # self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        
        
   
    def get_input_paths(self, event: tk.Event):
        self.input_paths = list(filedialog.askopenfilenames()) # array btw
        self.load_next_image()

    def get_output_path(self, event: tk.Event):
        self.output_path = filedialog.askdirectory()

    
    def can_crop(self) -> bool:
        # return bool(self.input_paths) and bool(self.output_path) and not self.is_draw 
        return True
    

    def zoom(self,event):
        x = self.canvas.canvasx(event.x)
        
        y = self.canvas.canvasy(event.y)
        factor = 1.01 ** event.delta
        self.canvas.scale(tk.ALL, event.x, event.y, factor, factor)
    




croptool()