import { useState, useEffect } from 'react'
import {Link} from 'react-router-dom'
import './css/home.css'



function Home(){
    const[userSteamId, setUserSteamId] = useState("")
    return (
        <div className="container">

        <div className="card">
            <h1> In and Indie </h1>

            <p> Discover indie games based on your Steam library. </p>

            <input type="text" placeholder="Enter Steam User ID" value={userSteamId} onChange={(change) => setUserSteamId(change.target.value)}/>

            <button className="a" onClick> <Link to={`/results/${userSteamId}`}> Find Reccomendations </Link></button>
        </div>

    </div>
    )
}
export default Home