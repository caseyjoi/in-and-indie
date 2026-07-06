# In and Indie



**How you'll keep in touch with the hottest new games and communities on Steam.**

**In and Indie** is a CLI that searches for the latest and hottest games on Steam and connects you with those you find most interesting. In and Indie presents a decluttered catalog of new games and their latest news.
___

## Who/what does this project interface with?

### People
This project is designed for gamers and developers who want to keep in touch with the latest games and their communities. This is perfect for those who want to quickly check up on the video game industry.

### Systems (APIs)

* **Steam Internal API**
* **Steam Web API**
* **Brave Search API**


### Hardware

Runs in your terminal!

---
## Inputs
Prompts the user to navigate through pages of lists, and allows users to select specifc games to view more information for.

## Outputs
Outputs pages of upcoming video games and their summary, publishers, price, and release date. Once prompted, the program also returns the latest news for that game once prompted. 


---
## Step by Step

1. USES Brave search API to find Steam Shop URLS of up and coming video games.
2. STRIPS the URLS for game IDs.
3. CROSS REFERENCES IDs with Steam Internal API to retrieve game metadata.
4. STORES IDs and metadata in a database for fast access
5. USES Steam Web API to return the latest update/news for selected games
---

## Risks
There runs the possibility of being rate limited however we have mitigated it by accessing games from our database when needed.  

## Success
We consider this a success when it can:
- Returns an updated list of up and coming steam games
- Returns the latest news associated with the games
- Presents a streamlined and decluttered experience for exploring new games
