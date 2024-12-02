import { useState, useEffect } from 'react';

const useWordle = (solution, restartGame) => {
    const [turn, setTurn] = useState(0);
    const [currentGuess, setCurrentGuess] = useState('');
    const [guesses, setGuesses] = useState([...Array(6)]);
    const [history, setHistory] = useState([]);
    const [isCorrect, setIsCorrect] = useState(false);
    const [gameWon, setGameWon] = useState(false);
    const [recommendation, setRecommendation] = useState(null);
    const [hasFetchedRecommendation, setHasFetchedRecommendation] = useState(false);
    const [usedKeys, setUsedKeys] = useState({});
    const [topKWords, setTopKWords] = useState([]);
    const [numWordsLeft, setNumWordsLeft] = useState(12972);

    const resetState = () => {
        setTurn(0);
        setCurrentGuess('');
        setGuesses([...Array(6)]);
        setHistory([]);
        setIsCorrect(false);
        setGameWon(false);
        setRecommendation(null);
        setUsedKeys({});
        setHasFetchedRecommendation(false);
    };

    const BASE_URL = 'http://127.0.0.1:5000';

    const formatGuess = (guess, feedback) => {
        const colors = { 2: 'green', 1: 'yellow', 0: 'gray' };
        const result = [];
        for (let i = 0; i < guess.length; i++) {
            result.push({
                letter: guess[i],
                color: colors[feedback[i]],
            });
        }
        return result;
    };

    const fetchRecommendation = async () => {
        if (isCorrect || hasFetchedRecommendation) {
            console.log('No need to fetch recommendation');
            return;
        }

        try {
            const response = await fetch(`${BASE_URL}/recommend`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
            });
            const data = await response.json();

            if (data.top_k_words) {
                setTopKWords(data.top_k_words); // Save the top K words
                setRecommendation(data.top_word.word); // Save the top recommended word
                setHasFetchedRecommendation(true);
            }
        
        } catch (err) {
            console.error('Error fetching recommendation:', err);
        }
    };
    useEffect(() => {
        console.log('Updated Top K Words:', topKWords);
    }, [topKWords]);

    const validateWord = async (word) => {
        const response = await fetch(`${BASE_URL}/validate-word`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ word }),
        });
        const data = await response.json();
        return data.valid;
    };

    const updateUsedKeys = (formattedGuess) => {
        setUsedKeys((prev) => {
            const newKeys = { ...prev };
            formattedGuess.forEach((l) => {
                const curColor = newKeys[l.letter];
                if (l.color === 'green') {
                    newKeys[l.letter] = 'green';
                } else if (l.color === 'yellow' && curColor !== 'green') {
                    newKeys[l.letter] = 'yellow';
                } else if (l.color === 'gray' && curColor !== 'green' && curColor !== 'yellow') {
                    newKeys[l.letter] = 'gray';
                }
            });
            return newKeys;
        });
    };

    const submitGuess = async () => {
        if (currentGuess.length !== 5) {
            console.log('Guess must be 5 letters!');
            return;
        }
    
        try {
            const response = await fetch(`${BASE_URL}/guess`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ guess: currentGuess }),
            });

            const data = await response.json();

            setNumWordsLeft(data.num_remaining_words);
    
            if (data.message) {
                // Success response
                console.log(data.message); // "Congratulations! You solved it!"
                const formattedGuess = formatGuess(currentGuess, [2, 2, 2, 2, 2]); // All green
                
                // Update the guesses array with the correct guess
                setGuesses((prevGuesses) => {
                    const newGuesses = [...prevGuesses];
                    newGuesses[turn] = formattedGuess;
                    return newGuesses;
                });
    
                // Update the used keys to turn all keys green
                setUsedKeys((prevKeys) => {
                    const newKeys = { ...prevKeys };
                    formattedGuess.forEach((l) => {
                        newKeys[l.letter] = 'green';
                    });
                    return newKeys;
                });
    
                const topWordEntry = topKWords.find((entry) => entry.word === currentGuess);
                setHistory((prevHistory) => [
                    ...prevHistory,
                    {
                        word: currentGuess,
                        score: topWordEntry?.combined_score || 0, // Fetch the combined_score
                        entropy: topWordEntry?.entropy || 0,
                        thompsonSample: topWordEntry?.thompson_sample || 0,
                        prior: topWordEntry?.prior || 0,
                    },
                ]);

                setIsCorrect(true);
                setGameWon(true); // This will trigger the useEffect for the alert
            } else if (data.feedback) {
                // Handle non-successful feedback case
                console.log("Printing Data from submitGuess", data);
                console.log('Feedback:', data.feedback);
    
                const formattedGuess = formatGuess(currentGuess, data.feedback);
                console.log('Formatted Guess:', formattedGuess);
    
                setGuesses((prevGuesses) => {
                    const newGuesses = [...prevGuesses];
                    newGuesses[turn] = formattedGuess;
                    return newGuesses;
                });
    
                const topWordEntry = topKWords.find((entry) => entry.word === currentGuess);
                setHistory((prevHistory) => [
                    ...prevHistory,
                    {
                        word: currentGuess,
                        score: topWordEntry?.combined_score || 0, // Fetch the combined_score
                        entropy: topWordEntry?.entropy || 0,
                        thompsonSample: topWordEntry?.thompson_sample || 0,
                        prior: topWordEntry?.prior || 0,
                    },
                ]);

                setTurn((prevTurn) => prevTurn + 1);
    
                // Update the used keys based on feedback
                updateUsedKeys(formattedGuess);
                setCurrentGuess('');
                setHasFetchedRecommendation(false);

            } else {
                console.error('Unexpected response:', data);
            }
        } catch (err) {
            console.error('Error submitting guess:', err);
        }
    };

    const handleKeyup = ({ key }) => {
        if (key === 'Enter') {
            if (turn > 5 || isCorrect) {
                return;
            }
            if (history.includes(currentGuess.toLowerCase())) {
                console.log('You already tried that word!');
                return;
            }
            if (currentGuess.length !== 5) {
                console.log('Guess must be 5 letters long!');
                return;
            }
            validateWord(currentGuess).then((isValid) => {
                if (!isValid) {
                    console.log('Word is not valid!');
                    return;
                }
                submitGuess();
            });
        } else if (key === 'Backspace') {
            setCurrentGuess((prev) => prev.slice(0, -1));
        } else if (/^[A-Za-z]$/.test(key) && currentGuess.length < 5) {
            setCurrentGuess((prev) => prev + key.toLowerCase());
        }
    };

    useEffect(() => {
        if (solution && !isCorrect && !hasFetchedRecommendation) {
            fetchRecommendation();
        }
    }, [solution, isCorrect, hasFetchedRecommendation]);

    useEffect(() => {
        if (gameWon) {

            setUsedKeys((prevKeys) => {
                const newKeys = { ...prevKeys };
                currentGuess.split('').forEach((letter) => {
                    newKeys[letter] = 'green';
                });
                return newKeys;
            });

            setTimeout(() => {
                alert('Congratulations! You solved it! Click OK to start a new game.');
                resetState();
                restartGame();
            }, 300);
        }
    }, [gameWon, restartGame]);

    return { turn, currentGuess, guesses, isCorrect, usedKeys, history, topKWords, numWordsLeft, handleKeyup };
};

export default useWordle;
