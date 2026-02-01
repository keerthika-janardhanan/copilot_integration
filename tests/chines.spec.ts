import { test } from "../testSetup";
import OnecognizantPage from "../pages/OnecognizantPage.ts";
import ResourcedashboardPage from "../pages/ResourcedashboardPage.ts";
import { getTestToRun, shouldRun, readExcelData } from "../util/csvFileManipulation.ts";
import { attachScreenshot, namedStep } from "../util/screenshot.ts";
import * as dotenv from 'dotenv';

const path = require('path');
const fs = require('fs');

dotenv.config();
let executionList: any[];

test.beforeAll(() => {
  executionList = getTestToRun(path.join(__dirname, '../testmanager.xlsx'));
});

test.describe("chines", () => {
  let onecognizantPage: OnecognizantPage;
  let resourcedashboardPage: ResourcedashboardPage;

  const run = (name: string, fn: ({ page }, testinfo: any) => Promise<void>) =>
    (shouldRun(name) ? test : test.skip)(name, fn);

  run("chines", async ({ page }, testinfo) => {
    onecognizantPage = new OnecognizantPage(page);
    resourcedashboardPage = new ResourcedashboardPage(page);

    const testCaseId = testinfo.title;
    const testRow: Record<string, any> = executionList?.find((row: any) => row['TestCaseID'] === testCaseId) ?? {};
    const defaultDataStem = (() => {
      const core = testCaseId.replace(/[^a-z0-9]+/gi, ' ').trim();
      if (!core) {
        return 'TestData';
      }
      return core.split(/\s+/).map((part) => part.charAt(0).toUpperCase() + part.slice(1)).join('');
    })();
    const defaultDatasheetName = `${defaultDataStem}Data.xlsx`;
    const defaultIdColumn = `${defaultDataStem}ID`;
    const defaultReferenceId = `${defaultDataStem}001`;
    const dataSheetName = String(testRow?.['DatasheetName'] ?? '').trim() || defaultDatasheetName;
    const envReferenceId = (process.env.REFERENCE_ID || process.env.DATA_REFERENCE_ID || '').trim();
    const excelReferenceId = String(testRow?.['ReferenceID'] ?? '').trim() || defaultReferenceId;
    const dataReferenceId = envReferenceId || excelReferenceId;
    const dataIdColumn = String(testRow?.['IDName'] ?? '').trim() || defaultIdColumn;
    const dataSheetTab = String(testRow?.['SheetName'] ?? testRow?.['Sheet'] ?? '').trim();
    const dataDir = path.join(__dirname, '../data');
    fs.mkdirSync(dataDir, { recursive: true });
    let dataRow: Record<string, any> = {};

    const ensureDataFile = (): string | null => {
      if (!dataSheetName) {
        return null;
      }
      const expectedPath = path.join(dataDir, dataSheetName);
      if (!fs.existsSync(expectedPath)) {
        const caseInsensitiveMatch = (() => {
          try {
            const entries = fs.readdirSync(dataDir, { withFileTypes: false });
            const target = dataSheetName.toLowerCase();
            const found = entries.find((entry) => entry.toLowerCase() === target);
            return found ? path.join(dataDir, found) : null;
          } catch (err) {
            return null;
          }
        })();
        if (caseInsensitiveMatch) {
          return caseInsensitiveMatch;
        }
        throw new Error(`Test data file '${dataSheetName}' not found in data/.`);
      }
      return expectedPath;
    };

    const dataPath = ensureDataFile();
    if (dataPath && dataReferenceId && dataIdColumn) {
      dataRow = readExcelData(dataPath, dataSheetTab || '', dataReferenceId, dataIdColumn) ?? {};
    }

    await namedStep("Step 1 - Navigate to OneCognizant", page, testinfo, async () => {
      await page.goto("https://onecognizant.cognizant.com/welcome");
      const screenshot = await page.screenshot();
      attachScreenshot("Step 1 - Navigate to OneCognizant", testinfo, screenshot);
    });

    await namedStep("Step 2 - Fill Field1", page, testinfo, async () => {
      await onecognizantPage.applyData(dataRow, ["Field1"], 0);
      const screenshot = await page.screenshot();
      attachScreenshot("Step 2 - Fill Field1", testinfo, screenshot);
    });

    await namedStep("Step 3 - Click Button1", page, testinfo, async () => {
      await onecognizantPage.button1.click();
      const screenshot = await page.screenshot();
      attachScreenshot("Step 3 - Click Button1", testinfo, screenshot);
    });

    await namedStep("Step 4 - Fill Field2", page, testinfo, async () => {
      await onecognizantPage.applyData(dataRow, ["Field2"], 0);
      const screenshot = await page.screenshot();
      attachScreenshot("Step 4 - Fill Field2", testinfo, screenshot);
    });

    await namedStep("Step 5 - Click Button1", page, testinfo, async () => {
      await onecognizantPage.button1.click();
      const screenshot = await page.screenshot();
      attachScreenshot("Step 5 - Click Button1", testinfo, screenshot);
    });

    await namedStep("Step 6 - Fill Field3", page, testinfo, async () => {
      await onecognizantPage.applyData(dataRow, ["Field3"], 0);
      const screenshot = await page.screenshot();
      attachScreenshot("Step 6 - Fill Field3", testinfo, screenshot);
    });

    await namedStep("Step 7 - Click Button1", page, testinfo, async () => {
      await onecognizantPage.button1.click();
      const screenshot = await page.screenshot();
      attachScreenshot("Step 7 - Click Button1", testinfo, screenshot);
    });

    await namedStep("Step 8 - Fill Field4", page, testinfo, async () => {
      await onecognizantPage.applyData(dataRow, ["Field4"], 0);
      const screenshot = await page.screenshot();
      attachScreenshot("Step 8 - Fill Field4", testinfo, screenshot);
    });

    await namedStep("Step 9 - Click Button1", page, testinfo, async () => {
      await onecognizantPage.button1.click();
      const screenshot = await page.screenshot();
      attachScreenshot("Step 9 - Click Button1", testinfo, screenshot);
    });

    await namedStep("Step 10 - Fill Field5", page, testinfo, async () => {
      await onecognizantPage.applyData(dataRow, ["Field5"], 0);
      const screenshot = await page.screenshot();
      attachScreenshot("Step 10 - Fill Field5", testinfo, screenshot);
    });

    await namedStep("Step 11 - Click Button1", page, testinfo, async () => {
      await onecognizantPage.button1.click();
      const screenshot = await page.screenshot();
      attachScreenshot("Step 11 - Click Button1", testinfo, screenshot);
    });

    await namedStep("Step 12 - Click Button2", page, testinfo, async () => {
      await onecognizantPage.button2.click();
      const screenshot = await page.screenshot();
      attachScreenshot("Step 12 - Click Button2", testinfo, screenshot);
    });

    await namedStep("Step 13 - Resource Dashboard Action 1", page, testinfo, async () => {
      await resourcedashboardPage.button1.click();
      const screenshot = await page.screenshot();
      attachScreenshot("Step 13 - Resource Dashboard Action 1", testinfo, screenshot);
    });

    await namedStep("Step 14 - Resource Dashboard Action 2", page, testinfo, async () => {
      await resourcedashboardPage.button2.click();
      const screenshot = await page.screenshot();
      attachScreenshot("Step 14 - Resource Dashboard Action 2", testinfo, screenshot);
    });

  });
});
