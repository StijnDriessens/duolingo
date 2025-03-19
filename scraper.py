import asyncio
from playwright.async_api import async_playwright
import re

# Felix883985
NAME = "Stijn3s"
URL = f"https://en.duolingo.com/profile/{NAME}"
URL_PROFILE = f"https://en.duolingo.com/profile/{NAME}"
URL_COURSES = f"https://en.duolingo.com/profile/{NAME}/courses"

async def scrape_duolingo():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await page.goto(URL_PROFILE, wait_until="networkidle")
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

async def scrape_duolingo_language():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await page.goto(URL_COURSES, wait_until="networkidle")

            # Locate all the <a class="_1QdQa"> elements (courses)
            courses = await page.locator('a._1QdQa').all()

            for course in courses:
                # Extract the language (course name) from the inner div
                language = await course.locator('div._1sqld').text_content()

                # Extract the XP value
                xp_text = await course.locator('div.vAc4a').text_content()

                # If XP is found, use regex to extract the XP number
                if xp_text and " XP" in xp_text:
                    match = re.search(r"(\d+)\s*XP", xp_text)
                    if match:
                        xp_value = match.group(1)
                        print(f"Course: {language}, XP: {xp_value}")

        except Exception as e:
            print(f"An error occurred: {e}")

        finally:
            await browser.close()

# Run both async functions together
async def main():
    await asyncio.gather(scrape_duolingo(), scrape_duolingo_language())

asyncio.run(main())