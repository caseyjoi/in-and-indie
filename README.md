# In and Indie



**How you'll keep in touch with the hottest new games and communities on Steam.**

**In and Indie** is a locally hosted website that searches for indie  games on Steam based on a Steam account's most played games. In and Indie presents a decluttered list of indie game recommendations and quick links to their respective YouTube trailers, Steam Store pages, and community links.
___

## Who/what does this project interface with?

### People
This project is meant for any gamers looking for new indie games to play. This project was designed to draw attention to and build community around indie games. 

### Systems (APIs)

* ** YouTube Data API**
* **Steam Web API**
* **Brave Search API**
* **IGDB API**


### Tech Stack

* **Frontend:** React, React Router
* **Backend:** Flask
* **Databases:** SQLite/SQLAlchemy

---
## Inputs
Takes in a Steam User ID (only functions if profile visibility is set to public).

## Outputs
Outputs the Steam User's top 5 games based on playtime, and recommends the user 5 indie games along with the game's Steam Store page, YouTube trailer (if applicable), Reddit subreddit (if applicable), Discord community (if applicable), and Fandom page (if applicable).


---
## Step by Step

1. RECEIVES Steam User ID
2. PULLS top 5 games and their tags
3. SAVES game information in the database
4. SEARCHES for game recommendations on IDGB based on game tags.
5. USES YouTube API to search for trailers and Brave Search API to search for communities
6. DISPLAYS information to user using React
---

## Risks
There is a possibility of being rate-limited for APIs as API calls are frequent.

## Future implementations
* Improve UI and performance
* Revamp product to include generality (removal of Steam dependency)
* Make mobile friendly
