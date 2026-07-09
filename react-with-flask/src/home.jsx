import { useState, useEffect } from 'react'
import './css/home.css'

function Home(){
    return (
        <div  className="container">

        <div className="card">
            <h1> In and Indie </h1>

            <p> Discover indie games based on your Steam library. </p>

            <input type="text" placeholder="Enter Steam User ID"/>

            <button> Find Reccomendations </button>
        </div>

    </div>
    )
}
export default Home