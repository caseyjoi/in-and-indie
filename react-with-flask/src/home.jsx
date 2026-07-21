import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import './css/home.css'



function Home() {
    const [userSteamId, setUserSteamId] = useState("")
    return (
        <div>
        <div className="container">

            <div className="card">
                <h1> In and Indie </h1>

                <p> Discover indie games based on your Steam library. </p>

                <input type="text" placeholder="Enter Steam User ID" value={userSteamId} onChange={(change) => setUserSteamId(change.target.value)} />

                <button className="a" onClick> <Link to={`/results/${userSteamId}`}> Find Reccomendations </Link></button>
                  <p> </p>
                  <p> Don't have a Steam library?</p>
                <button className="a" onClick> <Link to={`/random`}> Random Recommendations </Link></button>
                
            </div>


        </div>

        <div className="faq-container">
      <details>

        <summary>Where do I find my steam ID?</summary>
        <div className="faq-content">
          <p>Open the Steam app and click your username on the top right. Select Account Details. Your Steam ID sits underneath your displayed username in gray. Alternatively, you can find your Steam ID in your profile URL. When on your profile page, your Steam ID is the 17-digit number at the end of the URL.
</p>
        </div>
      </details> 
    </div>
</div>

    )
}
export default Home