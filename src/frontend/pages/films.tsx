import React, { useState, useEffect } from 'react';
// import { Table } from 'semantic-ui-react';

function GetFilms() {
    const [films, setFilms] = useState([]);

    useEffect(() => {
        fetch('http://localhost:8000/festivals/nziff/films')
            .then(response => response.json())
            .then(data => setFilms(data));

    // empty dependency array means this effect will only run once (like componentDidMount in classes)
    }, []);

    return (
        <div>
            {films.map(film => (
            <div className="card text-center m-3">
                <h5 className="card-header">{film.name}</h5>
                <div className="card-body">
                    {film.runtime} minutes, {film.year}
                </div>
            </div>
            ))}
        </div>        
    );
    

    // return (
    //     <Table celled striped>
    //     <Table.Header>
    //       <Table.Row>
    //         <Table.HeaderCell colSpan='3'>Films</Table.HeaderCell>
    //       </Table.Row>
    //     </Table.Header>
    
    //     <Table.Body>
    //     {films.map(film => (
    //       <Table.Row>
    //         <Table.Cell>{film.name}</Table.Cell>
    //         <Table.Cell>{film.runtime} minutes</Table.Cell>
    //         <Table.Cell>{film.year}</Table.Cell>
    //       </Table.Row>
    //       ))}
    //     </Table.Body>
    //   </Table>
    // );
}

export { GetFilms };