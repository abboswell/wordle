// This is where the entire UI is going to be rendered!!!
import React, { useEffect, useState } from 'react';   
import useWordle from '../hooks/useWordle';
import Grid from './grid';
import Keypad from './keypad';
import PastWords from './pastwords';
import TopWords from './topkwords';


export default function Wordle( { solution , restartGame, numWords}) {

    const {currentGuess, handleKeyup, guesses, isCorrect, turn, usedKeys, topKWords, history, numWordsLeft} = useWordle(solution, restartGame);
    const [wordsLeft, setWordsLeft] = useState(numWords);

    useEffect(() => {
        window.addEventListener('keyup', handleKeyup);

        return () => {
            window.removeEventListener('keyup', handleKeyup);
        }
    }, [handleKeyup]);

    useEffect(() => {
        console.log(guesses, turn, isCorrect);
    }, [guesses, turn, isCorrect]);

    useEffect(() => {
        if (numWordsLeft !== undefined) {
            setWordsLeft(numWordsLeft); // Update wordsLeft dynamically
        }
    }, [numWordsLeft]);

    return (
        <div className="wordle-container">
            {/* Left Panel: Past Words */}
            <div className="left-panel">
                <PastWords history={history} />
            </div>

            {/* Main Content: Grid and Keypad */}
            <div className="main-content">
                <div>

                    <div>Solution - {solution}</div>
                    <div>Words Left - {wordsLeft}</div>

                </div>
                <Grid currentGuess={currentGuess} guesses={guesses} turn={turn} />
                <Keypad usedKeys={usedKeys} />
            </div>

            {/* Right Panel: Top K Words */}
            <div className="right-panel">
                <TopWords topKWords={topKWords} />
            </div>

            {/* Restart Button */}
            {isCorrect && <button onClick={restartGame}>Restart Game</button>}
        </div>
    );
}