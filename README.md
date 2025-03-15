# E621-Scraper

E621-Scraper is a Python command line tool for both Linux and Windows. It scrapes posts from e621 based on tags you provide and lets you set a blacklist to exclude unwanted content. The tool sports a retro IBM-terminal style interface with a dynamic progress bar and session folders. Each scraping session creates a new subfolder (named with the current Unix time) inside your chosen working directory.

## Features

- **Search Posts:** Quickly search for posts by entering comma-separated tags.
- **Scrape Posts by Tag:** Download images and metadata from posts that match your search tags.
- **Search by Pool:** Scrape posts from a specific pool (files receive sequential numbering).
- **Update Blacklist:** Easily update a list of tags to exclude from your queries.
- **Retro Interface:** Enjoy a classic terminal look with a single-line progress bar that shows files downloaded, average download speed, and ETA.
- **Session Folders:** Every scraping session creates a new subfolder (named using the current Unix time) inside your working directory.

## Prerequisites

Ensure you have Python 3.6 or higher installed.
Ensure you include your e621 username and API key in the script. (Line 72)

### For Linux

1. Open your terminal.
2. Update your package lists and install Python 3 and pip. For example, on Debian/Ubuntu you might run:  
   sudo apt update  
   sudo apt install python3 python3-pip

### For Windows

1. Download Python from the official website (https://www.python.org/downloads/).  
   **Important:** During installation, make sure to check the option "Add Python to PATH."
2. Open Command Prompt or PowerShell.

## Installation

1. **Clone or Download the Repository:**  
   Get the repository either by cloning it from GitHub or by downloading and extracting the ZIP file.

2. **Navigate to the Project Directory:**  
   Open your terminal or command prompt and change to the project folder (e.g., using cd E621-Scraper).

3. **(Optional but Recommended) Create a Virtual Environment:**  
   This helps keep dependencies isolated.  
   On Linux, run:  
   python3 -m venv env  
   source env/bin/activate  
   On Windows, run:  
   python -m venv env  
   .\env\Scripts\activate

4. **Install Required Packages:**  
   The tool uses the requests library. Install it by running:  
   pip install requests

## Usage

1. **Run the Script:**  
   In your terminal or command prompt, run the script by entering:  
   python e621_scraper.py  
   (On Linux, you might need to run python3 e621_scraper.py.)

2. **Initial Setup:**  
   On first launch, the tool will prompt you to set up:  
   - **Nickname:** A friendly name for your session.  
   - **Working Directory:** Provide an absolute path where scraped images and metadata will be stored. If this directory does not exist, you will be asked if you want to create it.  
   - **Blacklist Tags:** Enter any tags (comma-separated) that you want to exclude from searches and scrapes.  
   These settings are saved in a config.json file for future sessions.

3. **Main Menu Options:**  
   Once setup is complete, you'll see a retro-style main menu with the following options:  
   - **1) Search Posts:** Enter comma-separated tags to view matching posts. The tool displays each post's ID, rating, and image URL.  
   - **2) Scrape Posts by Tag:**  
     - Enter the tags (comma-separated) you wish to scrape.  
     - The tool scans and displays how many pages and total posts are available.  
     - You can then choose how many pages to scrape or type "all" to scrape all available pages.  
     - A new session folder (named with the current Unix time) is created within your working directory.  
     - A single-line progress bar shows the current file count, average download speed, and ETA.
   - **3) Search by Pool:** Enter a pool ID to scrape posts from a specific pool. Files downloaded in pool mode are sequentially numbered (001, 002, 003, etc.).
   - **4) Update Blacklisted Tags:** Modify your blacklist settings.
   - **5) Exit:** Close the tool.

4. **During the Scrape:**  
   - The tool first scans your query and shows the total number of available pages and posts.  
   - After confirmation, it clears the screen and starts downloading, displaying a progress bar.  
   - A metadata file (posts_metadata.json) is saved in the session folder, containing details of the scraped posts.

## Troubleshooting

- **Directory Issues:** Make sure the working directory exists or agree to have it created.
- **Network Problems:** Verify that your internet connection is stable, as the tool connects to the e621 API.
- **Dependency Errors:** Ensure that requests is installed in your active virtual environment.

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to open an issue or submit a pull request on GitHub.

## Disclaimer

This tool is intended for personal use only. Please use it responsibly and respect the e621 terms of service.
