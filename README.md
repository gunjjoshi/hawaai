# hawaAI

hawaAI is an innovative air mouse tracker for laptops that uses hand gestures to control the cursor. This project leverages advanced computer vision and machine learning techniques to provide a hands-free computing experience, making it ideal for presentations, gaming, and various interactive applications.

## Features

- **Hand Gesture Recognition**: Control your cursor using hand gestures with high accuracy.
- **Customizable Gestures**: Supports multiple gestures for different mouse actions:
  - Pinch index and thumb: Left Click
  - Pinch middle and thumb: Right Click
  - Pinch index and middle: Double Click
- **Real-time Performance**: Smooth and responsive cursor movements based on hand position.
- **User-Friendly Interface**: Simple display with help instructions on available gestures.

## Technologies Used

- Python
- OpenCV
- Mediapipe
- PyAutoGUI
- NumPy

## Requirements

Before running the project, ensure you have the following installed:

- Python 3.x
- pip

You can install the required Python packages using the following command:

```bash
pip install opencv-python mediapipe pyautogui numpy
```

## Getting Started

Clone the Repository:

```bash
git clone https://github.com/gunjjoshi/hawaai
```

Change into the project directory:

```bash
cd hawaai
```

Run the Application: Make sure your camera is connected and functioning, then run:

```bash
python main.py
```

Using the Application:

- Follow the on-screen instructions to control the mouse using hand gestures.
- Press the ESC key to exit the application.
