from time import sleep

from flask import Flask, request, jsonify
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)

# ✅ Hello World Route
@app.route('/hello', methods=['GET'])
def hello():
    return "Hello, World!"

@app.route('/scrape_youtube_post', methods=['GET'])
def scrape_youtube_post():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "❌ Please provide a YouTube post URL using the 'url' query parameter."}), 400

    options = uc.ChromeOptions()
    options.add_argument('--no-first-run --no-service-autorun --password-store=basic')
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--start-maximized")

    driver = uc.Chrome(options=options)

    try:
        driver.get(url)

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "contents"))
        )
        sleep(3)

        # Get comments
        comment_elements = driver.find_elements(By.XPATH, '//yt-attributed-string[@id="content-text"]')
        comments = [el.text.strip() for el in comment_elements if el.text.strip()]

        # Get authors
        author_elements = driver.find_elements(By.XPATH, '//ytd-item-section-renderer[@id="sections"]//a[@id="author-text"]')
        authors = []
        for author in author_elements:
            text = author.text.strip()
            if text:
                authors.append(text)
            else:
                href = author.get_attribute("href")
                if href and "@" in href:
                    handle = href.split("@")[-1]
                    authors.append(f"@{handle}")
                elif href:
                    authors.append(href)
                else:
                    authors.append("[NO AUTHOR]")

        print(authors, comments)
        # Combine data
        combined = []
        for i in range(min(len(authors), len(comments))):
            combined.append({
                "author": authors[i],
                "text": comments[i]
            })

        return jsonify(combined)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        driver.quit()

if __name__ == '__main__':
    app.run(debug=True)
