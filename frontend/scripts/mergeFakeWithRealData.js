"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
const fs = __importStar(require("fs"));
const lorem_ipsum_1 = require("lorem-ipsum");
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
function mergeData(realData) {
    const mergedData = [];
    for (let hour = 1; hour < 13; hour++) {
        for (let minute = 0; minute < 60; minute++) {
            const paddedMinute = minute < 10 ? `0${minute}` : minute.toString();
            const targetClockTime = Number(`${hour}${paddedMinute}`);
            const targetClockTimeInRealData = realData.find((record) => record.clockTime === targetClockTime ||
                record.clockTime * 100 === targetClockTime);
            if (targetClockTimeInRealData) {
                mergedData.push(targetClockTimeInRealData);
            }
            else {
                let clockTime;
                if (Math.random() < 0.4) {
                    clockTime = Number(`${hour}.${paddedMinute}`);
                }
                else {
                    clockTime = Number(`${hour}${paddedMinute}`);
                }
                const randomDataset = datasets[Math.floor(Math.random() * datasets.length)];
                console.log("Not found -- generating fake data", targetClockTime, randomDataset.agency, randomDataset.datasetTitle);
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
        const realData = JSON.parse(fs.readFileSync("realData.json", "utf-8"));
        const mergedData = mergeData(realData);
        fs.writeFileSync("../src/data.ts", `export default ${JSON.stringify(mergedData, null, 2)}`);
        console.log("Merge successful. Merged data saved to mergedData.json");
    }
    catch (error) {
        console.error("Error:", error);
    }
}
main();
