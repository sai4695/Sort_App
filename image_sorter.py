import os
import shutil
from tkinter import Tk, Label, Button, filedialog, Frame, messagebox
from PIL import ImageTk, Image


class ImageSorter:
    def __init__(self, master):
        self.master = master
        master.title("Image Sorter")
        self.master.geometry("800x600")

        self.image_folder = ""
        self.current_image_index = 0
        self.image_files = []
        self.history = []  # To handle undo functionality

        self.label_text = Label(master, text="Select a folder to start")
        self.label_text.pack()

        self.image_label = Label(master)
        self.image_label.pack()

        self.select_folder_button = Button(master, text="Select Folder", command=self.select_folder)
        self.select_folder_button.pack()

        # Frame for buttons including undo button
        self.button_frame = Frame(master)
        self.button_frame.pack()

        # Undo button
        self.undo_button = Button(self.button_frame, text="Undo", command=self.undo_last_action)
        self.undo_button.pack(side='left', padx=5)

        # Labels for counts
        self.count_labels = {}

    def select_folder(self):
        self.image_folder = filedialog.askdirectory()
        if not self.image_folder:
            self.label_text.config(text="No folder selected. Please select a folder.")
            return

        if self.image_folder.endswith('Include') or self.image_folder.endswith('Exclude'):
            self.image_files = [file for file in os.listdir(self.image_folder) if
                                file.lower().endswith((".png", ".jpg", ".jpeg"))]
            if self.image_files:
                self.create_sorting_folders(self.image_folder.endswith('Include'))
                self.current_image_index = 0
                self.display_image()
            else:
                self.label_text.config(text="No image files found in the selected folder.")
        else:
            messagebox.showinfo("Notification", "Please select either 'Include' or 'Exclude' folder.")

    def create_sorting_folders(self, is_include):
        categories = ['TP', 'FP'] if is_include else ['TN', 'FN']
        folder_exists_flag = False

        # Clear existing buttons and labels before recreating them
        for widget in self.button_frame.winfo_children():
            if widget != self.undo_button:
                widget.destroy()

        for category in categories:
            folder_path = os.path.join(self.image_folder, category)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path, exist_ok=True)
            else:
                folder_exists_flag = True

            initial_count = len(
                [name for name in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, name))])
            self.count_labels[category] = Label(self.button_frame, text=f"{category}: {initial_count}")
            self.count_labels[category].pack(side='left', padx=10)

        if folder_exists_flag:
            messagebox.showinfo("Notification", "Sorting folders already exist. Current counts are:")

        self.create_sort_buttons(categories)

    def create_sort_buttons(self, categories):
        for category in categories:
            Button(self.button_frame, text=category, command=lambda c=category: self.sort_image(c)).pack(side='left',
                                                                                                         padx=5)

    def sort_image(self, category):
        if self.current_image_index < len(self.image_files):
            destination_folder = os.path.join(self.image_folder, category)
            self.move_image(destination_folder)
            self.update_count(category)
            # Store the move in history
            self.history.append((self.image_folder, destination_folder, self.image_files[self.current_image_index - 1]))

    def move_image(self, destination_folder):
        if self.current_image_index < len(self.image_files):
            image_file = self.image_files[self.current_image_index]
            src_path = os.path.join(self.image_folder, image_file)
            dst_path = os.path.join(destination_folder, image_file)
            shutil.move(src_path, dst_path)
            self.current_image_index += 1
            self.display_image()

    def update_count(self, category):
        # Increment the count for the specific category and update the label
        current_count = int(self.count_labels[category].cget("text").split(": ")[1])
        current_count += 1
        self.count_labels[category].config(text=f"{category}: {current_count}")

        if self.current_image_index >= len(self.image_files):
            self.label_text.config(text="All images have been sorted.")

    def undo_last_action(self):
        if not self.history:
            messagebox.showinfo("Undo", "No move to undo.")
            return
        # Get the last move details
        original_folder, moved_folder, file_name = self.history.pop()
        src_path = os.path.join(moved_folder, file_name)
        dst_path = os.path.join(original_folder, file_name)
        shutil.move(src_path, dst_path)
        self.current_image_index -= 1
        self.display_image()
        self.update_count_for_undo(moved_folder)

    def update_count_for_undo(self, moved_folder):
        category = os.path.basename(moved_folder)
        current_count = int(self.count_labels[category].cget("text").split(": ")[1]) - 1
        self.count_labels[category].config(text=f"{category}: {current_count}")

    def display_image(self):
        if self.current_image_index < len(self.image_files):
            image_path = os.path.join(self.image_folder, self.image_files[self.current_image_index])
            image = Image.open(image_path)
            image.thumbnail((760, 560), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(image)
            self.image_label.configure(image=photo)
            self.image_label.image = photo
        else:
            self.image_label.configure(image='')
            total_count = sum(
                len(os.listdir(os.path.join(self.image_folder, category))) for category in self.count_labels)
            self.label_text.config(text=f"No more images! Total sorted: {total_count}")


root = Tk()
app = ImageSorter(root)
root.mainloop()
