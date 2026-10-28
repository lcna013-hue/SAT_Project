# GESTURE CONTROLLED GUI


"""
Software Solution 

This software solution allows my users to capture and save images of books using
hand gestures or buttons. The webcam acts as the main data source, providing
live image data which is analysed by the MediaPipe machine learning model which I got from using an API.

The solution uses OOP (object-oriented programming) with many classes,
including App, Camera, and individual page classes. I chose this structure so I can separate
different tasks, making the program easier to maintain and modify.

Data is stored using these data types:
--> Strings store file paths and user input.
--> Integers store quantities and camera dimensions.
--> Booleans store gesture detection states.
--> Images store captured camera frames.
--> Tuples transfer multiple related values between functions.

User input is validated before being saved to prevent incorrect database
entries. Images and quantities are saved together using unique identifiers,
ensuring each book record is stored separately.
"""

# Created and coded by Lucinda Blackmore :)

# Imports here:
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.vision.gesture_recognizer import (GestureRecognizer, GestureRecognizerOptions)
from mediapipe.tasks.python.vision.hand_landmarker import (HandLandmarker, HandLandmarkerOptions)
from mediapipe.tasks.python.core.base_options import BaseOptions

import time
import uuid


# From recogonizers file take the functions to use later. This helps to keep the code cleaner as they are seperated
from recognizers_gesture import ( count_fingers, recognize_victory, recognize_thumbs_up, recognize_thumbs_down)

# Camera details
CAMERA_WIDTH = 800
CAMERA_HEIGHT = 600

# There are the two recgonizer models. They are both API's from MEDIAPIPE
GESTURE_RECOGNIZER_MODEL_PATH = "gesture_recognizer.task"
HAND_LANDMARKER_MODEL_PATH = "hand_landmarker.task"

FINGER_HOLD_DURATION = 2

# Used a class structure as it is able to store its own data and functions which helps to orginasise the code and reduced it from getting repeteive 
class App(tk.Tk):

    # Conductor sets up the GUI, creates the pages, and strts the camera processing
    def __init__(self):
        super().__init__()
        self.title("Gesture Photo Capturer")
        self.geometry("1500x800")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.camera = Camera(self)

        # Obhects are sotred here as variables beacese each page is an instance of a class. This allows pages to keep their own info while still being controlled by the main application
        self.home_page = HomePage(container, self)
        self.home_page.grid(row=0, column=0, sticky="nsew")

        self.photo_page = PhotoPage(container, self)
        self.photo_page.grid(row=0, column=0, sticky="nsew")

        self.saved_page = SavedPage(container, self)
        self.saved_page.grid(row=0, column=0, sticky="nsew")

        self.end_page = EndPage(container, self)
        self.end_page.grid(row=0, column=0, sticky="nsew")

        self.deleted_page = DeletedPage(container, self)
        self.deleted_page.grid(row=0, column=0, sticky="nsew")

        # A variable storing an object reference is ued becuase only one page should be active or "current" at a tie. This allows the programe to know which page should receive the camera input
        self.current_page = self.home_page
        self.current_page.show()
        self.current_page.tkraise()

        self.run_camera()

    
    def run_camera(self):
        frame, finger_count, is_victory, is_thumbs_up, is_thumbs_down = (
            self.camera.run()
        )
        self.current_page.handle_camera_event(
            frame, finger_count, is_victory, is_thumbs_up, is_thumbs_down
        )
        self.after(10, self.run_camera)

    def show_home(self):
        old_page = self.current_page
        self.current_page = self.home_page
        self.current_page.show()
        self.current_page.tkraise()
        old_page.reset()

    def show_photo(self, image: Image):
        old_page = self.current_page
        self.current_page = self.photo_page
        self.current_page.show(image)
        self.current_page.tkraise()
        old_page.reset()

    def show_saved(self, image: Image):
        old_page = self.current_page
        self.current_page = self.saved_page
        self.current_page.show(image)
        self.current_page.tkraise()
        old_page.reset()

    def show_end(self, quantity: int):
        old_page = self.current_page
        self.current_page = self.end_page
        self.current_page.show(quantity)
        self.current_page.tkraise()
        old_page.reset()

    def show_deleted(self):
        old_page = self.current_page
        self.current_page = self.deleted_page
        self.current_page.show()
        self.current_page.tkraise()
        old_page.reset()

