import React, { useState } from 'react';

export default function Keypad({ usedKeys = {} }) {
    const cur_letters = [
        { key: "a" },
        { key: "b" },
        { key: "c" },
        { key: "d" },
        { key: "e" },
        { key: "f" },
        { key: "g" },
        { key: "h" },
        { key: "i" },
        { key: "j" },
        { key: "k" },
        { key: "l" },
        { key: "m" },
        { key: "n" },
        { key: "o" },
        { key: "p" },
        { key: "q" },
        { key: "r" },
        { key: "s" },
        { key: "t" },
        { key: "u" },
        { key: "v" },
        { key: "w" },
        { key: "x" },
        { key: "y" },
        { key: "z" },
    ];

    const [letters, setLetters] = useState(cur_letters);

    return (
        <div className="keypad">
            {letters.map((l) => {
                const color = usedKeys[l.key] || "white"; // Safe access with optional chaining
                return (
                    <div key={l.key} className={`key ${color}`}>
                        {l.key}
                    </div>
                );
            })}
        </div>
    );
}
