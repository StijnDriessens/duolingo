import os
from pymongo import MongoClient
import asyncio
from playwright.async_api import async_playwright
import re
from datetime import datetime
from typing import List

USERNAME = os.getenv("MONGO_USERNAME")
PASSWORD = os.getenv("MONGO_PASSWORD")
CLUSTER = os.getenv("MONGO_CLUSTER")
NAME = os.getenv("DUOLINGO_USERNAME")
URL_PROFILE = f"https://en.duolingo.com/profile/{NAME}"
URL_COURSES = f"https://en.duolingo.com/profile/{NAME}/courses"

# Connect to MongoDB Atlas
try:
    uri = f"mongodb+srv://{USERNAME}:{PASSWORD}@{CLUSTER}.ijztv.mongodb.net/Duolingo?retryWrites=true&w=majority&appName=Duolingo"
    client = MongoClient(uri)
    db = client.Duolingo  # database
    collection = db.Duolingo  # collection name
    print("Successfully connected to MongoDB")
except ConnectionError as e:
    print(f"Error connecting to MongoDB: {e}")
    exit(1)

class Course:
    def __init__(self, language, courseXP):
        self.language = language
        self.courseXP = courseXP

class Profile:
    def __init__(self, name, dayStreak, totalXP, league, leagueWeek, top3Finishes, courses: List[Course]):
        self.name = name
        self.dayStreak = dayStreak
        self.totalXP = totalXP
        self.league = league
        self.leagueWeek = leagueWeek
        self.top3Finishes = top3Finishes
        self.courses = courses

def save(profile: Profile):
    try:
        new_record = {
            "name": profile.name,
            "dayStreak": profile.dayStreak,
            "totalXP": profile.totalXP,
            "league": f"{profile.league} Week {profile.leagueWeek}",
            "top3Finishes": profile.top3Finishes,
            "course": profile.courses[0].language,
            "courseXP": profile.courses[0].courseXP,
            "createdAt": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        result = collection.insert_one(new_record)
        print(f"Inserted document with _id: {result.inserted_id}")
    except Exception as e:
        print(f"An error occurred while saving the data: {e}")

async def scrape_duolingo_account():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        result = ""

        try:
            # Go to the profile URL and wait until the page is loaded
            await page.goto(URL_PROFILE, wait_until="networkidle")

            # Extract the username - Adjusted to follow the same pattern
            name_locator = page.locator('h1[data-test="profile-username"] span')
            await name_locator.wait_for(state="attached")  # Wait until the element is attached
            name = await name_locator.text_content()

            if not name:
                raise ValueError("Username not found!")

            # Extract statistics sections - follow the same approach for waiting and extracting
            stats_sections = await page.locator('div._2Hzv5').all()

            # Initialize statistics variables
            day_streak = total_xp = league = week = top_3_finishes = "N/A"

            # Loop through statistics sections to extract values
            for section in stats_sections:
                # Wait for the section to be attached
                await section.wait_for(state="attached")

                # Extract label (e.g., "Day streak", "Total XP", etc.)
                label_locator = section.locator('div._3oUUc')
                await label_locator.wait_for(state="attached")
                label = await label_locator.text_content()

                # Extract value (e.g., "700", "72071", etc.)
                value_locator = section.locator('h4')
                await value_locator.wait_for(state="attached")
                value = await value_locator.text_content()

                # Match the label and assign the correct value
                if label == "Day streak":
                    day_streak = value
                elif label == "Total XP":
                    total_xp = value
                elif label == "Top 3 finishes":
                    top_3_finishes = value
                elif label == "Current league":
                    league = value
                else:
                    print(f"label error: {label}")

            # Extract the week number
            week_locator = page.locator('text=Week')
            await week_locator.wait_for(state="attached")
            week_text = await week_locator.text_content()

            # Use regex to find the number after "Week"
            match = re.search(r'Week (\d+)', week_text)
            if match:
                week = match.group(1)  # Extracts the number after "Week"

            # Print out the extracted information
            print(f"Name: {name}")
            print(f"DayStreak: {day_streak}")
            print(f"TotalXP: {total_xp}")
            print(f"League: {league} {week}")
            print(f"Top3Finishes: {top_3_finishes}")

            result = Profile(name, day_streak, total_xp, league, week, top_3_finishes, await scrape_duolingo_courses())
        except Exception as e:
            print(f"An error occurred while webscraping the data: {e}")
        finally:
            await browser.close()
            return result

async def scrape_duolingo_courses():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        result = []

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
                        result.append(Course(language, xp_value))

        except Exception as e:
            print(f"An error occurred while webscraping the data: {e}")

        finally:
            await browser.close()
            return result

# Run both async functions together
async def main():
    save(await scrape_duolingo_account())

asyncio.run(main())