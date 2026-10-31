import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperActivityCard from "../src/components/api-developer-activity-card";

const devs = [
  { developer_id: "alice", api_calls: 500, active_days: 20, endpoints_used: 10, engagement_score: 85.5 },
  { developer_id: "bob", api_calls: 50, active_days: 3, endpoints_used: 2, engagement_score: 25.0 },
];

describe("APIDeveloperActivityCard", () => {
  it("renders header and active count", () => {
    const { container } = render(<APIDeveloperActivityCard developers={devs} totalActive={10} appName="App" />);
    expect(container.textContent).toContain("Developer Activity");
    expect(container.textContent).toContain("10 active devs");
  });

  it("shows developer stats", () => {
    const { container } = render(<APIDeveloperActivityCard developers={devs} totalActive={2} appName="App" />);
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("500 calls");
    expect(container.textContent).toContain("score 85.5");
  });

  it("shows empty state", () => {
    const { container } = render(<APIDeveloperActivityCard developers={[]} totalActive={0} appName="App" />);
    expect(container.textContent).toContain("No developer activity");
  });
});
