import threading

import pygame

# Initialize Pygame
pygame.init()


class JoyStickController:
    def __init__(self, main):
        self.main = main

        # Initialize the joystick
        pygame.joystick.init()

        # Check if a joystick is connected
        if pygame.joystick.get_count() == 0:
            print("No joystick detected.")
        else:
            # Get the first joystick
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

            # Call the sniffer in a parallel thread
            thread = threading.Thread(target=self.doButtonHandling)
            thread.start()

    def doButtonHandling(self):
        # Main loop
        while self.main.gui_open:
            # Handle events
            events = pygame.event.get()
            for event in events:
                # D-Pad
                if event.type == pygame.JOYHATMOTION:
                    if event.value == (1, 0):
                        print("Right")
                    elif event.value == (-1, 0):
                        print("Left")
                    elif event.value == (0, 1):
                        print("Up")
                    elif event.value == (0, -1):
                        print("Down")
                # Buttons
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 4:
                        print("Speed down")
                    elif event.button == 5:
                        print("Speed up")
                    elif event.button == 6:
                        print("Stop guide")
                    elif event.button == 7:
                        print("Start guide")

            # Add a delay to avoid printing too quickly
            pygame.time.delay(100)  # Delay in milliseconds