'use client'

import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

import React, { useEffect, useState } from 'react';

async function getFestivals() {
  const res = await fetch('https://schedul-production.up.railway.app/festivals');
  if (!res.ok) {
    throw new Error('Failed to fetch data');
  }
  return res.json();
}

async function getSchedule(festival_id: string) {

  const payload = {
    "excluded_dates": [
      "2023-06-07",
      "2023-06-08",
      "2023-06-09",
      "2023-06-16",
      "2023-06-17",
      "2023-06-18",
      "2023-06-19",
      "2023-06-20",
      "2023-06-21",
      "2023-06-22"
    ],
    "time_preferences": [
      {
        "day_bucket": "weekend",
        "time_bucket": "morning"
      },
      {
        "day_bucket": "weekday",
        "time_bucket": "evening"
      },
      {
        "day_bucket": "weekend"
      },
      {
        "day_bucket": "weekday",
        "time_bucket": "morning"
      }
    ],
    "venues": [
      "Embassy Grand",
      "Light House Cuba",
      "Roxy Cinema",
      "Light House Petone",
      "Light House Pauatahanui"
    ],
    "watchlist": [
      "November",
      "Annie's Fire",
      "Masquerade",
      "The Innocent",
      "Other People's Children",
      "The Origin of Evil",
      "Maria Into Life"
    ],
    "watchlist_only": false,
    "max_daily_screenings": 1,
    "time_zone": "Pacific/Auckland"
  }

  const res = await fetch(`https://schedul-production.up.railway.app/festivals/${festival_id}/schedule`, {
    method: 'POST',
    body: JSON.stringify(payload),
    headers: {"Content-Type": "application/json"}
  });
  if (!res.ok) {
    throw new Error('Failed to fetch data');
  }
  return res.json();
}



export default async function IndexPage() {
  const [schedule, setSchedule] = useState([])

  const festivals = await getFestivals();

  async function handleFestivalSelect(selection: string) {
    getSchedule(selection).then(data => setSchedule(data))
  }


  return (
    <section className="container grid items-center gap-6 pb-8 pt-6 md:py-10">
      <div className="flex gap-4">
        <Select onValueChange={handleFestivalSelect}>
          <SelectTrigger>
            <SelectValue placeholder="Select festival" />
          </SelectTrigger>
          <SelectContent>
            {festivals.map((x: { id: string; full_name: string }) => (
              <SelectItem value={x.id} key={x.id}>{x.full_name}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div>
        {schedule.map((x: {screening}) => (
          <b key={x.screening.id}>{x.screening.film.name}</b>
        ))}

      </div>
      <div>{schedule}</div>

    </section>
  )
}
