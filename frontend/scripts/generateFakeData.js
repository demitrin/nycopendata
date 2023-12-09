"use strict";
// usage npx ts-node --esm generateFakeData.ts
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const lorem_ipsum_1 = require("lorem-ipsum");
const fs_1 = __importDefault(require("fs"));
const lorem = new lorem_ipsum_1.LoremIpsum({
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
        datasetSite: "https://data.cityofnewyork.us/City-Government/DOC-Hart-Island-Burial-Records/f5mc-f3zp",
        agency: "Department of Correction (BOC)",
        site: "https://www.nyc.gov/site/boc/index.page",
    },
    {
        datasetTitle: "NYC Leading Causes of Death",
        datasetSite: "https://data.cityofnewyork.us/Health/New-York-City-Leading-Causes-of-Death/jb7j-dtam",
        agency: "Department of Health and Mental Hygiene (DOHMH)",
        site: "https://www.nyc.gov/site/doh/index.page",
    },
    {
        datasetTitle: "NYPD Personnel Demographics",
        datasetSite: "https://data.cityofnewyork.us/Public-Safety/NYPD-Personnel-Demographics/5vr7-5fki",
        agency: "Police Department (NYPD)",
        site: "https://www.nyc.gov/site/nypd/index.page",
    },
    {
        datasetTitle: "Citywide Payroll Data (Fiscal Year)",
        datasetSite: "https://data.cityofnewyork.us/City-Government/Citywide-Payroll-Data-Fiscal-Year-/k397-673e",
        agency: "Office of Payroll Administration (OPA)",
        site: "https://www.nyc.gov/site/opa/index.page",
    },
    {
        datasetTitle: "Participator Budgeting Projects",
        datasetSite: "https://data.cityofnewyork.us/City-Government/Participatory-Budgeting-Projects/wwhr-5ven",
        agency: "City Council (NYCC)",
        site: "https://council.nyc.gov/pb/",
    },
];
const generateClockNumbers = () => {
    const clockRecords = [];
    for (let hour = 1; hour < 13; hour++) {
        for (let minute = 0; minute < 60; minute++) {
            let clockTime;
            const paddedMinute = minute < 10 ? `0${minute}` : minute.toString();
            if (Math.random() < 0.4) {
                clockTime = Number(`${hour}.${paddedMinute}`);
            }
            else {
                clockTime = Number(`${hour}${paddedMinute}`);
            }
            const randomDataset = datasets[Math.floor(Math.random() * datasets.length)];
            clockRecords.push({
                clockTime,
                prompt: `${lorem.generateSentences(1)}`,
                department: randomDataset.agency,
                datasource: randomDataset.datasetTitle,
            });
        }
    }
    return clockRecords;
};
console.log("generating fake data:", generateClockNumbers().length, "records");
fs_1.default.writeFileSync("./fakeData.json", `${JSON.stringify(generateClockNumbers(), null, 2)}`);
