import { useEffect, useState } from 'react';
import Wordle from './components/wordle';

function App() {
  const [solution, setSolution] = useState(null);
  const [numWordsLeft, setNumWordsLeft] = useState(null);


  const fetchSolution = async () => {
    try {
      const res = await fetch('http://localhost:5000/solution');
      if (!res.ok) {
        // If the solution endpoint fails, start a new game
        if (res.status === 400) {
          await fetch('http://localhost:5000/new-game', { method: 'POST' });
          const newRes = await fetch('http://localhost:5000/solution');

          if (!newRes.ok) throw new Error('Failed to fetch solution after starting a new game');
          const newData = await newRes.json();

          console.log(newData); // Check if `word_count` is present

          setSolution(newData.solution);
          setNumWordsLeft(newData.words_left);

        } else {
          throw new Error('Failed to fetch solution');
        }
      } else {
        const data = await res.json();
        setSolution(data.solution);
        setNumWordsLeft(data.words_left);
      }
    } catch (err) {
      console.error(err.message);
    }
  };

  useEffect(() => {
    fetchSolution();
  }, [setSolution]);


  const restartGame = async () => {
    setSolution(null); // Temporarily unset the solution to prevent unnecessary renders
    await fetch('http://localhost:5000/new-game', { method: 'POST' });
    fetchSolution(); // Fetch a new solution
  };
  

  return (
    <div>
      <h1>Wordle Solver With Information Theory</h1>
      
      {solution ? <Wordle solution={solution} restartGame={restartGame} numWords = {numWordsLeft} /> : <p>Loading solution...</p>}
    </div>
  );

}

export default App;