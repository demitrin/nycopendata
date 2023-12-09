import * as fs from "fs";
import { LoremIpsum } from "lorem-ipsum";

type ClockRecord = {
  clockTime: number;
  prompt: string;
  department: string;
  datasource: string;
};

const lorem = new LoremIpsum({
  sentencesPerParagraph: {
    max: 8,
    min: 4,
  },
  wordsPerSentence: {
    max: 16,
    min: 10,
  },
});

const datasets = [
  {
    datasetTitle: "Hart Island Burial Records",
    datasetSite:
      "https://data.cityofnewyork.us/City-Government/DOC-Hart-Island-Burial-Records/f5mc-f3zp",
    agency: "Department of Correction (BOC)",
    site: "https://www.nyc.gov/site/boc/index.page",
  },
  {
    datasetTitle: "NYC Leading Causes of Death",
    datasetSite:
      "https://data.cityofnewyork.us/Health/New-York-City-Leading-Causes-of-Death/jb7j-dtam",
    agency: "Department of Health and Mental Hygiene (DOHMH)",
    site: "https://www.nyc.gov/site/doh/index.page",
  },
  {
    datasetTitle: "NYPD Personnel Demographics",
    datasetSite:
      "https://data.cityofnewyork.us/Public-Safety/NYPD-Personnel-Demographics/5vr7-5fki",
    agency: "Police Department (NYPD)",
    site: "https://www.nyc.gov/site/nypd/index.page",
  },
  {
    datasetTitle: "Citywide Payroll Data (Fiscal Year)",
    datasetSite:
      "https://data.cityofnewyork.us/City-Government/Citywide-Payroll-Data-Fiscal-Year-/k397-673e",
    agency: "Office of Payroll Administration (OPA)",
    site: "https://www.nyc.gov/site/opa/index.page",
  },
  {
    datasetTitle: "Participator Budgeting Projects",
    datasetSite:
      "https://data.cityofnewyork.us/City-Government/Participatory-Budgeting-Projects/wwhr-5ven",
    agency: "City Council (NYCC)",
    site: "https://council.nyc.gov/pb/",
  },
];

function mergeData(realData: ClockRecord[]): ClockRecord[] {
  const mergedData: ClockRecord[] = [];
  for (let hour = 1; hour < 13; hour++) {
    for (let minute = 0; minute < 60; minute++) {
      const paddedMinute = minute < 10 ? `0${minute}` : minute.toString();
      const targetClockTime = Number(`${hour}${paddedMinute}`);
      const targetClockTimeInRealData = realData.find(
        (record) =>
          record.clockTime === targetClockTime ||
          record.clockTime * 100 === targetClockTime
      );
      if (targetClockTimeInRealData) {
        mergedData.push(targetClockTimeInRealData);
      } else {
        let clockTime;
        if (Math.random() < 0.4) {
          clockTime = Number(`${hour}.${paddedMinute}`);
        } else {
          clockTime = Number(`${hour}${paddedMinute}`);
        }
        const randomDataset =
          datasets[Math.floor(Math.random() * datasets.length)];
        console.log(
          "Not found -- generating fake data",
          targetClockTime,
          randomDataset.agency,
          randomDataset.datasetTitle
        );
        mergedData.push({
          clockTime,
          prompt: `${lorem.generateSentences(1)}`,
          department: randomDataset.agency,
          datasource: randomDataset.datasetTitle,
        });
      }
    }
  }
  return mergedData;
}

function main() {
  try {
    // Read real data from realData.json
    const realData: ClockRecord[] = JSON.parse(
      fs.readFileSync("realData.json", "utf-8")
    );
    const mergedData = mergeData(realData);

    fs.writeFileSync(
      "../src/data.ts",
      `export default ${JSON.stringify(mergedData, null, 2)}`
    );

    console.log("Merge successful. Merged data saved to mergedData.json");
  } catch (error) {
    console.error("Error:", error);
  }
}

main();
