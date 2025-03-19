const puppeteer = require('puppeteer');
const name = 'Stijn3s';

//Felix883985
//Stijn3s

(async () => {
    const browser = await puppeteer.launch({ headless: true }); // Set to true for headless mode
    const page = await browser.newPage();

    try {
        await page.goto('https://en.duolingo.com/profile/' + name, { waitUntil: 'networkidle2', timeout: 60000 });

        // Extract text content and find the relevant information
        const data = await page.evaluate(() => {
            const textContent = document.body.innerText;
            const lines = textContent.split('\n');

            // Helper function to get lines above a specific term
            function getLinesAbove(term, count = 1) {
                const index = lines.findIndex(line => line.includes(term));
                if (index > 0) {
                    return lines.slice(Math.max(index - count, 0), index).join('\n');
                } else {
                    return `Text "${term}" not found.`;
                }
            }

            return {
                name: getLinesAbove('Day streak', 6),
                dayStreak: getLinesAbove('Day streak', 1),
                totalXP: getLinesAbove('Total XP', 1),
                league: getLinesAbove('Current league', 1),
                top3finishes: getLinesAbove('Top 3 finishes', 1)
            };
        });

        // Print results
        console.log('Name:' + data.name);
        console.log('Day streak:' + data.dayStreak);
        console.log('Total XP:' + data.totalXP);
        console.log('League:' + data.league);
        console.log('Top 3 finishes:' + data.top3finishes);

    } catch (error) {
        console.error('An error occurred:', error);
    } finally {
        await browser.close();
    }
})();
