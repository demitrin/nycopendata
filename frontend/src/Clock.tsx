import { useState, useEffect } from "react";
import "./Clock.css"; // You may need to create this CSS file for styling

import data from './data'

type ClockRecord = {
  clockTime: number;
  prompt: string;
  department: string;
  datasource: string;
};

const dataByClockTime: Record<number, ClockRecord> = {}
for (const item of data) {
  dataByClockTime[item.clockTime] = item
}

function getClockRecordFromCurrentTime() {
  const currentDate = new Date();
  const hours = currentDate.getHours() % 12 || 12; // Convert to 12-hour format
  const minutes = currentDate.getMinutes();

  const clockTimeOption1 = hours * 100 + minutes
  const clockTimeOption2 = hours + minutes / 100
  return dataByClockTime[clockTimeOption1] || dataByClockTime[clockTimeOption2]

}

function getFormattedTime() {
  const currentDate = new Date();
  const hours = currentDate.getHours() % 12 || 12; // Convert to 12-hour format
  const minutes = currentDate.getMinutes();
  const ampm = currentDate.getHours() >= 12 ? "PM" : "AM";

  return `${hours}:${minutes < 10 ? "0" : ""}${minutes} ${ampm}`;
}

const Clock = () => {
  const [time, setTime] = useState(getFormattedTime);
  const [clockRecord, setClockRecord] = useState(getClockRecordFromCurrentTime);

  useEffect(() => {
    const intervalId = setInterval(() => {
      setTime(getFormattedTime());
      setClockRecord(getClockRecordFromCurrentTime());

    }, 1000); // Update every minute

    return () => clearInterval(intervalId); // Cleanup on component unmount
  }, []);

  return <div className="clock">
      <div className="container">
        <div className="clockTime">{clockRecord.clockTime}</div>
        <div className="prompt">{clockRecord.prompt}</div>
        <div className="datasource">
          <div>{clockRecord.datasource}</div>
          <div>{clockRecord.department}</div>
        </div>
      </div>
      
    </div>
};

export default Clock;
