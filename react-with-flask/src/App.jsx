import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Results from './results'
import Home from './home'
import Random from './random'
import './css/results.css'
import './css/home.css'


function App() {

  return (
    <>
      <BrowserRouter>

        <Routes>
          <Route path="/" element={<Home/>} />
          <Route path="/results/:userSteamId" element={<Results/>} />
          <Route path="/random" element={<Random/>} />
        </Routes>

      </BrowserRouter>

    </>
  )
}

export default App
