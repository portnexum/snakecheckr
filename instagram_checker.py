import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import os

# ─────────────────────────────────────────
USERNAME = input("Enter your Instagram username (without @): ").strip()
# ─────────────────────────────────────────

options = uc.ChromeOptions()
options.add_argument("--lang=en-US")
driver = uc.Chrome(options=options, version_main=148)
wait = WebDriverWait(driver, 15)


def human_scroll(modal, usernames, label):
    last_count = 0
    stall_count = 0
    scroll_counter = 0

    while stall_count < 5:
        items = driver.find_elements(By.XPATH, "//div[@role='dialog']//a[@role='link']")
        if not items:
            items = driver.find_elements(By.XPATH, "//div[@role='dialog']//a[contains(@href, '/')]")

        for item in items:
            try:
                href = item.get_attribute("href")
                if href and "/p/" not in href and "/explore/" not in href:
                    uname = href.strip("/").split("/")[-1]
                    if uname and uname != USERNAME:
                        usernames.add(uname)
            except:
                continue

        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", modal)
        scroll_counter += 1

        if scroll_counter % 20 == 0:
            pause = random.uniform(5, 10)
            print(f"\n  ⏸  Natural pause ({pause:.1f}s)...")
            time.sleep(pause)
        else:
            time.sleep(random.uniform(1.5, 3.5))

        if len(usernames) == last_count:
            stall_count += 1
        else:
            stall_count = 0
            last_count = len(usernames)

        print(f"  Loaded {len(usernames)} {label}...", end="\r")

    return usernames


def scrape_list(label):
    btn_xpaths = [
        f"//a[contains(@href, '/{label}/')]",
        f"//a[contains(text(), '{label}')]",
        f"//span[contains(text(), '{label}')]/ancestor::a",
    ]
    btn = None
    for xpath in btn_xpaths:
        try:
            btn = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            break
        except:
            continue

    if not btn:
        print(f"\n❌ Could not find the '{label}' button. Instagram may have updated its UI.")
        driver.quit()
        exit()

    btn.click()
    time.sleep(random.uniform(2, 3.5))

    modal = None
    modal_xpaths = [
        "//div[@role='dialog']//ul",
        "//div[@role='dialog']//div[contains(@style,'overflow')]",
        "//div[@role='dialog']",
    ]
    for xpath in modal_xpaths:
        try:
            modal = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            break
        except:
            continue

    if not modal:
        print(f"\n❌ Could not open the '{label}' modal. Try refreshing and re-running.")
        driver.quit()
        exit()

    usernames = set()
    usernames = human_scroll(modal, usernames, label)

    close_xpaths = [
        "//div[@role='dialog']//button[@aria-label='Close']",
        "//div[@role='dialog']//button[contains(@class,'close')]",
        "//*[@aria-label='Close']",
    ]
    for xpath in close_xpaths:
        try:
            driver.find_element(By.XPATH, xpath).click()
            break
        except:
            continue

    time.sleep(random.uniform(1.5, 2.5))
    return usernames


driver.get("https://www.instagram.com/")
input("\n🔐 Log in manually in the browser window, then press ENTER to continue...")

# ── STEP 2: Verify logged-in account matches entered username ──
while True:
    driver.get(f"https://www.instagram.com/{USERNAME}/")
    time.sleep(random.uniform(2, 3))

    edit_btn = driver.find_elements(By.XPATH, "//a[contains(@href, '/accounts/edit/')]")
    if edit_btn:
        print(f"\n✅ Confirmed: logged in as @{USERNAME}")
        break
    else:
        print(f"\n⚠️  Could not verify @{USERNAME}. You may be logged into a different account.")
        USERNAME = input("Re-enter your Instagram username (without @): ").strip()

# ── STEP 3: Scrape followers ──
driver.get(f"https://www.instagram.com/{USERNAME}/")
time.sleep(random.uniform(2, 4))
print("\n📥 Scraping your followers...")
followers = scrape_list("followers")

# ── STEP 4: Scrape following ──
driver.get(f"https://www.instagram.com/{USERNAME}/")
time.sleep(random.uniform(2, 4))
print("\n📥 Scraping your following...")
following = scrape_list("following")

# ── STEP 5: Compute results ──
not_following_back = following - followers

print(f"\n\n📊 You follow:          {len(following)}")
print(f"📊 Follow you back:     {len(followers)}")
print(f"🚫 Not following back:  {len(not_following_back)}\n")

if not_following_back:
    for user in sorted(not_following_back):
        print(f"  - https://www.instagram.com/{user}/")
else:
    print("🎉 Everyone you follow, follows you back!")

# ── STEP 6: Save, display, then auto-delete ──
output_file = "not_following_back.txt"
with open(output_file, "w") as f:
    for user in sorted(not_following_back):
        f.write(f"https://www.instagram.com/{user}/\n")

print(f"\n💾 Results saved to {output_file}")
input("\n⚠️  Press ENTER to permanently delete the file from disk...")
os.remove(output_file)
print("🗑️  File deleted. No trace left on disk.")

driver.quit()
print("\n✅ Done. Browser closed.")