# Launch Remote Browser

To turn that script into something you can actually execute, you have two main options: the **Terminal way** (standard for devs) or the **Double-Click way** (best for your workflow).

## Option 1: The "Double-Click" Method (Recommended)

If you want to just click an icon and have Edge launch with debugging enabled, rename your file extension from `.sh` to **`.command`**.

1. Rename your file to `launch-[browser]-[OS].command`.
2. Open **Terminal** (Cmd + Space, type "Terminal").
3. Type `chmod +x` (make sure there is a space at the end).
4. **Drag and drop** your `launch-[browser]-[OS].command` file from Finder into the Terminal window. It will look something like this:
    `chmod +x /Users/yourname/Desktop/launch-[browser]-[OS].command`
5. Press **Enter**.

Now, you can **double-click** that file in Finder whenever you want to start your debugging session. It will open a terminal window, run the command, and launch Edge.

## Option 2: Running via Terminal

If you prefer keeping it as a `.sh` file and running it manually:

1. Open **Terminal**.
2. Navigate to where the file is (e.g., `cd ~/Desktop`).
3. Give it permission to run:

    ```bash
    chmod +x launch-[browser]-[OS].sh
    ```

4. Run it by typing:

    ```bash
    ./launch-[browser]-[OS].sh
    ```

---

### Troubleshooting: "Action Not Permitted"

If you double-click the `.command` file and macOS complains about an "unidentified developer" or permissions:

1. Go to **System Settings > Privacy & Security**.
2. Scroll down to the bottom and click **"Open Anyway"** for the script.
3. You might also need to grant Terminal "Full Disk Access" if the script is trying to write to a protected `/tmp/` folder.

## Tips for your Setup

- Why the separate user-dir? By using --user-data-dir="/tmp/chrome-debug", you are opening a "clean" instance of Chrome. If you try to run the command while your normal Chrome is already open without this flag, macOS will just open a new window in your existing session, which usually ignores the debugging port request.
- Verify it’s working: Once the browser opens, go to <http://localhost:9222/json> in the address bar. If you see a list of tabs in JSON format, your VS Code Copilot is officially connected and ready to give you insights.
- VS Code Settings: Since you now have scripts for both, your browser-auto configuration in mcp.json will work for either browser—whichever one you happened to launch last!
