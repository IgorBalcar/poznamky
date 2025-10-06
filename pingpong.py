# filepath: c:\Users\balca\Desktop\my-project\src\pingpong\game.py
# ...existing code...
"""
Standalone Ping-Pong (Pong) game using tkinter.

Controls:
- Left player: W (up), S (down)
- Right player: Up arrow, Down arrow
- Press R to reset scores

Run:
    python pingpong.py         # single-player (AI right)
    python pingpong.py -2      # two-player (both keyboards)
"""
import tkinter as tk
import random
import argparse
import sys

WIDTH = 800
HEIGHT = 400
PADDLE_WIDTH = 10
PADDLE_HEIGHT = 80
BALL_SIZE = 16
PADDLE_SPEED = 6
BALL_SPEED = 5
AI_SPEED = 4
SCORE_FONT = ("Helvetica", 18)


class PongGame:
    def __init__(self, root, two_player=False):
        self.root = root
        self.two_player = two_player
        self.root.title("Ping Pong")
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="black")
        self.canvas.pack()
        # paddles
        self.left_paddle = self.canvas.create_rectangle(
            20,
            (HEIGHT - PADDLE_HEIGHT) // 2,
            20 + PADDLE_WIDTH,
            (HEIGHT - PADDLE_HEIGHT) // 2 + PADDLE_HEIGHT,
            fill="white",
        )
        self.right_paddle = self.canvas.create_rectangle(
            WIDTH - 20 - PADDLE_WIDTH,
            (HEIGHT - PADDLE_HEIGHT) // 2,
            WIDTH - 20,
            (HEIGHT - PADDLE_HEIGHT) // 2 + PADDLE_HEIGHT,
            fill="white",
        )
        # ball
        self.ball = self.canvas.create_oval(0, 0, BALL_SIZE, BALL_SIZE, fill="white")
        self.reset_ball()
        # scores
        self.left_score = 0
        self.right_score = 0
        self.score_text = self.canvas.create_text(
            WIDTH // 2, 20, fill="white", font=SCORE_FONT, text=self.score_text_value()
        )
        # controls flags
        self.p1_up = self.p1_down = self.p2_up = self.p2_down = False

        # bindings
        root.bind("<KeyPress>", self.on_key_press)
        root.bind("<KeyRelease>", self.on_key_release)
        # start loop
        self.running = True
        self.update()

    def score_text_value(self):
        return f"{self.left_score}    {self.right_score}"

    def reset_ball(self, direction=None):
        cx = (WIDTH - BALL_SIZE) // 2
        cy = (HEIGHT - BALL_SIZE) // 2
        self.canvas.coords(self.ball, cx, cy, cx + BALL_SIZE, cy + BALL_SIZE)
        angle = random.uniform(-0.6, 0.6)
        if direction is None:
            dir_sign = 1 if random.choice([True, False]) else -1
        else:
            dir_sign = 1 if direction == "right" else -1
        self.ball_vx = dir_sign * BALL_SPEED
        self.ball_vy = BALL_SPEED * angle

    def on_key_press(self, event):
        k = event.keysym.lower()
        if k == "w":
            self.p1_up = True
        elif k == "s":
            self.p1_down = True
        elif k == "up":
            self.p2_up = True
        elif k == "down":
            self.p2_down = True
        elif k == "r":
            self.left_score = self.right_score = 0
            self.canvas.itemconfig(self.score_text, text=self.score_text_value())
            self.reset_ball()

    def on_key_release(self, event):
        k = event.keysym.lower()
        if k == "w":
            self.p1_up = False
        elif k == "s":
            self.p1_down = False
        elif k == "up":
            self.p2_up = False
        elif k == "down":
            self.p2_down = False

    def move_paddles(self):
        x1, y1, x2, y2 = self.canvas.coords(self.left_paddle)
        if self.p1_up and y1 > 0:
            self.canvas.move(self.left_paddle, 0, -PADDLE_SPEED)
        if self.p1_down and y2 < HEIGHT:
            self.canvas.move(self.left_paddle, 0, PADDLE_SPEED)

        if self.two_player:
            x1, y1, x2, y2 = self.canvas.coords(self.right_paddle)
            if self.p2_up and y1 > 0:
                self.canvas.move(self.right_paddle, 0, -PADDLE_SPEED)
            if self.p2_down and y2 < HEIGHT:
                self.canvas.move(self.right_paddle, 0, PADDLE_SPEED)
        else:
            bx1, by1, bx2, by2 = self.canvas.coords(self.ball)
            ball_cy = (by1 + by2) / 2
            rx1, ry1, rx2, ry2 = self.canvas.coords(self.right_paddle)
            paddle_cy = (ry1 + ry2) / 2
            if paddle_cy < ball_cy and ry2 < HEIGHT:
                self.canvas.move(self.right_paddle, 0, min(AI_SPEED, ball_cy - paddle_cy))
            elif paddle_cy > ball_cy and ry1 > 0:
                self.canvas.move(self.right_paddle, 0, -min(AI_SPEED, paddle_cy - ball_cy))

    def update_ball(self):
        self.canvas.move(self.ball, self.ball_vx, self.ball_vy)
        bx1, by1, bx2, by2 = self.canvas.coords(self.ball)
        if by1 <= 0 and self.ball_vy < 0:
            self.ball_vy = -self.ball_vy
        if by2 >= HEIGHT and self.ball_vy > 0:
            self.ball_vy = -self.ball_vy
        if self.overlaps(self.ball, self.left_paddle) and self.ball_vx < 0:
            self.ball_vx = -self.ball_vx
            self._tweak_ball_vy(self.left_paddle)
        if self.overlaps(self.ball, self.right_paddle) and self.ball_vx > 0:
            self.ball_vx = -self.ball_vx
            self._tweak_ball_vy(self.right_paddle)
        if bx1 <= 0:
            self.right_score += 1
            self.canvas.itemconfig(self.score_text, text=self.score_text_value())
            self.reset_ball(direction="right")
        elif bx2 >= WIDTH:
            self.left_score += 1
            self.canvas.itemconfig(self.score_text, text=self.score_text_value())
            self.reset_ball(direction="left")

    def overlaps(self, a_id, b_id):
        ax1, ay1, ax2, ay2 = self.canvas.coords(a_id)
        bx1, by1, bx2, by2 = self.canvas.coords(b_id)
        return not (ax2 < bx1 or ax1 > bx2 or ay2 < by1 or ay1 > by2)

    def _tweak_ball_vy(self, paddle_id):
        px1, py1, px2, py2 = self.canvas.coords(paddle_id)
        paddle_center = (py1 + py2) / 2
        bx1, by1, bx2, by2 = self.canvas.coords(self.ball)
        ball_center = (by1 + by2) / 2
        offset = (ball_center - paddle_center) / (PADDLE_HEIGHT / 2)
        self.ball_vy += offset * 3
        max_v = BALL_SPEED * 2
        if self.ball_vy > max_v:
            self.ball_vy = max_v
        if self.ball_vy < -max_v:
            self.ball_vy = -max_v

    def update(self):
        if not self.running:
            return
        self.move_paddles()
        self.update_ball()
        self.root.after(16, self.update)

    def stop(self):
        self.running = False

    def run(self):
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.stop()


def main(argv=None):
    parser = argparse.ArgumentParser(description="Ping Pong game")
    parser.add_argument("-2", "--two-player", action="store_true", help="enable local two-player mode")
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    root = tk.Tk()
    game = PongGame(root, two_player=args.two_player)
    game.run()


if __name__ == "__main__":
    main()
# ...existing code...