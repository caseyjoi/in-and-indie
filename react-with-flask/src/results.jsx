import { useState, useEffect } from 'react'
import './css/results.css'
import { useParams, useNavigate, Link } from 'react-router-dom';

/*
const MOCK_API_RESPONSE = {
  "recommendations": [
    {
      "community_links": [
        {
          "platform": "reddit",
          "title": "r/NintendoSwitch Community",
          "url": "https://www.reddit.com/r/NintendoSwitch/"
        },
        {
          "platform": "fandom",
          "title": "Characters | Lethal League Blaze Wiki | Fandom",
          "url": "https://lethal-league-blaze.fandom.com/wiki/Characters"
        },
        {
          "platform": "discord",
          "title": "Join the LLB Stadium Discord Server!",
          "url": "https://discord.com/invite/llbstadium"
        }
      ],
      "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co2toi.jpg",
      "genres": "Fighting, Sport, Indie, Arcade",
      "name": "Lethal League Blaze",
      "rating": 9,
      "steam_link": "https://store.steampowered.com/app/553310",
      "trailer_url": "https://www.youtube.com/watch?v=3Sc-6GOrGNw"
    },
    {
      "community_links": [
        {
          "platform": "reddit",
          "title": "r/videogames Community",
          "url": "https://www.reddit.com/r/videogames/"
        }
      ],
      "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co2tgh.jpg",
      "genres": "Shooter, Platform, Indie, Arcade, Visual Novel",
      "name": "Neon White",
      "rating": 8.6,
      "steam_link": "https://store.steampowered.com/app/1533420",
      "trailer_url": "https://www.youtube.com/watch?v=fDD17TfIn7Y"
    },
    {
      "community_links": [
        {
          "platform": "reddit",
          "title": "r/PokemonInfiniteFusion Community",
          "url": "https://www.reddit.com/r/PokemonInfiniteFusion/"
        },
        {
          "platform": "fandom",
          "title": "Pokémon Infinite Fusion Wiki | Fandom",
          "url": "https://infinitefusion.fandom.com/wiki/Pok%C3%A9mon_Infinite_Fusion_Wiki"
        },
        {
          "platform": "discord",
          "title": "Join the Pokémon Infinite Fusion Discord Server!",
          "url": "https://discord.com/invite/infinitefusion"
        }
      ],
      "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co7k5u.jpg",
      "genres": "Role-playing (RPG), Adventure, Indie",
      "name": "Pokémon Infinite Fusion",
      "rating": 9.8,
      "steam_link": "#",
      "trailer_url": "https://www.youtube.com/watch?v=EAoklAoVwAw"
    },
    {
      "community_links": [
        {
          "platform": "reddit",
          "title": "r/everskiestrashhh Community",
          "url": "https://www.reddit.com/r/everskiestrashhh/"
        },
        {
          "platform": "discord",
          "title": "Join the LURKERS Discord Server!",
          "url": "https://discord.com/invite/lurkers-931526619573657670"
        }
      ],
      "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co9hgu.jpg",
      "genres": "Shooter, Platform, Role-playing (RPG), Simulator, Hack and slash/Beat 'em up, Adventure, Indie",
      "name": "Lurkers",
      "rating": 9.7,
      "steam_link": "https://store.steampowered.com/app/2365750/Lurkers/",
      "trailer_url": "https://www.youtube.com/watch?v=DO1JCgHwNDo"
    },
    {
      "community_links": [
        {
          "platform": "reddit",
          "title": "r/starcontrol Community",
          "url": "https://www.reddit.com/r/starcontrol/"
        }
      ],
      "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co2d9l.jpg",
      "genres": "Simulator, Strategy, Adventure, Indie",
      "name": "Star Control II",
      "rating": 9.6,
      "steam_link": "https://store.steampowered.com/app/358920",
      "trailer_url": "https://www.youtube.com/watch?v=_EedROUdypo"
    }
  ],
  "steam_id": "76561198924137021",
  "user_games": [
    {
      "appid": 383980,
      "genres": "Fighting, Indie",
      "igdb_rating": "7.3",
      "name": "Rivals of Aether",
      "playtime": 25992,
      "trailer": "https://www.youtube.com/watch?v=Y4SFvmJ9NPE",
      "user_steam_id": "76561198924137021"
    },
    {
      "appid": 1372280,
      "genres": "Fighting, Visual Novel",
      "igdb_rating": "7.5",
      "name": "MELTY BLOOD: TYPE LUMINA",
      "playtime": 22246,
      "trailer": "https://www.youtube.com/watch?v=v4cvNNB65uM",
      "user_steam_id": "76561198924137021"
    },
    {
      "appid": 2076010,
      "genres": "Action, Fighting, Visual Novel",
      "igdb_rating": "7.3",
      "name": "UNDER NIGHT IN-BIRTH II Sys:Celes",
      "playtime": 11436,
      "trailer": "https://www.youtube.com/watch?v=w2EEzogHcT4",
      "user_steam_id": "76561198924137021"
    },
    {
      "appid": 105600,
      "genres": "Sandbox, Survival, Adventure",
      "igdb_rating": "8.2",
      "name": "Terraria",
      "playtime": 10861,
      "trailer": "https://www.youtube.com/watch?v=w7uOhFTrrq0",
      "user_steam_id": "76561198924137021"
    },
    {
      "appid": 71340,
      "genres": "Platform, Action, Adventure",
      "igdb_rating": "7.7",
      "name": "Sonic Generations",
      "playtime": 9966,
      "trailer": "https://www.youtube.com/watch?v=L1SzeWaJa94",
      "user_steam_id": "76561198924137021"
    }
  ]
}
  */

