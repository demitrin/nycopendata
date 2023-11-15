import { useState, useEffect } from "react";
import "./Clock.css"; // You may need to create this CSS file for styling

function getFormattedTime() {
  const currentDate = new Date();
  const hours = currentDate.getHours() % 12 || 12; // Convert to 12-hour format
  const minutes = currentDate.getMinutes();
  const ampm = currentDate.getHours() >= 12 ? "PM" : "AM";

  return `${hours}:${minutes < 10 ? "0" : ""}${minutes} ${ampm}`;
}

const Clock = () => {
  const [time, setTime] = useState(getFormattedTime);

  useEffect(() => {
    const intervalId = setInterval(() => {
      setTime(getFormattedTime());
    }, 60000); // Update every minute

    return () => clearInterval(intervalId); // Cleanup on component unmount
  }, []);

  return <div className="clock">{time}</div>;
};

export default Clock;
