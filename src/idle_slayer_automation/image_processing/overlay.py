import win32gui, win32ui, win32api


class WindowRect:
    def __init__(self, left, top, bottom, right):
        self.left = left
        self.top = top
        self.bottom = bottom
        self.right = right
        self.width = right - left
        self.height = bottom - top


def windows_rect(rect: WindowRect):
    return (rect.left, rect.top, rect.right, rect.bottom)


def get_window_rect(window_hwnd):
    left, top, right, bottom = win32gui.GetWindowRect(window_hwnd)
    return WindowRect(left, top, bottom, right)


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

    def drop(self):
        self.dcObj.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, self.dc)

    def draw_fps(self, fps):
        """
        Draws the FPS as text on the middle bottom of the overlay window.
        """
        rect = get_window_rect(self.window_hwnd)
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
        window_rect = get_window_rect(self.window_hwnd)
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