function watchURLToEmbedURL(url) {
    if (!url) {
        return "";
    }

    if (url.includes("watch?v=")) {
        let videoID = url.split("watch?v=");
        videoID = videoID[1];
        return `https://www.youtube.com/embed/${videoID}`;
    }
    return url;
};

function Results() {
    const [top5Games, setTop5Games] = useState({});
    const [recommendations, setRecommendations] = useState({})
    const { userSteamId } = useParams()
    const [error, setError] = useState(null)
    const [isLoading, setIsLoading] = useState(true);
    const navigator = useNavigate();



    useEffect(() => {

        const fetchData = async () => {
            try {
                setIsLoading(true);
                setError(null);

                const response = await fetch(`/api/recommendations/${userSteamId}`);

                if (!response.ok) {
                    throw new Error('API fetch failed.');
                }

                const result = await response.json();
                setTop5Games(result.user_games);
                setRecommendations(result.recommendations);
            } catch (err) {
                setError(err.message);
            } finally {
                setIsLoading(false);
            }
        };

        fetchData();

    }, []);

    //mock api response (no longer in the correct place)
    /*
    //MOCK api response and error, functioning userSteamId = "76561198924137021"
    const data = MOCK_API_RESPONSE;
    if (userSteamId == "76561198924137021"){
        setTop5Games(data.user_games);
        setRecommendations(data.recommendations);
    }
    else {
        setTop5Games({});
        setRecommendations({});
        setError("There was an error with the userid.")
    }
    */

    //loads loading page
    if (isLoading) {

        return (
<>

                <div className="container">

                    <div className="card">
                        <div className="top-games"> Loading data, please wait...</div>
                    </div>

                </div>
            </>

        )
    }
    //loads error page
    if (error) {
        return (
            <>

                <div className="container">

                    <div className="card">
                        <div className="top-games">Error: {error}</div>
                        <div className="top-game-details">We could not find your Steam User ID. Please make sure that your profile visibility is set to public and verify that the Steam User ID is correct. </div>
                        
                        <button className="a" onClick> <Link to={'/'}>Return to Home Page</Link></button>
                    </div>

                </div>
            </>
        )
    }


    //loads recommendation page
    return (
        <>
            {/*<pre>{JSON.stringify(top5Games, null, 2)}</pre>*/}
            <div className="dashboard-wrapper">
            <header>
                <h1> Welcome!</h1>
            </header>
            <main>
                <section>
                    <h2> Your 5 top games: </h2>

                    <div className="top-games">

                        {Array.isArray(top5Games) && top5Games.map((game) => (
                            <div key={game.name} className="top-game">
                                <img className="game-cover-thumbnail" src={`https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/${game.appid}/library_600x900.jpg`} />
                                <div className="top-game-details">
                                    <strong> {game.name} </strong>
                                    <span> {game.playtime ? `${game.playtime} minutes` : "Never played"} </span>
                                    <span> {game.genres} </span>
                                </div>

                            </div>
                        )
                        )}

                    </div>
                </section>

                <section>

                    <h2> Based on your top genres, we recommended these games: </h2>


                    {Array.isArray(recommendations) && recommendations.map((rec) => (
                        <div key={rec.name} className="rec-card">
                            <div className="rec-trailer-or-img">
                                {rec.trailer_url ? (
                                    <iframe
                                        width="250"
                                        height="146"
                                        src={watchURLToEmbedURL(rec.trailer_url)}
                                        title="YouTube video player"
                                        frameBorder="0"
                                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                                        referrerPolicy="strict-origin-when-cross-origin"
                                        allowFullScreen>
                                    </iframe>)
                                    : (rec.cover_url && <img src={rec.cover_url} alt="game content" />)}
                            </div>

                            <div className="rec-card-details">
                                <div className="rec-card-header">
                                    <h3 className="game-title"> {rec.name} </h3>
                                </div>

                                <div className="rec-tags">
                                    <span className="tag"> genre: {rec.genres} </span>
                                </div>

                                 <div className="rec-summary">
                                    <span className="summary"> {rec.summary} </span>
                                </div>

                                <div className="rec-rating">
                                    <span className="rating">IGDB Rating: {rec.rating} </span>
                                </div>

                                <div className="community-buttons">
                                    {rec.steam_link && <a href={rec.steam_link} className="btn"> View on Steam </a>}

                                    {Array.isArray(rec.community_links) && rec.community_links.map((community) => (
                                        community.url && <a key={community.url} href={community.url} className="btn"> {community.platform} </a>
                                    ))}
                                </div>


                            </div>
                        </div>
                    ))}
                </section>
                    <div className="card">
                        <button className="a" onClick> <Link to={'/'}>Return to Home Page</Link></button>
                    </div>
            </main>
            </div>
        </>
    )

}

export default Results;