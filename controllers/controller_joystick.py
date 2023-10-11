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
                # Buttons
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 4:
                        self.speedDown()
                    elif event.button == 5:
                        self.speedUp()
                    elif event.button == 6:
                        print("Stop guide")
                    elif event.button == 7:
                        print("Start guide")
                    elif event.button == 0:
                        self.main.manual_controller.button_ar_n.toggle()
                        self.main.manual_controller.move_ar_n()
                    elif event.button == 1:
                        self.main.manual_controller.button_dec_p.toggle()
                        self.main.manual_controller.move_dec_p()
                    elif event.button == 2:
                        self.main.manual_controller.button_dec_n.toggle()
                        self.main.manual_controller.move_dec_n()
                    elif event.button == 3:
                        self.main.manual_controller.button_ar_p.toggle()
                        self.main.manual_controller.move_ar_p()

                if event.type == pygame.JOYBUTTONUP:
                    if event.button == 0:
                        self.main.manual_controller.button_ar_n.toggle()
                        self.main.manual_controller.move_ar_n()
                    elif event.button == 1:
                        self.main.manual_controller.button_dec_p.toggle()
                        self.main.manual_controller.move_dec_p()
                    elif event.button == 2:
                        self.main.manual_controller.button_dec_n.toggle()
                        self.main.manual_controller.move_dec_n()
                    elif event.button == 3:
                        self.main.manual_controller.button_ar_p.toggle()
                        self.main.manual_controller.move_ar_p()

            # Add a delay to avoid printing too quickly
            pygame.time.delay(100)  # Delay in milliseconds

    def speedUp(self):
        current_index = self.main.manual_controller.speed_combo.currentIndex()
        if current_index < self.main.manual_controller.speed_combo.count() - 1:
            next_index = current_index + 1
            self.main.manual_controller.speed_combo.setCurrentIndex(next_index)

    def speedDown(self):
        current_index = self.main.manual_controller.speed_combo.currentIndex()
        if current_index > 0:
            next_index = current_index - 1
            self.main.manual_controller.speed_combo.setCurrentIndex(next_index)
