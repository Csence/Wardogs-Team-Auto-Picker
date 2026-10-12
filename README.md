Wardogs Team Auto Picker
========================

⚠️ Legal & Ethical Disclaimer
-----------------------------

This project is provided strictly for **educational and research purposes only**. The use of automated scripts, macros, or computer vision tools to interact with game clients often violates the Terms of Service (ToS) or End User License Agreement (EULA) of many software providers and game publishers.

By downloading, viewing, or running this code, you acknowledge and agree that you use it entirely at your own risk. The creators and contributors of this repository are not responsible for any consequences resulting from the use of this software, including but not limited to: account suspensions, permanent bans, hardware bans, or any other punitive actions taken by game administrators. Do not use this tool in public or competitive multiplayer environments.

Overview
--------

This project is an automated team selector utility for Wardogs. It uses screen automation to detect on-screen visual elements and automatically select a chosen faction: Lonestar, Valkyra, or Manticore. The script runs in the background and continuously clicks the desired team's button until it detects that you have successfully entered the game.

Features
--------

*   **Hotkey Integration:** Users can instantly trigger the auto-picker for a specific team by pressing F1, F2, or F3.
    
*   **Dynamic Resolution Scaling:** The script automatically calculates and scales the search regions based on your monitor's current screen resolution. It calculates this using a 1920x1080 resolution baseline.
    
*   **Image Recognition:** Now using mss, pywin32, and OpenCV for faster image capture and processing. It operates with a high confidence threshold and uses grayscale matching to improve performance.
    
*   **Auto-Clicking Loop:** Once activated, the script searches for the team image, clicks it, and repeatedly checks for a secondary "in-game" image to confirm success. Upon successful confirmation, it notifies the user and returns to the main menu.
    
*   **Cancelable Operations:** Pressing the ESC key immediately halts the auto-clicking loop or exits the application.
    
Installation & Usage
-----

You no longer need to install Python or mess with dependencies! Just download the pre-compiled version:

1.  Go to the **Releases** section on the right side of this GitHub repository.
    
2.  Download the latest .zip file (e.g., windows-build.zip).
    
3.  **Extract the entire .zip file** into a folder on your computer._(⚠️ Important: Do not run the .exe directly from inside the .zip archive, or it will fail to load the required images folder)._
    
4.  Double-click main.exe to run the program.
    
5.  Follow the console prompts while your game is open:
    
    *   Press **F1** to auto-pick Lonestar.
        
    *   Press **F2** to auto-pick Valkyra.
        
    *   Press **F3** to auto-pick Manticore.
        
    *   Press **ESC** to stop the auto-clicking loop or exit the program.

## Issues & Support
If you encounter any bugs, run into problems getting the script to work, or have suggestions for improvements, please feel free to open an issue in this repository!
