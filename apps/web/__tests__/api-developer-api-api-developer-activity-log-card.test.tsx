import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperActivityLogCard from "../src/components/api-developer-api-api-developer-activity-log-card";

const activities = [
  { activity_id: "a1", developer_id: "alice", action: "key_created", resource: "key-1" },
  { activity_id: "a2", developer_id: "bob", action: "login", resource: "session-1" },
];

describe("APIDeveloperAPIApiDeveloperActivityLogCard", () => {
  it("shows activities", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperActivityLogCard activities={activities} totalCount={500} appName="App" />);
    expect(container.textContent).toContain("Activity Log");
    expect(container.textContent).toContain("500 events");
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("key created");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperActivityLogCard activities={[]} totalCount={0} appName="App" />);
    expect(container.textContent).toContain("No activity");
  });
});