# A serperated class for the camera becuase image capture and gesture recognition are sperate responsibilities from the GUI. thsi improves the functionality as the camera can be resued inderpendently.
class Camera:
    def __init__(self, controller: App):
        self.controller = controller

        self.video = cv2.VideoCapture(0)
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

        base_options = BaseOptions(model_asset_path=GESTURE_RECOGNIZER_MODEL_PATH)
        options = GestureRecognizerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=2,
        )
        self.gesture_recognizer = GestureRecognizer.create_from_options(options)

    def run(self) -> tuple[Image, int, bool, bool, bool]:
        _, frame = self.video.read()
        opencv_image = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=opencv_image)
        
        # The gesture_result data is used because MediaPipe returne multiple peices of information including the gesture that was detected andd hand landmarks. This data is proecessed sperately by the two reconition functions
        gesture_result = self.gesture_recognizer.recognize_for_video(
            mp_image, time.time_ns() // 1000
        )

        finger_count = count_fingers(gesture_result)
        is_victory = recognize_victory(gesture_result)
        is_thumbs_up = recognize_thumbs_up(gesture_result)
        is_thumbs_down: bool = recognize_thumbs_down(gesture_result)

        frame = Image.fromarray(opencv_image)

        print(finger_count, is_victory, is_thumbs_up, is_thumbs_down)

        #A tuple data structer was used becuase multiple related values need to be returned by one function.
        return frame, finger_count, is_victory, is_thumbs_up, is_thumbs_down

# Each screen is stored as a class becuase every page contains it own UI elements, buttons, gesture responses. This follows modular programming principles and makes debugging easier.
class HomePage(tk.Frame):
    def __init__(self, parent: tk.Misc, controller: App):
        super().__init__(parent)

        self.controller = controller

        # THUMBS UP IMAGE
        image_thumbs_up = Image.open("thumbs_up.png")
        thumbs_up_image = image_thumbs_up.resize((230, 250))
        self.thumbs_up_image = ImageTk.PhotoImage(thumbs_up_image)
        thumbs_up_image_label = tk.Label(
            self,
            image=self.thumbs_up_image,
            highlightthickness=4,
            highlightbackground="orchid2",
        )
        thumbs_up_image_label.place(anchor="e", relx=0.86, rely=0.67)

        # LABEL
        title_label = tk.Label(self, text="HOME", font=("Aptos", 40), fg="blue2")
        title_label.place(anchor="n", relx=0.5, rely=0.05)

        # BUTTON
        instructions_button = tk.Button(
            self,
            text="""To take a photo, make a thumbs up
        gesutre with your hand, 
        like seen below ⬇""",
            font=("Aptos", 24),
            highlightthickness=4,
            highlightbackground="dodgerblue2",
            command=lambda: self.controller.show_photo(self.frame),
        )
        instructions_button.place(anchor="se", rely=0.38, relx=0.94)

        # A label wiget was slected because tkinter labels can display images. This allows the live camera feed to be show to the user.
        self.camera_label = tk.Label(self)
        self.camera_label.place(relx=0.05, rely=0.2)

    def show(self):
        pass

    def reset(self):
        pass

    def handle_camera_event(
        self,
        frame: Image,
        finger_count: int,
        is_victory: bool,
        is_thumbs_up: bool,
        is_thumbs_down: bool,
    ):
        self.frame = frame
        tk_frame = ImageTk.PhotoImage(image=frame)
        self.camera_label.photo_image = tk_frame
        self.camera_label.configure(image=tk_frame)

        # A selection statement is used becuase the GUI only needs to move the screen when a specfic condition is met. This prevent unrelated gestures from triggering the screen changing response
        if is_thumbs_up == True:
            self.controller.show_photo(self.frame)


