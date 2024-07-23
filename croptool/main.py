import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageOps
import os


class croptool:
    def __init__(self) -> None:
        # init window
        self.root = tk.Tk()
        self.root.title("Image Viewer")
        self.canvas = tk.Canvas(self.root)
        self.canvas.pack(fill = "both", expand = True)

        # fields
        self.is_draw = False
        self.is_magnify = False
        self.input_paths = []
        self.output_path = ""
        self.x1, self.x2, self.y1, self.y2 = 0, 0, 0, 0
        self.image_idx = 0 
        self.imagex = 0
        self.imagey = 0
        self.pil_image = None
        self.tk_image = None
        self.resized_image = None
        self.magnify_window = None
        self.magnify_canvas = None
        self.magnified_image = None
        self.magnified_tk_image = None
        

        self.PADDING_FACTOR = 0.9
        self.ZOOM_FACTOR = 0.20
        # tracking user input
        self.canvas.bind('<Motion>', self.motion)
        self.canvas.bind('<Button-1>', self.toggle_draw)
        # self.canvas.bind('<MouseWheel>', self.zoom)
        self.canvas.bind('<ButtonPress-2>', lambda event: self.canvas.scan_mark(event.x, event.y))
        self.canvas.bind("<B2-Motion>", lambda event: self.canvas.scan_dragto(event.x, event.y, gain=1))

        self.root.bind('<Control-o>', self.get_input_paths)
        self.root.bind('<Control-s>', self.get_output_path)
        self.root.bind('<Return>', self.crop)
        
        self.root.bind('<Left>', self.before)
        self.root.bind('<Right>', self.next)

        self.root.bind('<m>', self.magnify_toggle)

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
        if self.is_magnify:
            self.magnify_canvas.delete("all")
            mousex = self.canvas.canvasx(event.x)
            mousey = self.canvas.canvasy(event.y)
            
            offsetx = mousex - self.canvas.canvasx(self.imagex)
            offsety = mousey - self.canvas.canvasy(self.imagey)

            x = (offsetx / self.resized_image.width) * self.pil_image.width
            y = (offsety / self.resized_image.height) * self.pil_image.height
           
            # some black magic to find a square

            padding_pixels = ((self.pil_image.width + self.pil_image.height) / 2) * self.ZOOM_FACTOR

            x1 = max(x - padding_pixels, 0)
            y1 = max(y - padding_pixels, 0)
            x2 = min(x + padding_pixels, self.pil_image.width)
            y2 = min(y + padding_pixels, self.pil_image.height)

            self.magnified_image = self.pil_image.crop((x1, y1, x2, y2))
            self.magnified_tk_image = ImageTk.PhotoImage(self.magnified_image)
            magnified_canvas_width = self.magnify_canvas.winfo_width()
            magnified_canvas_height = self.magnify_canvas.winfo_height()
            
            magnified_image_x = (magnified_canvas_width - self.magnified_tk_image.width()) / 2
            magnified_image_y = (magnified_canvas_height - self.magnified_tk_image.height()) / 2

            self.magnify_canvas.create_image(magnified_image_x, magnified_image_y, anchor=tk.NW, image=self.magnified_tk_image)
            self.magnify_canvas.update()
            self.magnify_canvas.pack()
            



    def crop(self, event: tk.Event):
        if self.can_crop():
            image_name = self.input_paths[self.image_idx].split('/')[-1]
            self.pil_image.crop(self.find_image_coord()).save(
                os.path.join(self.output_path, 'cropped' + image_name))
            self.next(None)
        else:
            self.error_thrower("can't crop right now, cant crop during drawing or if there is no output file")

    def find_image_coord(self): # convert from canvas coord to image coord for crop
        # covert to crop coordinates
        x1 = self.canvas.canvasx(min(self.x1, self.x2))
        y1 = self.canvas.canvasy(min(self.y1, self.y2))
        x2 = self.canvas.canvasx(max(self.x1, self.x2)) 
        y2 = self.canvas.canvasy(max(self.y1, self.y2))
        delta_x = x2 - x1
        delta_y = y2 - y1
        offset_x = x1 - self.imagex
        offset_y = y1 - self.imagey

        # scale back up to originial image
        
        return (
            (offset_x / self.resized_image.width) * self.pil_image.width,
            (offset_y / self.resized_image.height) * self.pil_image.height,
            ((offset_x + delta_x) / self.resized_image.width) * self.pil_image.width, 
            ((offset_y + delta_y) / self.resized_image.height) * self.pil_image.height)
        

        
    def load_image(self, idx: int):
        self.canvas.delete("all")
        path = self.input_paths[idx]
        self.root.title(path)
        self.pil_image = Image.open(path)
        # self.resized_image = ImageOps.contain(self.pil_image, ((int(self.PADDING_FACTOR * self.root.winfo_screenwidth()), int(self.PADDING_FACTOR * self.root.winfo_screenheight()))))
        resize_factor = max((self.pil_image.width / self.root.winfo_screenwidth()), (self.pil_image.height / self.root.winfo_height()))
        self.resized_image = self.pil_image.resize((int((self.pil_image.width / resize_factor) * self.PADDING_FACTOR), int((self.pil_image.height / resize_factor) * self.PADDING_FACTOR)))
        self.tk_image = ImageTk.PhotoImage(self.resized_image)

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        img_width, img_height = self.tk_image.width(), self.tk_image.height()
        self.imagex = (canvas_width - img_width) / 2
        self.imagey = (canvas_height - img_height) / 2
        self.canvas.create_image(self.imagex, self.imagey, anchor=tk.NW, image=self.tk_image)
        self.canvas.update()
        # self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
          
   
    def get_input_paths(self, event: tk.Event):
        self.input_paths = list(filedialog.askopenfilenames()) # array btw
        self.load_image(0)

    def get_output_path(self, event: tk.Event):
        self.output_path = filedialog.askdirectory()

    def next(self, event: tk.Event):
        if self.image_idx < len(self.input_paths) - 1:
            self.image_idx += 1
            self.load_image(self.image_idx)
        else:
            self.error_thrower('no next image')

    def before(self, event: tk.Event):
        if self.image_idx > 0:
            self.image_idx -= 1
            self.load_image(self.image_idx)
        else:
            self.error_thrower('no previous image')
    def can_crop(self) -> bool:
        return bool(self.output_path) and not self.is_draw 
    

    def error_thrower(self, error_message: str):
        error_window = tk.Toplevel(self.root)    
        tk.Label(error_window, text = error_message).pack()
        tk.Button(error_window, text = 'Ok', command = error_window.destroy).pack()

    def magnify_toggle(self, event: tk.Event):
        ZOOM_FACTOR = 0.10
        if not self.is_magnify:
            self.magnify_window = tk.Toplevel(self.root)
            self.magnify_canvas = tk.Canvas(self.magnify_window,)
            self.is_magnify = True
        else:
            self.magnify_window.destroy()
            self.is_magnify = False


            
        




croptool()