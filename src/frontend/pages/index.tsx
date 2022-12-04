import Head from "next/head";
import React from "react";
import styles from "../styles/Home.module.css";
import { GetFestivals } from "./festivals";
import { GetFilms } from "./films";
import { GetSchedule } from "./schedule";

export default function Home({}) {
  return (
    <div className={styles.container}>
      <Head>
        <title>Scedul</title>
        <meta name="description" content="Scedul" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main>
        <GetFestivals/>
      </main>
    </div>
  );
}