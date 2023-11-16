import { useEffect, useState } from "react";
import "./Clock.css"; // You may need to create this CSS file for styling

import data from "./data";

type ClockRecord = {
  clockTime: number;
  prompt: string;
  department: string;
  datasource: string;
};

const dataByClockTime: Record<number, ClockRecord> = {};
for (const item of data) {
  dataByClockTime[item.clockTime] = item;
}

function getClockRecordFromCurrentTime() {
  const currentDate = new Date();
  const hours = currentDate.getHours() % 12 || 12; // Convert to 12-hour format
  const minutes = currentDate.getMinutes();
  const clockTimeOption1 = hours * 100 + minutes;
  const clockTimeOption2 = hours + minutes / 100;
  return dataByClockTime[clockTimeOption1] || dataByClockTime[clockTimeOption2];
}

const hasDecimal = (clockTime: number) => {
  return clockTime % 1 !== 0;
};

const getDigit = (clockTime: number, digit: "1" | "2" | "3" | "4") => {
  if (hasDecimal(clockTime)) {
    switch (digit) {
      case "1":
        return Math.floor(clockTime / 10);
      case "2":
        return Math.floor(clockTime % 10);
      case "3":
        return Math.floor(clockTime * 10) % 10;
      case "4":
        return Math.floor(clockTime * 100) % 10;
      default:
        return 0;
    }
  } else {
    switch (digit) {
      case "1":
        return Math.floor(clockTime / 1000);
      case "2":
        return Math.floor(clockTime / 100) % 10;
      case "3":
        return Math.floor(clockTime / 10) % 10;
      case "4":
        return clockTime % 10;
      default:
        return 0;
    }
  }
};

const Clock = () => {
  const [clockRecord, setClockRecord] = useState(getClockRecordFromCurrentTime);

  useEffect(() => {
    const intervalId = setInterval(() => {
      setClockRecord(getClockRecordFromCurrentTime());
      // testing only
      // setClockRecord({
      //   clockTime: 22,
      //   prompt:
      //     "Commodo id culpa anim ad non culpa sunt aute consectetur ad enim labore fugiat.",
      //   department: "Department of Health and Mental Hygiene (DOHMH)",
      //   datasource: "NYC Leading Causes of Death",
      // });
    }, 1000);

    return () => clearInterval(intervalId);
  }, []);

  const firstDigit = getDigit(clockRecord.clockTime, "1");
  const secondDigit = getDigit(clockRecord.clockTime, "2");

  return (
    <div className="clock">
      <div className="container">
        <div className="clockTime">
          <div className={`digit ${firstDigit === 0 ? "faded-text" : ""}`}>
            {firstDigit}
          </div>
          <div
            className={`digit ${
              firstDigit === 0 && secondDigit === 0 ? "faded-text" : ""
            }`}
          >
            {secondDigit}
          </div>
          <div className="breaker">
            <div className={`topColon`}>
              <div className={`period faded-div`}></div>
            </div>
            <div className={`bottomColon`}>
              <div
                className={`period ${
                  hasDecimal(clockRecord.clockTime) ? "" : "faded-div"
                }`}
              ></div>
            </div>
          </div>
          <div className="digit">{getDigit(clockRecord.clockTime, "3")}</div>
          <div className="digit">{getDigit(clockRecord.clockTime, "4")}</div>
        </div>
        <div className="prompt">{clockRecord.prompt}</div>
        <div className="datasource">
          <div>{clockRecord.datasource}</div>
          <div>{clockRecord.department}</div>
        </div>
      </div>
    </div>
  );
};

export default Clock;
