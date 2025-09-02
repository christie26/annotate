import os
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk, ImageEnhance
class ImageLabelingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Batch Image Labeling")
        self.root.geometry("1000x800")  # Initial window size
        # Initialize variables for car folder navigation
        self.parent_folder = None
        self.car_folders = []
        self.current_car_index = 0
        # Variables for image navigation within a car folder
        self.image_folder = None
        self.image_files = []
        self.current_image_index = 0
        self.label = None
                # Limit for image display size
        self.MAX_DISPLAY_WIDTH = 800
        self.MAX_DISPLAY_HEIGHT = 600
        # Settings for image display
        self.aliasing_var = BooleanVar(value=True)  # True: use LANCZOS filter, False: NEAREST
        self.contrast_factor = 1.0  # 1.0 means no contrast adjustment
        # Create Menubar with Settings (only aliasing is toggled via menu)
        self.menubar = Menu(root)
        settings_menu = Menu(self.menubar, tearoff=0)
        settings_menu.add_checkbutton(label="Enable Aliasing",
                                      variable=self.aliasing_var,
                                      command=self.on_setting_change)
        self.menubar.add_cascade(label="Settings", menu=settings_menu)
        self.root.config(menu=self.menubar)
        # Create UI components
        self.top_frame = Frame(root)
        self.top_frame.pack(pady=5, fill=X)
        # Display current car folder
        self.car_label = Label(self.top_frame, text="No car folder loaded")
        self.car_label.pack()
        # Frame for image display; it expands with window resizing
        self.label_frame = Frame(root)
        self.label_frame.pack(fill=BOTH, expand=True)
        self.image_label = Label(self.label_frame)
        self.image_label.pack(fill=BOTH, expand=True)
        # Control frame with buttons, label entry, and contrast slider
        self.control_frame = Frame(root)
        self.control_frame.pack(pady=5, fill=X)
        # Car navigation buttons
        self.prev_car_button = Button(self.control_frame, text="Previous Car", command=self.previous_car)
        self.prev_car_button.pack(side=LEFT, padx=5)
        self.next_car_button = Button(self.control_frame, text="Next Car", command=self.next_car)
        self.next_car_button.pack(side=LEFT, padx=5)
        # Image navigation buttons
        self.prev_button = Button(self.control_frame, text="Previous Image", command=self.previous_image)
        self.prev_button.pack(side=LEFT, padx=5)
        self.next_button = Button(self.control_frame, text="Next Image", command=self.next_image)
        self.next_button.pack(side=LEFT, padx=5)
        # Label entry and set label button
        self.label_entry = Entry(self.control_frame, width=20)
        self.label_entry.pack(side=LEFT, padx=5)
        self.label_button = Button(self.control_frame, text="Set Label", command=self.set_label)
        self.label_button.pack(side=LEFT, padx=5)
        self.load_button = Button(self.control_frame, text="Load Parent Folder", command=self.load_parent_folder)
        self.load_button.pack(side=LEFT, padx=5)
        # Contrast slider (cursor) for adjusting contrast
        self.contrast_scale = Scale(self.control_frame, from_=0.5, to=2.0, resolution=0.1,
                                    orient=HORIZONTAL, label="Contrast", command=self.on_contrast_change)
        self.contrast_scale.set(1.0)
        self.contrast_scale.pack(side=LEFT, padx=5)
        # Bind window resize event to update the image display dynamically
        self.root.bind("<Configure>", self.on_resize)
    def on_setting_change(self):
        """Called when aliasing setting is toggled."""
        self.show_image()
    def on_contrast_change(self, value):
        """Called when the contrast slider is moved."""
        self.contrast_factor = float(value)
        self.show_image()
    def on_resize(self, event):
        """Update the image display when the window is resized."""
        if self.image_files:
            self.show_image()
    def load_parent_folder(self):
        """Load the parent folder containing car subfolders."""
        self.parent_folder = filedialog.askdirectory(title="Select Parent Folder Containing Car Subfolders")
        if self.parent_folder:
            self.car_folders = [d for d in os.listdir(self.parent_folder)
                                if os.path.isdir(os.path.join(self.parent_folder, d))]
            if self.car_folders:
                self.current_car_index = 0
                self.load_car_folder()
            else:
                print("No subfolders found in the selected parent folder.")
        else:
            print("No folder selected.")
    def load_car_folder(self):
        """Load images from the current car folder and update display."""
        current_car = self.car_folders[self.current_car_index]
        self.image_folder = os.path.join(self.parent_folder, current_car)
        self.car_label.config(text=f"Current Car: {current_car}")
        self.image_files = [f for f in os.listdir(self.image_folder)
                            if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        self.current_image_index = 0
        if self.image_files:
            self.show_image()
        else:
            self.image_label.config(image='', text="No images in this folder.")
            print("No images found in the current car folder.")
    def show_image(self):
        """Display the current image with dynamic resizing and contrast adjustment."""
        if self.image_files and 0 <= self.current_image_index < len(self.image_files):
            image_path = os.path.join(self.image_folder, self.image_files[self.current_image_index])
            image = Image.open(image_path)
            # Get dynamic dimensions from the image_label frame
            label_width = self.image_label.winfo_width()
            label_height = self.image_label.winfo_height()
            max_width = min(label_width, self.MAX_DISPLAY_WIDTH)
            max_height = min(label_height, self.MAX_DISPLAY_HEIGHT)
            original_width, original_height = image.size
            width_ratio = max_width / original_width
            height_ratio = max_height / original_height
            scaling_factor = min(width_ratio, height_ratio)
            new_width = int(original_width * scaling_factor)
            new_height = int(original_height * scaling_factor)
            # Choose filter based on aliasing setting
            resample_filter = Image.LANCZOS if self.aliasing_var.get() else Image.NEAREST
            image = image.resize((new_width, new_height), resample_filter)
            # Apply contrast enhancement if necessary
            if self.contrast_factor != 1.0:
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(self.contrast_factor)
            photo = ImageTk.PhotoImage(image)
            self.image_label.config(image=photo)
            self.image_label.image = photo
        else:
            print("No image to display.")
    def set_label(self):
        """Rename the current vehicle folder and update a global CSV with the label."""
        self.label = self.label_entry.get().strip()
        if not self.label:
            print("Please enter a label.")
            return
        # Get the current folder name (e.g. "123" or "123_oldLabel")
        current_folder_name = os.path.basename(self.image_folder)
        if "_" in self.label:
            new_folder_name = self.label
        else:
            if "_" in current_folder_name:
                id_part = current_folder_name.split("_")[0]
                new_folder_name = f"{id_part}_{self.label}"
            else:
                new_folder_name = f"{current_folder_name}_{self.label}"
        new_folder_path = os.path.join(self.parent_folder, new_folder_name)
        if new_folder_name != current_folder_name:
            try:
                os.rename(self.image_folder, new_folder_path)
                print(f"Renamed folder to: {new_folder_name}")
                self.image_folder = new_folder_path
                self.car_label.config(text=f"Current Car: {new_folder_name}")
            except Exception as e:
                print(f"Error renaming folder: {e}")
        else:
            print("Folder name already matches the label format.")
        # Extract the vehicle ID (assumed to be the part before the underscore)
        vehicle_id = new_folder_name.split("_")[0]
        # Update global CSV file "labels.csv" with columns ID,LABEL
        csv_filename = os.path.join(self.parent_folder,"labels.csv")
        header = ["ID", "LABEL"]
        rows = []
        if os.path.exists(csv_filename):
            import csv
            with open(csv_filename, "r", newline="") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    rows.append(row)
        found = False
        for row in rows:
            if row["ID"] == vehicle_id:
                row["LABEL"] = self.label
                found = True
                break
        if not found:
            rows.append({"ID": vehicle_id, "LABEL": self.label})
        with open(csv_filename, "w", newline="") as csvfile:
            writer = __import__('csv').DictWriter(csvfile, fieldnames=header)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        print(f"Label updated in {csv_filename}")
    def next_image(self):
        if self.current_image_index < len(self.image_files) - 1:
            self.current_image_index += 1
            self.show_image()
        else:
            print("No more images in the folder.")
    def previous_image(self):
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.show_image()
        else:
            print("This is the first image; no previous image to display.")
    def next_car(self):
        if self.current_car_index < len(self.car_folders) - 1:
            self.current_car_index += 1
            self.load_car_folder()
        else:
            print("No more car folders.")
    def previous_car(self):
        if self.current_car_index > 0:
            self.current_car_index -= 1
            self.load_car_folder()
        else:
            print("This is the first car folder; no previous folder to display.")
if __name__ == "__main__":
    root = Tk()
    app = ImageLabelingApp(root)
    root.mainloop()