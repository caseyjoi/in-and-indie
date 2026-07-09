import { useState, useEffect } from 'react'
import Results from './results'
import './css/results.css'
import './css/App.css'

function App() {

  return (
    <>
     <header> 
        <h1> Welcome!</h1>
    </header>

    <main>
          <Results></Results>
    </main>
          
    </>
  )
}

export default App
