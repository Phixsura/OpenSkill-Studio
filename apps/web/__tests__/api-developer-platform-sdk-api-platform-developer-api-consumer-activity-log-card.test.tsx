import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-consumer-activity-log-card";

describe("ActivityLogCard", () => {
  it("shows activity", () => {
    const entries = [{ entry_id: "e1", consumer_id: "c1", action: "api_call", resource: "/users", status_code: 200 }];
    const { container } = render(<Card entries={entries} totalEntries={1500} uniqueConsumers={12} appName="App" />);
    expect(container.textContent).toContain("Activity Log");
    expect(container.textContent).toContain("1,500 entries");
    expect(container.textContent).toContain("12 consumers");
    expect(container.textContent).toContain("/users");
    expect(container.textContent).toContain("200");
  });
  it("shows empty", () => {
    const { container } = render(<Card entries={[]} totalEntries={0} uniqueConsumers={0} appName="App" />);
    expect(container.textContent).toContain("No activity");
  });
});
