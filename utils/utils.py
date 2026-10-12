import time
import win32process, win32api, win32gui, win32con
import logging
import psutil
from mss import MSS

"""
process_handle = win32security.OpenProcessToken(win32api.GetCurrentProcess(), win32con.TOKEN_ADJUST_PRIVILEGES | win32con.TOKEN_QUERY)
privilege_value = win32security.LookupPrivilegeValue(None, win32con.SE_DEBUG_NAME)
win32security.AdjustTokenPrivileges(process_handle, False, [(privilege_value, win32con.SE_PRIVILEGE_ENABLED)])
"""

def getGameStatus():
    """
    Check if the game is running by enumerating all processes and checking their names.
    Returns a tuple (running: bool, pid: int or None)
    """

    app_name = "WardogsClient-Win64-Shipping.exe"
    logging.basicConfig()

    running = False
    pid = None

    for proc in win32process.EnumProcesses():
        if proc == 0:
            logging.debug("Skipping System Idle Process (PID 0)")
            continue
        if proc == 4:
            logging.debug("Skipping System process (PID 4)")
            continue
        try:
            psutil_process = psutil.Process(proc) 
            """
            Using psutil to get the process name because win32process.GetModuleFileNameEx can throw an access denied error if the process is protected or running with higher privileges than the script.
            Still trying to figure out how to get the process name using win32process without getting access denied errors.
            """
            logging.debug(f"Checking process: {psutil_process.name()} (PID: {proc})")
            if psutil_process.name().lower() == app_name.lower():
                running = True
                pid = proc
                break
        except Exception as e:
            # supress any exceptions that occur while trying to access process information
            logging.debug(f"Could not access process {proc}: {e}")
            pass

    logging.info(f"{app_name} is running: {running, pid}")

    return running, pid

def getMonitorId(process_id):
    """Get the monitor ID for the window associated with the given process ID."""

    logging.basicConfig()
    windows = []

    def callback(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return
    
        windows.append(hwnd)
    win32gui.EnumWindows(callback, None)

    for hwnd in windows:
        if process_id == win32process.GetWindowThreadProcessId(hwnd)[1]:
            logging.info(f"Found window for process ID {process_id}: {hwnd}")
            monitor_handle = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
            monitor_id = win32api.GetMonitorInfo(monitor_handle)["Device"][-1]
            logging.info(f"Monitor info for window {hwnd}: {monitor_id}")
            return int(monitor_id)
            
    return Exception(f"No window found for process ID {process_id}")

def moveMouseToPosition(x, y):
    """Move the mouse cursor to the specified (x, y) coordinates."""

    logging.basicConfig()
    win32api.SetCursorPos((x, y))
    logging.info(f"Moved mouse to ({x}, {y})")

    return None

def clickLeftMouseButton():
    """Simulate a left mouse button click at the current cursor position."""

    logging.basicConfig()
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.01)  # Short delay to simulate a real click
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    logging.info("Left mouse button clicked")

    return None

def getMonitorPosition(mssInstance: MSS, monitorId: int):
    """Get the position of the monitor with the given ID."""

    logging.basicConfig()
    monitorData = mssInstance.monitors[monitorId]
    logging.info(f"Monitor {monitorId} position: {monitorData['left']}, {monitorData['top']}")
    return monitorData['left'], monitorData['top']

