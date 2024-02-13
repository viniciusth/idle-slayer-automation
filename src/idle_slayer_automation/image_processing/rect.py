import win32gui


class WindowRect:
    def __init__(self, left, top, bottom, right):
        self.left = left
        self.top = top
        self.bottom = bottom
        self.right = right
        self.width = right - left
        self.height = bottom - top

    def __repr__(self):
        return f"WindowRect({self.left}, {self.top}, {self.bottom}, {self.right})"


def get_window_rect(window_hwnd):
    left, top, right, bottom = win32gui.GetWindowRect(window_hwnd)
    return WindowRect(left, top, bottom, right)
