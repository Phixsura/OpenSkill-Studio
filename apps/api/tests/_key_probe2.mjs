import { chromium } from "playwright";
const CHROMIUM_PATH = process.env.CHROMIUM_PATH ??
  `${process.env.HOME}/Library/Caches/ms-playwright/chromium-1223/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing`;
const BASE = "http://localhost:3000";
const browser = await chromium.launch({ headless: true, executablePath: CHROMIUM_PATH });
const page = await browser.newPage();
page.on("console", async (msg) => {
  if (msg.type() !== "error") return;
  const parts = [];
  for (const a of msg.args()) {
    try { parts.push(String(await a.jsonValue())); } catch { parts.push("?"); }
  }
  console.log("ERR @", page.url(), "::", msg.text().slice(0,200), "||", parts.join(" | ").slice(0, 200));
});
// register+login like commercial suite
const email = `kp2-${Date.now()}@test.com`;
await page.request.post("http://localhost:8000/api/v1/auth/register", {
  data: { email, password: "TestPass123!", display_name: "KP" },
});
await page.goto(`${BASE}/login`, { waitUntil: "load" });
await page.fill('input[type="email"]', email);
await page.fill('input[type="password"]', "TestPass123!");
await page.click('button[type="submit"]');
await page.waitForTimeout(3000);
await page.goto(`${BASE}/dashboard`, { waitUntil: "load" });
await page.waitForTimeout(3000);
await page.goto(`${BASE}/dashboard/orgs/new`, { waitUntil: "load" });
await page.waitForTimeout(3000);
await browser.close();
