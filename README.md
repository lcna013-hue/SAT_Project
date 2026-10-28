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


To run:
First download all files
Ensure device has a camera, and space is not dark (to ensure hands can be seen)
And it should work!!
