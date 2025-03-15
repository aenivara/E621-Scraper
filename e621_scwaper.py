#!/usr/bin/env python3
import os
import sys
import json
import time
import requests

CONFIG_FILE = "config.json"
API_ENDPOINT = "https://e621.net/posts.json"
DEFAULT_LIMIT = 20  # e621 default per page
MAX_SCAN_PAGES = 200  # max pages to scan for availability

# ================================
# Terminal & Config Functions
# ================================
def print_header():
    header = """
================================================================================
||                                                                            ||
||               WELCOME TO THE E621 TERMINAL SCRAPER v1.0                  ||
||                 (C) 2099 SkunkWerkz CORPORATION - ALL RIGHTS RESERVED             ||
||                                                                            ||
================================================================================
"""
    print(header)

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
            return config
        except Exception as e:
            print(f"ERROR: Could not read config file: {e}")
            sys.exit(1)
    else:
        return None

def save_config(config):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
        print("Configuration saved successfully.")
    except Exception as e:
        print(f"ERROR: Unable to write config file: {e}")

def initialize_config():
    print("It appears this is your first run.")
    nickname = input("Enter your desired nickname: ").strip() or "anonymous"
    working_dir = input("Set your working directory (absolute path): ").strip()
    if not working_dir:
        print("No directory provided. Exiting.")
        sys.exit(1)
    if not os.path.exists(working_dir):
        confirm_input = input(f"Directory '{working_dir}' does not exist. Create it? (y/n): ")
        if confirm_input.lower() == 'y':
            try:
                os.makedirs(working_dir)
                print(f"Directory '{working_dir}' created.")
            except Exception as e:
                print(f"ERROR: Could not create directory: {e}")
                sys.exit(1)
        else:
            print("Working directory must exist. Exiting.")
            sys.exit(1)
    blacklist_input = input("Enter any tags to blacklist (separated by commas), or leave blank: ")
    blacklist = [t.strip() for t in blacklist_input.split(",") if t.strip()] if blacklist_input else []
    config = {
        "nickname": nickname,
        "working_directory": working_dir,
        "blacklist": blacklist,
        # Add e621 authentication info here. API key is found in account settings.
        "username": "",
        "api_key": ""
    }
    save_config(config)
    return config

def confirm(prompt):
    answer = input(f"{prompt} (y/n): ").strip().lower()
    return answer == "y"

def append_counter_to_filename(filename, counter):
    base, ext = os.path.splitext(filename)
    return f"{base}_{counter:03d}{ext}"

# ================================
# API Functions
# ================================
def build_tag_query(user_tags, blacklist):
    # user_tags is a list; blacklist is a list
    user_tags = [t.strip() for t in user_tags if t.strip()]
    blacklist_tags = [f"-{t}" for t in blacklist]
    full_query = " ".join(user_tags + blacklist_tags)
    return full_query.strip()

def fetch_posts(query, page, auth, user_agent, limit=DEFAULT_LIMIT):
    params = {
        'tags': query,
        'page': page,
        'limit': limit
    }
    headers = {
        'User-Agent': user_agent
    }
    try:
        response = requests.get(API_ENDPOINT, params=params, headers=headers, auth=auth)
        if response.status_code == 200:
            data = response.json()
            posts = data.get("posts", [])
            return posts
        else:
            print(f"ERROR: HTTP {response.status_code} returned while fetching posts.")
            return []
    except Exception as e:
        print(f"EXCEPTION: {e}")
        return []

def scan_query(query, auth, user_agent, limit=DEFAULT_LIMIT, max_pages=MAX_SCAN_PAGES):
    """
    Scan up to max_pages to determine how many pages and posts are available.
    """
    page = 1
    total_posts = 0
    while page <= max_pages:
        posts = fetch_posts(query, page, auth, user_agent, limit)
        if not posts:
            break
        total_posts += len(posts)
        # if a page returns less than limit, it's the last page
        if len(posts) < limit:
            break
        page += 1
    total_pages = page
    return total_pages, total_posts

