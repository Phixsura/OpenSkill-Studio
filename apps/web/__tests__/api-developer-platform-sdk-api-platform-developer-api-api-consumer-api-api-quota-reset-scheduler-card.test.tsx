import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-quota-reset-scheduler-card";

describe("QuotaResetSchedulerCard", () => {
  it("shows schedules", () => {
    const schedules = [{ consumer_id: "c1", interval: "daily", minutes_until_reset: 720, total_resets: 30 }];
    const { container } = render(<Card schedules={schedules} dueCount={0} appName="App" />);
    expect(container.textContent).toContain("Quota Resets");
    expect(container.textContent).toContain("daily");
    expect(container.textContent).toContain("720m");
  });
  it("shows due count", () => {
    const { container } = render(<Card schedules={[]} dueCount={3} appName="App" />);
    expect(container.textContent).toContain("3 due");
  });
});
