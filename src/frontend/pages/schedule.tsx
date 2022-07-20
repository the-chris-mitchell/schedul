import React, { useState, useEffect } from 'react';
// import { Table } from 'semantic-ui-react';

function GetSchedule() {
    const [schedule, setSchedule] = useState([]);

    useEffect(() => {
        fetch('http://localhost:8000/festivals/nziff/schedule')
            .then(response => response.json())
            .then(data => setSchedule(data));

    // empty dependency array means this effect will only run once (like componentDidMount in classes)
    }, []);

    return (
        <div>
        {schedule.map(film => (
            <div>
            {film.formatted}
            </div>
        ))}  
        </div>  
    );

}

export { GetSchedule };