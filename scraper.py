import asyncio
from playwright.async_api import async_playwright

NAME = "Stijn3s"
URL = f"https://en.duolingo.com/profile/{NAME}"

async def scrape_duolingo():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await page.goto(URL, wait_until="networkidle")
            text_content = await page.inner_text("body")
            lines = text_content.split("\n")

            def get_lines_above(term, count=1):
                try:
                    index = next(i for i, line in enumerate(lines) if term in line)
                    return "\n".join(lines[max(index - count, 0):index])
                except StopIteration:
                    return f'Text "{term}" not found.'

            data = {
                "name": get_lines_above("Day streak", 6),
                "dayStreak": get_lines_above("Day streak", 1),
                "totalXP": get_lines_above("Total XP", 1),
                "league": get_lines_above("Current league", 1),
                "top3finishes": get_lines_above("Top 3 finishes", 1)
            }

            # Print results
            for key, value in data.items():
                print(f"{key}: {value}")
        
        except Exception as e:
            print(f"An error occurred: {e}")
        
        finally:
            await browser.close()

asyncio.run(scrape_duolingo())