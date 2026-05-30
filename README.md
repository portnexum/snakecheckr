# snakecheckr - Instagram Unfollower Checker
vibe code bot that finds out who does not follow you back on instagram. does not store your IG data. undetected IG botting. (requires chrome v148).

A free, private tool that shows you exactly who doesn't follow you back on Instagram.
Runs 100% locally on your computer — no data is stored, no third-party servers involved.

## How It Works

1. You enter your Instagram username.
2. A Chrome browser window opens and takes you to Instagram's login page.
3. You log in manually — this is completely normal and expected.
4. The tool scans your followers and following list.
5. It shows you every account that doesn't follow you back.

NOTE: A new Chrome window will open automatically when you start the tool.
This is intentional — the tool needs a real browser session to access Instagram.
You are logging into your own Instagram account, just like you normally would.
No passwords are saved or transmitted anywhere.

## Requirements

- Python 3.11
- Google Chrome installed on your computer
- A stable internet connection

## Setup & Installation

### Step 1: Download the project

Click the green Code button on this page -> Download ZIP -> unzip the folder.

### Step 2: Move the folder to your root drive

Windows:
Move the unzipped folder to your C: drive so the path looks like this:
C:\instagram-unfollower-checker

Mac:
Move the unzipped folder to your home directory so the path looks like this:
/Users/yourmacusername/instagram-unfollower-checker

### Step 3: Install Python 3.11

If you don't have Python installed, download and install it from:
https://www.python.org/downloads/

During installation on Windows, make sure to check the box that says "Add Python to PATH" before clicking Install.

### Step 4: Open your terminal inside the project folder

Windows:
1. Press the Windows key, type cmd, and open Command Prompt.
2. Type the following and press Enter:
cd C:\instagram-unfollower-checker

Mac:
1. Open Terminal.
2. Type the following and press Enter:
cd /Users/yourmacusername/instagram-unfollower-checker

### Step 5: Install the required libraries

Copy and paste this into your terminal and press Enter:
pip install flask selenium undetected-chromedriver

Wait for it to finish installing.

### Step 6: Run the app

Copy and paste this into your terminal and press Enter:
python app.py

### Step 7: Open in your browser

Once the terminal shows that the server is running, open your browser and go to:
http://localhost:5000

The app will load and you are ready to use it.

## Usage

1. Enter your Instagram username without the @.
2. Click Start.
3. A Chrome window will open — log into your Instagram account manually.
4. Come back to the app and click I'm Logged In / Continue.
5. Wait for the scan to complete.
6. View the full list of accounts not following you back.

## Privacy & Safety

- Your login credentials are never stored or transmitted.
- Everything runs on your own machine — no cloud, no external servers.
- The Chrome window uses your normal Instagram session, just like logging in from any browser.
- No data is saved after you close the app.

## Common Issues

Chrome opens but immediately closes:
Make sure you have Google Chrome installed.

ModuleNotFoundError:
Run `pip install flask selenium undetected-chromedriver` again and make sure you're using Python 3.11.

The scan seems stuck:
Instagram rate-limits requests. Just wait — the tool adds natural delays to avoid this.

Could not verify username:
Make sure you're logging into the same account you entered in the app.

## Tech Stack

- Python 3.11
- Flask
- Selenium
- Undetected ChromeDriver
- Vanilla HTML/CSS/JS

## License

Free to use and modify for personal use.

Made with Python