# --------------------------
# Download with Progress Bar
# --------------------------
def download_image(url, output_dir, user_agent, pool_counter=None):
    headers = {'User-Agent': user_agent}
    total_downloaded = 0
    try:
        response = requests.get(url, headers=headers, stream=True)
        if response.status_code == 200:
            filename = os.path.basename(url.split('?')[0])
            if pool_counter is not None:
                filename = append_counter_to_filename(filename, pool_counter)
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        total_downloaded += len(chunk)
            return filename, total_downloaded
        else:
            print(f"\nERROR: Could not download image (HTTP {response.status_code}) for URL: {url}")
            return None, 0
    except Exception as e:
        print(f"\nEXCEPTION: Error downloading image {url}: {e}")
        return None, 0

# --------------------------
# Progress Bar Updater
# --------------------------
def update_progress(current_file, total_files, downloaded_bytes, total_bytes, start_time):
    elapsed = time.time() - start_time
    # Calculate average speed in KB/s
    avg_speed = (downloaded_bytes / 1024) / elapsed if elapsed > 0 else 0
    remaining_bytes = total_bytes - downloaded_bytes
    eta_seconds = remaining_bytes / (downloaded_bytes / elapsed) if downloaded_bytes > 0 else 0
    eta_str = f"{int(eta_seconds//60):02d}:{int(eta_seconds%60):02d}" if avg_speed > 0 else "N/A"
    progress_line = f"Files: {current_file}/{total_files} | Download Speed: {avg_speed:.2f} KB/s | ETA: {eta_str}  "
    sys.stdout.write("\r" + progress_line)
    sys.stdout.flush()

# ================================
# Feature Functions
# ================================
def option_search(config, auth, user_agent):
    print("\n==================================")
    print(" SEARCH MODE: FINDING POSTS")
    print("==================================")
    tags_input = input("Enter tags to search (separated by commas): ")
    user_tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]
    query = build_tag_query(user_tags, config["blacklist"])
    print(f"\nQuerying e621 with: '{query}' ...")
    posts = fetch_posts(query, page=1, auth=auth, user_agent=user_agent)
    if posts:
        print(f"\n--- FOUND {len(posts)} POSTS ON PAGE 1 ---")
        for post in posts:
            post_id = post.get("id")
            rating = post.get("rating")
            file_url = post.get("file", {}).get("url", "N/A")
            print(f"ID: {post_id} | Rating: {rating} | URL: {file_url}")
    else:
        print("No posts found for your query.")
    input("\nPress Enter to return to the main menu...")