class PhotoPage(tk.Frame):
    def __init__(self, parent: tk.Misc, controller: App):
        super().__init__(parent)

        self.controller = controller

        # LABEL
        title_label = tk.Label(self, text="PHOTO TAKEN", font=("Aptos", 40), fg="blue2")
        title_label.place(anchor="n", relx=0.5, rely=0.025)

        # BUTTON
        keep_photo_button = tk.Button(
            self,
            text="""If you wish to keep \n this photo and move \n on, show a peace sign \n to the camera """,
            font=("Aptos", 24),
            highlightthickness=4,
            highlightbackground="orchid2",
            command=lambda: self.controller.show_saved(self.image),
        )
        keep_photo_button.place(relx=0.6, rely=0.20)
                
        # PEACE GESTURE IMAGE
        image_peace = Image.open("peace_hand.jpg")
        peace_image = image_peace.resize((120, 200))
        self.peace_image = ImageTk.PhotoImage(peace_image)
        peace_label = tk.Label(
            self,
            image=self.peace_image,
            highlightthickness=4,
            highlightbackground="orchid2",
        )
        peace_label.place(anchor="e", relx=0.96, rely=0.30)


        # THUMBS DOWN IMAGE
        image_thumbs_down = Image.open("thumbs_down.jpg")
        thumbs_down_image = image_thumbs_down.resize((180, 185))
        self.thumbs_down = ImageTk.PhotoImage(thumbs_down_image)
        thumbs_down_label = tk.Label(
            self,
            image=self.thumbs_down,
            highlightthickness=4,
            highlightbackground="orchid2",
        )
        thumbs_down_label.place(anchor="e", relx=0.98, rely=0.73)


        # LABEL
        or_label = tk.Label(self, text="OR", font=("Aptos", 35))
        or_label.place(relx=0.68, rely=0.50)

        # BUTTON
        delete_photo_button = tk.Button(
            self,
            text="""If you would like \n to delete this photo \n show a thumbs down \n to the camera""",
            font=("Aptos", 24),
            highlightthickness=4,
            highlightbackground="red2",
            command=lambda: self.controller.show_deleted(),
        )
        delete_photo_button.place(relx=0.6, rely=0.65)

        # LABEL IMAGE
        photo_taken_image = Image.open("file.jpg")
        photo_taken_image.resize((300, 400))
        photo_taken_image = ImageTk.PhotoImage(photo_taken_image)
        self.pinching_image_label = tk.Label(
            self,
            highlightthickness=4,
            highlightbackground="orchid2",
        )
        self.pinching_image_label.place(anchor="e", relx=0.50, rely=0.50)

    # The image is is stored as an instance variable becuase that captured photo is required later when saving or deleting the image. Sorting it avoids the need to recapture it.
    def show(self, image: Image):
        self.image = image
        image_resized = image.copy()
        image_resized.resize((300, 400))
        tk_image = ImageTk.PhotoImage(image=image_resized)
        self.pinching_image_label.photo_image = tk_image
        self.pinching_image_label.configure(image=tk_image)

    def reset(self):
        pass

    def handle_camera_event(
        self,
        frame: Image,
        finger_count: int,
        is_victory: bool,
        is_thumbs_up: bool,
        is_thumbs_down: bool,
    ):
        #The conditionstatements are used becuase the different gestures perform different actions. Only one response should occur for each gesture.
        if is_victory == True:
            self.controller.show_saved(self.image)
        elif is_thumbs_down == True:
            self.controller.show_deleted()


