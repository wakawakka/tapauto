from tkinter import Tk, Label
from PIL import Image, ImageTk
import cv2
import numpy as np
import math


class Detector:

    def __init__(self):
        self.window = Tk()
        self.asteroids_cache = []

    def detect_asteroids(self, img_cv, top_left_padding):
        """
        Detect the yellow asteroids in the image.

        :param img_cv: Image in OpenCV format (RGB)
        :return: List of asteroid positions (center coordinates)
        """
        # Define yellow color range in RGB
        lower_yellow = np.array([200, 200, 0])
        upper_yellow = np.array([255, 255, 150])

        # Mask yellow objects
        mask_yellow = cv2.inRange(img_cv, lower_yellow, upper_yellow)

        # Find contours of yellow asteroids
        yellow_asteroids = cv2.findContours(
            mask_yellow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )[0]

        asteroid_positions = []
        yp, xp = top_left_padding
        for cnt in yellow_asteroids:
            x, y, w, h = cv2.boundingRect(cnt)
            r = (w + h) // 3
            if r < 10:
                continue
            asteroid_positions.append(
                (x + w // 2 + xp, y + h // 2 + yp, r)
            )  # center of the asteroid

        return asteroid_positions

    def detect_stick(self, img_cv, top_left_padding):
        """
        Detect the angle of the airplane's hand (white stick).

        :param img_cv: Image in OpenCV format (RGB)
        :return: Angle of the white stick in degrees
        """
        # Define white color range in RGB
        lower_white = np.array([215, 215, 215])
        upper_white = np.array([255, 255, 255])

        # Mask white objects (stick)
        mask_white = cv2.inRange(img_cv, lower_white, upper_white)
        # cv2.imshow("Detected Results", mask_white)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        # Detect edges for white stick
        # edges_white = cv2.Canny(mask_white, 100, 150)

        # cv2.imshow("Detected Results", edges_white)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        # Detect lines using Hough Transform
        lines = cv2.HoughLinesP(
            mask_white, 1, np.pi / 180, threshold=12, minLineLength=11, maxLineGap=3
        )
        yp, xp = top_left_padding
        line_list = []
        if lines is not None:
            for line in lines:
                # Apply padding
                x1, y1, x2, y2 = line[0]
                (
                    x1p,
                    x2p,
                ) = (
                    x1 + xp,
                    x2 + xp,
                )
                y1p, y2p = y1 + yp, y2 + yp
                # Calculate the angle of the line
                angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
                # line_list.append((angle, line[0]))  # Also return the line coordinates
                line_list.append(
                    (angle, (x1p, y1p, x2p, y2p))
                )  # Also return the line coordinates
        return line_list
        return None, None  # No stick detected

    def show_results(self, img_cv, asteroid_positions=[], stick_lines=[], shots=[]):
        """
        Show the detected results on the image: asteroids and stick.

        :param img_cv: Image in OpenCV format (RGB)
        :param asteroid_positions: List of (x, y) positions for asteroids
        :param stick_line: Coordinates of the detected stick line (x1, y1, x2, y2)
        """
        for widget in self.window.winfo_children():
            widget.destroy()
        # Draw asteroids
        if asteroid_positions:
            for x, y, r in asteroid_positions:
                cv2.circle(img_cv, (x, y), r, (0, 255, 255), 2)  # Yellow circle

        # Draw airplane stick if detected

        for stick_line in stick_lines:
            x1, y1, x2, y2 = stick_line[1]
            cv2.line(
                img_cv, (x1, y1), (x2, y2), (0, 255, 255), 2
            )  # Blue line for the stick

        for shot in shots:
            xs1, ys1, xs2, ys2 = shot
            cv2.line(
                img_cv, (xs1, ys1), (xs2, ys2), (255, 255, 0), 2
            )  # Blue line for the stick

        # Display the result
        img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)

        tk_img = ImageTk.PhotoImage(img_pil)
        label = Label(self.window, image=tk_img)
        label.image = tk_img
        label.pack()
        self.window.update()
        self.window.after(500)

        # cv2.namedWindow("results", cv2.WINDOW_NORMAL)

        # cv2.imshow("results", img_cv)
        # cv2.resizeWindow("results", 1000, 1000)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

    # Load the image
    def is_shot(self, img_io, keep_old_asteroids=False, show=False):
        img = Image.open(img_io)

        w, h = img.size

        img_cv = np.array(img)
        img_cv_top = img_cv[100:200, w // 2 - 50 : w // 2 + 50]
        top_left_padding_lines = (100, w // 2 - 50)
        img_cv_bot = img_cv[200:]
        top_left_padding_asteroids = (200, 0)
        lines = self.detect_stick(img_cv_top, top_left_padding_lines)
        if not keep_old_asteroids:
            asteroids = self.detect_asteroids(img_cv_bot, top_left_padding_asteroids)
            self.asteroids_cache = asteroids
        else:
            asteroids = self.asteroids_cache
        shot_lines = []
        for l in lines:
            x1, y1, x2, y2 = l[1]
            for a in asteroids:
                x, y, r = a
                # d - расстояние от прямой до центра окружности
                d = abs((x2 - x1) * (y1 - y) - (y2 - y1) * (x1 - x)) / math.sqrt(
                    (x2 - x1) ** 2 + (y2 - y1) ** 2
                )
                if d < r:
                    shot_lines.append((x1, y1, x, y))
                    if show:
                        self.show_results(
                            img_cv=img_cv,
                            asteroid_positions=asteroids,
                            stick_lines=lines,
                            shots=shot_lines,
                        )
                    return True

        return False


if __name__ == "__main__":
    d = Detector()
    for i in range(100):
        if i % 10 == 0:
            d.is_shot(f"screenshots/{i}.png", False, True)
        else:
            d.is_shot(f"screenshots/{i}.png", True, True)
    # if angle is not None:
    #     print(f"Angle of airplane hand: {angle} degrees")
    # else:
    #     print("No airplane hand (stick) detected.")
    # show_results(img_cv_top, stick_lines=lines, asteroid_positions=asteroids)
    # show_results(
    #     img_cv, asteroid_positions=asteroids, stick_lines=lines, shots=shot_lines
    # )


# img_cv_bot = img_cv[200:]
# cv2.imshow("top", img_cv_top)
# cv2.imshow("bot", img_cv_bot)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
#
# Detect asteroids
# asteroid_positions = detect_asteroids(img_cv)
# print(f"Positions of yellow asteroids: {asteroid_positions}")

# # Detect airplane hand (stick) angle
# stick_angle, stick_line = detect_stick(img_cv)
# if stick_angle is not None:
#     print(f"Angle of airplane hand: {stick_angle} degrees")
# else:
#     print("No airplane hand (stick) detected.")

# # Display the results
# show_results(img_cv, asteroid_positions, stick_line)


# mb.sleep()
# cookie_reject_button = mb.find_element(
#     By.XPATH, '//button[contains(text(), "Reject Additional Cookies")]', False
# )
# mb.scroll_and_click(cookie_reject_button)
# mb.sleep()
# play_button = mb.find_element(By.XPATH, '//div[contains(text(), "Play Game")]')
# mb.scroll_and_click(play_button)

# mb.sleep()
# canvas = mb.find_element(By.XPATH, "//div/div/div/canvas")
# # mb.scroll_and_click(canvas)

# d = moonbix_detector.Detector()
# frame_i = 0

# while True:
#     png = canvas.screenshot_as_png
#     hash = md5(png).hexdigest()
#     png_io = io.BytesIO(png)
#     png_io.seek(0)

#     # keep_old_asteroids - economy of calculations of asteroids positions
#     # is_shot = d.is_shot(png_io, keep_old_asteroids=False)
#     if frame_i % 5 == 0:
#         is_shot = d.is_shot(png_io, keep_old_asteroids=False)
#     else:
#         is_shot = d.is_shot(png_io, keep_old_asteroids=True)
#     if is_shot:
#         canvas.click()
#     # time.sleep(0.1)
#     frame_i += 1


# pass