def option_scrape(config, auth, user_agent, pool_mode=False):
    mode_text = "POOL SCRAPE" if pool_mode else "TAG SCRAPE"
    print(f"\n==================================")
    print(f" {mode_text}: DOWNLOAD POSTS")
    print("==================================")
    
    if pool_mode:
        pool_id = input("Enter the pool ID: ").strip()
        query = f"pool:{pool_id}"
    else:
        tags_input = input("Enter tags to scrape (separated by commas): ")
        user_tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]
        query = build_tag_query(user_tags, config["blacklist"])
    
    # Scan the query first to show total available posts and pages.
    print("\n[SCAN] Calculating available pages and posts for your query...")
    available_pages, available_posts = scan_query(query, auth, user_agent)
    print(f"[SCAN] Found {available_posts} posts across {available_pages} pages.")
    
    # Ask the user: do they want to scrape all posts, or just a subset?
    pages_input = input("Enter the number of pages to scrape (or type 'all' for all pages): ").strip()
    if pages_input.lower() == "all":
        pages_to_scrape = available_pages
    else:
        try:
            pages_to_scrape = int(pages_input)
            if pages_to_scrape > available_pages:
                pages_to_scrape = available_pages
        except ValueError:
            pages_to_scrape = 1
            print("Invalid input; defaulting to 1 page.")
    
    # Create a subfolder named with the current Unix time inside the working directory.
    session_folder = os.path.join(config["working_directory"], str(int(time.time())))
    try:
        os.makedirs(session_folder)
        print(f"[INFO] Session folder created: {session_folder}")
    except Exception as e:
        print(f"ERROR: Unable to create session folder: {e}")
        return
    
    print(f"[INFO] {available_posts} posts available over {available_pages} pages.")
    if not confirm("Do you wish to continue with the scrape?"):
        print("Scrape cancelled by user.")
        return

    # Clear the screen and begin the scrape with a progress bar.
    os.system("clear" if os.name == "posix" else "cls")
    print_header()

    current_file_count = 0
    downloaded_bytes = 0
    pool_counter = 1  # only used in pool mode
    start_time = time.time()
    total_expected_bytes = 0
    # Pre-calculate expected size from scanned posts:
    scanned_posts = []
    for page in range(1, pages_to_scrape + 1):
        posts = fetch_posts(query, page, auth, user_agent)
        if not posts:
            break
        scanned_posts.extend(posts)
    valid_posts = [p for p in scanned_posts if p.get("file", {}).get("url")]
    for post in valid_posts:
        total_expected_bytes += post.get("file", {}).get("size", 0)

    total_files = len(valid_posts)
    
    # Download each valid post’s image, updating the progress bar on one line.
    for post in valid_posts:
        file_url = post.get("file", {}).get("url")
        if file_url:
            fname, bytes_downloaded = download_image(file_url, session_folder, user_agent,
                                                     pool_counter if pool_mode else None)
            if fname:
                current_file_count += 1
                downloaded_bytes += bytes_downloaded
                if pool_mode:
                    pool_counter += 1
            update_progress(current_file_count, total_files, downloaded_bytes, total_expected_bytes, start_time)
            time.sleep(0.2)  # slight pause for rate limiting
    sys.stdout.write("\n")
    
    # Save metadata into the session folder
    metadata_file = os.path.join(session_folder, "posts_metadata.json")
    try:
        with open(metadata_file, "w") as f:
            json.dump(scanned_posts, f, indent=4)
        print(f"\n[SUCCESS] Metadata saved to {metadata_file}")
    except Exception as e:
        print(f"ERROR: Could not save metadata: {e}")

    input("\nPress Enter to return to the main menu...")

def option_update_blacklist(config):
    print("\n==================================")
    print(" UPDATE BLACKLISTED TAGS")
    print("==================================")
    current = ", ".join(config.get("blacklist", []))
    print(f"Current blacklisted tags: {current if current else 'None'}")
    new_list = input("Enter new blacklist tags (separated by commas): ")
    config["blacklist"] = [t.strip() for t in new_list.split(",") if t.strip()]
    save_config(config)
    input("Blacklist updated. Press Enter to return to the main menu...")

# ================================
# Main Menu Loop
# ================================
def main_menu():
    print_header()
    config = load_config()
    if config is None:
        config = initialize_config()

    auth = None
    if config.get("username") and config.get("api_key"):
        auth = (config["username"], config["api_key"])
    user_agent = f"e621_terminal_scraper/1.0 (by {config.get('nickname', 'anonymous')})"

    while True:
        os.system("clear" if os.name == "posix" else "cls")
        print_header()
        print("MAIN MENU:")
        print(" 1) Search Posts")
        print(" 2) Scrape Posts by Tag")
        print(" 3) Search by Pool")
        print(" 4) Update Blacklisted Tags")
        print(" 5) Exit")
        choice = input("\nEnter your selection (1-5): ").strip()
        if choice == "1":
            option_search(config, auth, user_agent)
        elif choice == "2":
            option_scrape(config, auth, user_agent, pool_mode=False)
        elif choice == "3":
            option_scrape(config, auth, user_agent, pool_mode=True)
        elif choice == "4":
            option_update_blacklist(config)
        elif choice == "5":
            print("\nExiting... Have a great day!")
            break
        else:
            print("Invalid selection. Please choose a valid option.")
            time.sleep(1)

if __name__ == "__main__":
    main_menu()

