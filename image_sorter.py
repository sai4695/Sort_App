import os
import shutil
from tkinter import Tk, Label, Button, filedialog, messagebox
from PIL import ImageTk, Image
import time


class ImageSorter:
    def __init__(self, master):
        self.master = master
        master.title("Image Sorter")

        self.master.geometry("800x600")  # Adjusted for a larger window size
        self.master.lift()
        self.master.attributes("-topmost", True)  # Attempt to make the window active
        self.master.after_idle(self.master.attributes, '-topmost', False)

        self.image_folder = ""
        self.current_image_index = 0
        self.image_files = []
        self.last_sort_time = 0
        self.debounce_interval = 0.25  # Interval for debounce (in seconds)
        self.undo_stack = []

        self.label_text = Label(master, text="Select a folder to start")
        self.label_text.pack()

        self.image_label = Label(master)
        self.image_label.pack()

        self.select_folder_button = Button(master, text="Select Folder", command=self.select_folder)
        self.select_folder_button.pack()

        master.bind("<Left>", self.sort_false_negative)
        master.bind("<Right>", self.sort_false_positive)

    def select_folder(self):
        self.image_folder = filedialog.askdirectory()
        if self.image_folder:
            self.image_files = [file for file in os.listdir(self.image_folder) if
                                file.lower().endswith((".png", ".jpg", ".jpeg"))]
            if self.image_files:
                self.create_sorting_folders()
                self.current_image_index = 0
                self.display_image()
            else:
                self.label_text.config(text="No image files found in the selected folder.")
        else:
            self.label_text.config(text="No folder selected. Please select a folder.")

    def create_sorting_folders(self):
        self.false_negative_folder = os.path.join(self.image_folder, "FN")
        self.false_positive_folder = os.path.join(self.image_folder, "FP")
        os.makedirs(self.false_negative_folder, exist_ok=True)
        os.makedirs(self.false_positive_folder, exist_ok=True)

    def display_image(self):
        if self.current_image_index < len(self.image_files):
            image_path = os.path.join(self.image_folder, self.image_files[self.current_image_index])
            image = Image.open(image_path)
            image.thumbnail((760, 560), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            self.image_label.configure(image=photo)
            self.image_label.image = photo
        else:
            self.image_label.configure(image='')
            self.label_text.config(text="No more images to sort.")

    def sort_false_negative(self, event):
        if self.current_image_index < len(self.image_files):
            self.debounce_sort(self.move_image_to_false_negative)

    def sort_false_positive(self, event):
        if self.current_image_index < len(self.image_files):
            self.debounce_sort(self.move_image_to_false_positive)

    def debounce_sort(self, sort_function):
        current_time = time.time()
        if current_time - self.last_sort_time >= self.debounce_interval:
            sort_function()
            self.last_sort_time = current_time
        else:
            if messagebox.askyesno("Rapid Sorting", "You are sorting images rapidly. Do you want to undo the last sort?"):
                self.undo_last_sort()

    def move_image_to_false_negative(self):
        self.move_image(self.false_negative_folder)

    def move_image_to_false_positive(self):
        self.move_image(self.false_positive_folder)

    def move_image(self, destination_folder):
        if self.current_image_index < len(self.image_files):
            image_file = self.image_files[self.current_image_index]
            src_path = os.path.join(self.image_folder, image_file)
            dst_path = os.path.join(destination_folder, image_file)
            shutil.move(src_path, dst_path)
            self.undo_stack.append((src_path, dst_path))
            self.current_image_index += 1
            self.display_image()

    def undo_last_sort(self):
        if self.undo_stack:
            src_path, dst_path = self.undo_stack.pop()
            shutil.move(dst_path, src_path)
            self.current_image_index -= 1
            self.display_image()

root = Tk()
app = ImageSorter(root)
root.mainloop()
