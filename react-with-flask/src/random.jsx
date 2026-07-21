import { useState, useEffect } from 'react'
import './css/results.css'
import { useParams, useNavigate, Link } from 'react-router-dom';


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

function Random() {
  const [recommendations, setRecommendations] = useState({})
  const [error, setError] = useState(null)
  const [isLoading, setIsLoading] = useState(true);
  const navigator = useNavigate();



  useEffect(() => {

    const fetchData = async () => {
      try {
        setIsLoading(true);
        setError(null);

        const response = await fetch(`/api/random`);

        if (!response.ok) {
          throw new Error('API fetch failed.');
        }

        const result = await response.json();
        setRecommendations(result.random_games);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();

  }, []);



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
            <div className="top-game-details">Sorry, we had trouble loading your recommendations Please try again later.</div>

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

            <h2> We pulled 3 random games for you. </h2>

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

export default Random;