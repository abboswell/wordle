import React from 'react';

export default function TopWords({ topKWords }) {
    return (
        <div className="top-words-container">
            <h3>Top Words to Predict</h3>
            <table className="top-words-table">
                <thead>
                    <tr>
                        <th>Word</th>
                        <th>Score</th>
                        <th>Entropy</th>
                        <th>Thompson Sample</th>
                        <th>Prior</th>
                    </tr>
                </thead>
                <tbody>
                    {topKWords.map((wordObj, index) => (
                        <tr key={index}>
                            <td>{wordObj.word}</td>
                            <td>{wordObj.combined_score.toFixed(4)}</td>
                            <td>{wordObj.entropy.toFixed(6)}</td>
                            <td>{wordObj.thompson_sample.toFixed(6)}</td>
                            <td>{wordObj.prior.toFixed(6)}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
