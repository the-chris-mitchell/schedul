import React, { useState, useEffect } from 'react';

function GetFestivals() {
    const [festivals, setFestivals] = useState([]);

    useEffect(() => {
        fetch('http://localhost:8000/festivals')
            .then(response => response.json())
            .then(data => setFestivals(data));

    // empty dependency array means this effect will only run once (like componentDidMount in classes)
    }, []);

    return (
        <div>
            {festivals.map(festival => (
            <div className="card text-center m-3">
                <h5 className="card-header">{festival.full_name}</h5>
            </div>
            ))}
        </div>        
    );
}

export { GetFestivals };