class SavedPage(tk.Frame):
    def __init__(self, parent: tk.Misc, controller: App):
        super().__init__(parent)
        self.validation_message = tk.Label(
            self,
            font=("Aptos", 24),
            fg="red",
            highlightthickness=4,
            highlightbackground="dodgerblue2",
        )

        self.controller = controller

        self.quantity = 0
        self.last_updated = None
        self.locked = False

        self.image = None

        # LABEL
        title_label = tk.Label(
            self, text="ADD QUANTITY", font=("Aptos", 40), fg="blue2"
        )
        title_label.place(anchor="n", relx=0.5, rely=0.025)

        # LABEL
        subtitle_label = tk.Label(
            self,
            font=("Aptos", 24),
            text="How many books are there?",
            highlightthickness=4,
            highlightbackground="dodgerblue2",
        )
        subtitle_label.place(relx=0.55, rely=0.2)

        # ENTRY

        # A stringVar is used becuase tkinter entry widgets store user input as text. The input must first be stored as a string before being balidated and converted into an int.  
        self.manual_quantity = tk.StringVar()
        self.str_quantity = str(self.manual_quantity)
        quanty_entry = tk.Entry(
            self, textvariable=self.manual_quantity, font=("aptos", 18)
        )
        quanty_entry.place(anchor="n", relx=0.69, rely=0.3)

        # BUTTON
        submit_quantity_button = tk.Button(
            self,
            font=("Aptos", 24),
            text="Submit Quantity",
            command=lambda: self.submit(self.manual_quantity.get()),
        )
        submit_quantity_button.place(anchor="n", relx=0.69, rely=0.35)

        # LABEL
        instructions_label = tk.Label(
            self,
            font=("Aptos", 24),
            text="Hold up the number of \n fingers for how many of \n these books there are, \n for three seconds. When \n the number is correct, show \n a thumbs up to move on.",
            highlightthickness=4,
            highlightbackground="dodgerblue2",
        )
        instructions_label.place(anchor="n", relx=0.7, rely=0.59)

        # LABEL
        self.quantity_label = tk.Label(
            self,
            font=("Aptos", 24),
            highlightthickness=4,
            highlightbackground="dodgerblue2",
        )

    def show(self, image: Image):
        self.image = image

    def reset(self):
        self.manual_quantity.set(0)

        # Integer is used for quantity becuase books can only exist as whole numbers
        self.quantity = 0
        # None is used for the last_updated  becuased initially no finger gesture have been detected
        self.last_updated = None
        #   Boolean values are used for locked becuase the program only need two states; True: quantity confirmed, False: still detecting fingers
        self.locked = False

        self.quantity_label.place_forget()
        self.validation_message.place_forget()

    def handle_camera_event(
        self,
        frame: Image,
        finger_count: int,
        is_victory: bool,
        is_thumbs_up: bool,
        is_thumbs_down: bool,
    ):
        if self.locked:

            if is_thumbs_up == True:
                self.manual_quantity.set(str(self.quantity))
                self.submit(self.quantity)
                

            if is_thumbs_down == True:
                self.locked = False

                # Reset finger detection so the user can enter another quantity
                self.quantity = 0
                self.last_updated = None

                self.quantity_label.place_forget()

        else:
            # An interger comparason is used to determin is the detected number of fingers has changed. 
            if self.quantity != finger_count:
                self.quantity = finger_count
                # Updating the timestamp ensures the user must hold the same gesture fot the required amount of time before it is acepted. This also helps to validate the data as it leaves less room for errors since the user is hold the same number of fingers for a few seconds.
                self.last_updated = time.time()

            if (
                self.last_updated != None
                and time.time() >= self.last_updated + FINGER_HOLD_DURATION
                and self.quantity != 0
            ):
                self.locked = True

                self.quantity_label.configure(
                    text=f"If there are {finger_count} books, show a thumbs up to move on"
                )
                self.quantity_label.place(relx=0.48, rely=0.47)

    def submit(self, quantity: int):

        if self.image is None:
            return

        self.validation_message.place_forget()

        # The user input i collected as a string because keyboards entries are text. the .strip() function removesunnecessary spaces which prevent invalid entry inputs
        value = self.manual_quantity.get().strip()

        # Empty Box
        if value == "":
            self.validation_message.configure(
                text="Please enter a quantity."
            )
            self.validation_message.place(relx=0.48, rely=0.47)
            return

        # Must be an int 

        # Excetption handeling is used becuase the users input can not be trusted. The programe must prevent invalid values such as letters or decimals from causing an error.
        try:
            quantity = int(value)
        except ValueError:
            self.validation_message.configure(
                text="Enter an interger."
            )
            self.validation_message.place(relx=0.48, rely=0.47)
            return

        # Can not be a negative number
        if quantity < 0:
            self.validation_message.configure(
                text="Quantity can not be negative."
            )
            self.validation_message.place(relx=0.48, rely=0.47)
            return
            
        # Can not be zero
        if quantity == 0:
            self.validation_message.configure(
                text="Quantity can not be zero."
            )
            self.validation_message.place(relx=0.48, rely=0.47)
            return

        # UUD data is used becuase every saved book entry required a unique file name so it does not replace the previously saved book. The quantity variabke is included in the file name so the stored data contains the number of books associated with the image.
        submission_id = uuid.uuid4()
        self.image.save(f"{submission_id}_{quantity}.jpg")
        self.controller.show_end(quantity)



