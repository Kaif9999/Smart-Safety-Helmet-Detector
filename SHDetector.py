import cv2
import numpy as np
import cvui
import easygui
from processImage import process as processImage

class SDHException(Exception):
    def __init__(self, exception):
        self.exception = exception

def detect_safety(src_img):
    img = processImage(src_img)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # Detect helmets and draw bounding boxes
    # For demonstration purposes, let's assume helmet coordinates
    helmet_coordinates = [(100, 100, 200, 200)]  # Example coordinates (x1, y1, x2, y2)

    for (x1, y1, x2, y2) in helmet_coordinates:
        # Draw bounding box
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Add label "Helmet Found"
        cv2.putText(img, "Helmet Found", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    return img

#################### Main driver program #######################

# Main UI Frame and Source Image variable
window_name = 'Safety Helmet Detector'

ui_width = 500
ui_height = 300

max_image_width = 480

toolbar_top_height = 100

# Image Containers
frame = np.zeros((ui_height, ui_width, 3), np.uint8)
source_img = np.array([])
source_img_copy = np.array([])
detected_img = np.array([])

image_loaded = False
image_padding = 10

# Button messages
load_action_message = ''
load_action_message_color = 0xCECECE

detect_action_message = ''
detect_action_message_color = 0xCECECE

cvui.init(window_name)

# Initialize camera capture if available
cap = None
camera_used = False

# main program loop (window property check as while condition allows the close button to end the program)
while cv2.getWindowProperty(window_name, 0) >= 0:
    
    # Read frame from the camera or video file if camera or video is selected
    if camera_used and cap is not None:
        ret, frame = cap.read()
        if not ret:
            print("Error")
            break
    
    # If image is loaded adjust the UI size and display the image, else use default values
    if frame.size != 0:
        src_height, src_width = frame.shape[:2]

        new_height = src_height + toolbar_top_height + (image_padding * 2)
        new_width = src_width + (image_padding * 2)

        frame_display = np.zeros((new_height, new_width, 3), np.uint8)
        frame_display[:] = (49, 52, 49)
        
        if detected_img.size != 0:
            cvui.image(frame_display, image_padding, toolbar_top_height + image_padding, detected_img)
        else:
            cvui.image(frame_display, image_padding, toolbar_top_height + image_padding, frame)
    else:
        frame_display = np.zeros((ui_height, ui_width, 3), np.uint8)
        frame_display[:] = (49, 52, 49)

    # Load Image Button. if clicked, easygui opens a dialog for opening images. Error checking included.
    b_load_image = cvui.button(frame_display, 10, 10, 'Load Image')
    if b_load_image:
        src_path = easygui.fileopenbox('Choose an image...', filetypes=[['*.jpg', '*.png', '*.bmp', 'Image Files'], '*'])
        if src_path is not None:
            try:
                source_img = cv2.imread(src_path)

                if isinstance(source_img, type(None)):
                    source_img = np.array([])
                    raise SDHException('Wrong File Type')

                source_img_copy = source_img.copy()
                src_height, src_width = source_img.shape[:2]
                scale = max_image_width / src_width                
                
                source_img = cv2.resize(source_img, (int(src_width * scale), int(src_height * scale)), cv2.INTER_AREA)
                load_action_message = src_path
                load_action_message_color = 0xCECECE
                detect_action_message = ''
                detect_action_message_color = 0xCECECE
                detected_img = np.array([])
                camera_used = False

            except SDHException:
                load_action_message = 'Wrong file type. Please open an image file.'
                load_action_message_color = 0xFF0000

    # Use Camera Button
    b_camera = cvui.button(frame_display, 120, 10, 'Camera')
    if b_camera:
        cap = cv2.VideoCapture(0)  # Change the argument to the appropriate camera index if multiple cameras are available
        if cap.isOpened():
            camera_used = True
            load_action_message = 'Using device camera...'
            load_action_message_color = 0xCECECE
        else:
            load_action_message = 'Camera not available.'
            load_action_message_color = 0xFF0000

    # Load Video Button
    b_load_video = cvui.button(frame_display, 230, 10, 'Load Video')
    if b_load_video:
        src_path = easygui.fileopenbox('Choose a video...', filetypes=[['*.mp4', '*.avi', '*.mov', 'Video Files'], '*'])
        if src_path is not None:
            cap = cv2.VideoCapture(src_path)
            if cap.isOpened():
                camera_used = True
                load_action_message = 'Using video file...'
                load_action_message_color = 0xCECECE
            else:
                load_action_message = 'Failed to open video file.'
                load_action_message_color = 0xFF0000

    # Adding text beside the button to display path or error message
    cvui.text(frame_display, 126, 18, load_action_message, 0.4 , load_action_message_color)

    # If the image was loaded successfully or camera is used, buttons 'Safety Detection' and 'Save Image' appear
    if (source_img_copy.size != 0 or camera_used) and cap is not None:
        b_detect = cvui.button(frame_display, 10, 44, 'Safety Detection')
        if b_detect:
            if camera_used:
                detected_img = detect_safety(frame)
            else:
                detected_img = detect_safety(source_img_copy)
            detect_action_message = 'Done!'
            detect_action_message_color = 0x00FF00

            det_h, det_w = source_img.shape[:2] if camera_used else frame.shape[:2]
            scale = max_image_width / det_w                  
            detected_img = cv2.resize(detected_img, (int(det_w * scale), int(det_h * scale)), cv2.INTER_AREA)
            
        cvui.text(frame_display, 167, 52, detect_action_message, 0.4, detect_action_message_color)

        b_save = cvui.button(frame_display, frame_display.shape[1] - 104 - image_padding, 44, 'Save Image')
        if b_save:
            save_path = easygui.filesavebox('Save Image..', default='detected.jpg', filetypes=['*.jpg'])
            if save_path is not None:
                if detected_img.size != 0:
                    cv2.imwrite(save_path, detected_img)
                elif camera_used:
                    cv2.imwrite(save_path, frame)
                else:
                    cv2.imwrite(save_path, source_img)

    # Show the output on screen
    cvui.imshow(window_name, frame_display)

    # Exit using ESC button
    if cv2.waitKey(20) == 27:
        break
  
# Release resources
if cap is not None:
    cap.release()
cv2.destroyAllWindows()
