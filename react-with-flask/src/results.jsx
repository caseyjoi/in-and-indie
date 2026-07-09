import { useState, useEffect } from 'react'
import './css/results.css'
/*
const MOCK_API_RESPONSE = {
  "recommendations": [
    {
      "community_links": [
        {
          "platform": "reddit",
          "title": "r/NintendoSwitch on Reddit: WARNING: Do not buy Lethal League Blaze unless you want an incomplete version of the game.",
          "url": "https://www.reddit.com/r/NintendoSwitch/comments/cd7792/warning_do_not_buy_lethal_league_blaze_unless_you/"
        },
        {
          "platform": "fandom",
          "title": "Lethal League Blaze | Lethal League Wiki | Fandom",
          "url": "https://lethal-league.fandom.com/wiki/Lethal_League_Blaze"
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
          "title": "r/videogames on Reddit: Why You Should Play Neon White",
          "url": "https://www.reddit.com/r/videogames/comments/1kdb4dz/why_you_should_play_neon_white/"
        },
        {
          "platform": "fandom",
          "title": "Neon White (character) | Neon White Wiki | Fandom",
          "url": "https://neonwhite.fandom.com/wiki/Neon_White_(character)"
        },
        {
          "platform": "discord",
          "title": "Join the NEON WHITE - OFFICIAL DISCORD Discord Server!",
          "url": "https://discord.com/invite/Y7ZEHkwUDv"
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
          "title": "r/PokemonInfiniteFusion on Reddit: How do I get Pokémon Infinite Fusion?",
          "url": "https://www.reddit.com/r/PokemonInfiniteFusion/comments/196z553/how_do_i_get_pok%C3%A9mon_infinite_fusion/"
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
          "title": "r/FanFiction on Reddit: About Lurkers",
          "url": "https://www.reddit.com/r/FanFiction/comments/1bvizrp/about_lurkers/"
        },
        {
          "platform": "fandom",
          "title": "Lurkers | Jak and Daxter Wiki | Fandom",
          "url": "https://jakanddaxter.fandom.com/wiki/Lurkers"
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
          "title": "r/starcontrol on Reddit: Star Control II - The Ur-Quan Masters: First time player's review 31 years after release",
          "url": "https://www.reddit.com/r/starcontrol/comments/168jvoh/star_control_ii_the_urquan_masters_first_time/"
        },
        {
          "platform": "fandom",
          "title": "Star Control II - Codex Gamicus - Humanity's collective gaming knowledge at your fingertips.",
          "url": "https://gamicus.fandom.com/wiki/Star_Control_II"
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
      "appid": 105600,
      "igdb_rating": 8.2,
      "name": "Terraria",
      "playtime": 10861,
      "tag1": "33:themes",
      "tag2": "21:themes",
      "tag3": "31:genres",
      "trailer": "https://www.youtube.com/watch?v=w7uOhFTrrq0",
      "user_steam_id": "76561198924137021"
    },
    {
      "appid": 71340,
      "igdb_rating": 7.7,
      "name": "Sonic Generations",
      "playtime": 9966,
      "tag1": "8:genres",
      "tag2": "1:themes",
      "tag3": "31:genres",
      "trailer": "https://www.youtube.com/watch?v=L1SzeWaJa94",
      "user_steam_id": "76561198924137021"
    },
    {
      "appid": 1372280,
      "igdb_rating": 7.5,
      "name": "MELTY BLOOD: TYPE LUMINA",
      "playtime": 22246,
      "tag1": "4:genres",
      "tag2": "4:genres",
      "tag3": "34:genres",
      "trailer": "https://www.youtube.com/watch?v=v4cvNNB65uM",
      "user_steam_id": "76561198924137021"
    },
    {
      "appid": 383980,
      "igdb_rating": 7.3,
      "name": "Rivals of Aether",
      "playtime": 25992,
      "tag1": "4:genres",
      "tag2": "4:genres",
      "tag3": "32:genres",
      "trailer": "https://www.youtube.com/watch?v=Y4SFvmJ9NPE",
      "user_steam_id": "76561198924137021"
    },
    {
      "appid": 2076010,
      "igdb_rating": 7.3,
      "name": "UNDER NIGHT IN-BIRTH II Sys:Celes",
      "playtime": 11436,
      "tag1": "1:themes",
      "tag2": "4:genres",
      "tag3": "34:genres",
      "trailer": "https://www.youtube.com/watch?v=w2EEzogHcT4",
      "user_steam_id": "76561198924137021"
    }
  ]
}
*/
function watchURLToEmbedURL(url){
        if (!url) {
            return "";
        }

        if (url.includes("watch?v=")){
            let videoID = url.split("watch?v=");
            videoID = videoID[1];
            return `https://www.youtube.com/embed/${videoID}`;
        }
        return url;
    };

function Results() {
    const [top5Games, setTop5Games] = useState({});
    const [recommendations, setRecommendations] = useState({})

    useEffect(() => {
        //Commented out actual API call
        //current hardcoding a specific steam USER -> implement fetch(`/api/events/${day}`) format*/
        
        fetch(`/api/recommendations/76561198924137021`)
        .then(res => res.json())
        .then(data => {
            setTop5Games(data.user_games);
            setRecommendations(data.recommendations);
        });
        
        /*
        //MOCK api response
        const data = MOCK_API_RESPONSE;
        setTop5Games(data.user_games);
        setRecommendations(data.recommendations); 
        */
    }, []);

    return (
        <>
            {/*<pre>{JSON.stringify(top5Games, null, 2)}</pre>*/}

            <section>
                <h2> Your 5 top games: </h2>



                <div className="top-games">

                    {Array.isArray(top5Games) && top5Games.map((game) => (
                        <div key={game.name} className="top-game">
                            <img className="game-cover-thumbnail" src={`https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/${game.appid}/library_600x900.jpg`}/>
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


            {Array.isArray(recommendations) && recommendations.map ((rec) => (
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
                    : (rec.cover_url && <img src={rec.cover_url} alt ="game content"/>)}
                </div>

                <div className="rec-card-details">
                    <div className="rec-card-header"> 
                        <h3 className="game-title"> {rec.name} </h3>
                    </div> 

                    <div className="rec-tags">
                        <span className="tag"> genre: {rec.genres} </span>
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
        </>
    )

}

export default Results;