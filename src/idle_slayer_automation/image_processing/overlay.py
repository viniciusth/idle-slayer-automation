from collections import namedtuple
import win32gui, win32ui, win32con, win32api

WindowRect = namedtuple(
    "WindowRect", ["left", "top", "bottom", "right", "width", "height"]
)


def windows_rect(rect: WindowRect):
    return (rect.left, rect.top, rect.right, rect.bottom)


class OverlayHandler:
    def __init__(self, window_hwnd):
        self.window_hwnd = window_hwnd
        self.dc = win32gui.GetDC(0)
        self.dcObj = win32ui.CreateDCFromHandle(self.dc)
        self.hwnd = win32gui.WindowFromPoint((0, 0))
        self.monitor = (
            0,
            0,
            win32api.GetSystemMetrics(0),
            win32api.GetSystemMetrics(1),
        )

    def get_window_rect(self):
        left, top, right, bottom = win32gui.GetWindowRect(self.window_hwnd)
        width = right - left
        height = bottom - top
        return WindowRect(left, top, bottom, right, width, height)

    def drop(self):
        self.dcObj.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, self.dc)

    def draw_fps(self, fps):
        """
        Draws the FPS as text on the middle bottom of the overlay window.
        """
        rect = self.get_window_rect()
        self.dcObj.TextOut(
            rect.left + rect.width // 2,
            rect.bottom - 30,
            f"FPS: {fps}",
        )
        win32gui.InvalidateRect(self.hwnd, windows_rect(rect), True)

    def draw_rect_outline(self, rect: WindowRect):
        """
        Draws a white rectangle outline on the overlay window.
        """
        window_rect = self.get_window_rect()
        rect = WindowRect(
            rect.left + window_rect.left,
            rect.top + window_rect.top,
            rect.bottom + window_rect.top,
            rect.right + window_rect.left,
            rect.width,
            rect.height,
        )
        brush = win32ui.CreateBrush(0, 0xFF0000, 0)
        self.dcObj.FrameRect(windows_rect(rect), brush)
        win32gui.InvalidateRect(self.hwnd, windows_rect(rect), True)

    def clear(self):
        win32gui.InvalidateRect(0, self.monitor, True)