class EndPage(tk.Frame):
    def __init__(self, parent: tk.Misc, controller: App):
        super().__init__(parent)

        self.controller = controller

        # LABEL
        title_label = tk.Label(self, text="BOOK SAVED", font=("Aptos", 40), fg="blue2")
        title_label.place(anchor="n", relx=0.5, rely=0.025)

        # BUTTON
        self.add_another_button = tk.Button(
            self,
            text="Your book/s have \n been added into \n the data base! \n To add another book, \n show a victory gesture.",
            font=("Aptos", 24),
            highlightthickness=4,
            highlightbackground="limegreen",
            command=lambda: self.controller.show_home(),
        )
        self.add_another_button.place(relx=0.6, rely=0.20)

        # LABEL
        error_label = tk.Label(
            self,
            text="If there was a \n problem, please fix \n in the database \n within the next 30 mins",
            font=("Aptos", 24),
            highlightthickness=4,
            highlightbackground="red2",
        )
        error_label.place(relx=0.6, rely=0.65)

    def show(self, quantity):
        self.add_another_button.configure(
            text=f"{quantity} of this book have \n been added into \n the data base! \n To add another book, \n show a victory gesture."
        )

    def reset(self):
        pass

    def handle_camera_event(
        self,
        frame: Image,
        finger_count: int,
        is_victory: bool,
        is_thumbs_up: bool,
        is_thumbs_down: bool,
    ):
        if is_victory == True:
            self.controller.show_home()


class DeletedPage(tk.Frame):
    def __init__(self, parent: tk.Misc, controller: App):
        super().__init__(parent)

        self.controller = controller

        # LABEL
        title = tk.Label(self, text="PHOTO DELTETED", font=("Aptos", 40), fg="blue2")
        title.place(anchor="n", relx=0.5, rely=0.025)

        # LABEL
        photo_deleted = tk.Label(
            self,
            font=("Aptos", 24),
            text="Your photo has been deleted",
            highlightthickness=4,
            highlightbackground="dodgerblue2",
        )
        photo_deleted.place(relx=0.36, rely=0.2)

        # BUTTON
        take_another_button = tk.Button(
            self,
            font=("Aptos", 24),
            text="If you wish to take \n another photo, show an \n victory gesture to return \n to the home screen",
            highlightthickness=4,
            highlightbackground="dodgerblue2",
            command=lambda: self.controller.show_home(),
        )
        take_another_button.place(anchor="n", relx=0.5, rely=0.35)

        # PEACE GESTURE IMAGE
        image_peace = Image.open("peace_hand.jpg")
        peace_image = image_peace.resize((120, 200))
        self.peace_image = ImageTk.PhotoImage(peace_image)
        peace_label = tk.Label(
            self,
            image=self.peace_image,
            highlightthickness=4,
            highlightbackground="orchid2",
        )
        peace_label.place(anchor="e", relx=0.80, rely=0.40)


    def show(self):
        pass

    def reset(self):
        pass

    def handle_camera_event(
        self,
        frame: Image,
        finger_count: int,
        is_victory: bool,
        is_thumbs_up: bool,
        is_thumbs_down: bool,
    ):
        if is_victory == True:
            self.controller.show_home()


if __name__ == "__main__":
    app = App()
    app.mainloop()
