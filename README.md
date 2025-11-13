# Lightnovel Crawler for QPython

An app to download novels from online sources and generate e-books, specifically tailored for the QPython environment on Android.

## Changes for QPython Version

This version of `lightnovel-crawler` has been modified to run on Python 3.4 within QPython. Due to these constraints, several features have been changed or removed:

*   **Removed Platforms:** Support for all platforms other than QPython has been removed. This includes bots for Discord and Telegram, as well as deployment methods for Docker and Heroku.
*   **Removed `wuxiaworld.com` Support:** The crawler for `wuxiaworld.com` has been removed due to incompatible dependencies.
*   **Cloudflare Bypass:** The `cloudscraper` library has been replaced with a manual, cookie-based method for bypassing Cloudflare's anti-bot protection.

## Installation on QPython

1.  **Download the Repository:** Download the `lightnovel-crawler` repository as a ZIP file and extract it to a location on your Android device.
2.  **Install Dependencies:** Open QPython and navigate to the extracted directory. Run the following command to install the necessary libraries:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Install Calibre (Optional):** This application uses Calibre to convert ebooks. To generate formats other than EPUB, text, and web, you will need to have Calibre installed on a computer and transfer the generated files there for conversion.

## Usage

1.  **Navigate to the Directory:** Open a terminal in QPython and navigate to the `lightnovel-crawler` directory.
2.  **Run the Application:** Start the interactive console by running:
    ```bash
    python lncrawl
    ```
3.  **Follow the Prompts:** The application will guide you through the process of searching for a novel, selecting chapters, and downloading them.

## Bypassing Cloudflare

To download novels from websites protected by Cloudflare, you will need to manually provide a Cloudflare clearance cookie.

1.  **Obtain the Cookie:**
    *   Open a web browser on your computer.
    *   Navigate to the website you want to download from and solve the Cloudflare challenge.
    *   Open your browser's developer tools (usually by pressing F12).
    *   Go to the "Application" or "Storage" tab and find the cookies for the website.
    *   Copy the value of the `cf_clearance` cookie.
2.  **Set the Environment Variable:** In your QPython terminal, set the `cf_cookie` environment variable to the value you copied:
    ```bash
    export cf_cookie="your_cf_clearance_cookie_value"
    ```
3.  **Run the Application:** You can now run the `lightnovel-crawler` as usual. The application will use the provided cookie to bypass Cloudflare.

## Supported Output Formats

- JSON
- EPUB
- TEXT
- WEB
- And many more if you have Calibre installed on a computer.
