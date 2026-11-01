import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import FeatureRequestCard from "../src/components/feature-request-card";

const requests = [
  {
    request_id: "r1",
    title: "Dark Mode",
    status: "planned" as const,
    vote_count: 25,
    tags: ["ui"],
  },
  { request_id: "r2", title: "API v2", status: "open" as const, vote_count: 15, tags: ["api"] },
  { request_id: "r3", title: "Old Feature", status: "done" as const, vote_count: 5, tags: [] },
];

describe("FeatureRequestCard", () => {
  it("renders header and counts", () => {
    const { container } = render(<FeatureRequestCard requests={requests} appName="App" />);
    expect(container.textContent).toContain("Feature Requests");
    expect(container.textContent).toContain("1 open / 3 total");
  });

  it("shows titles and vote counts", () => {
    const { container } = render(<FeatureRequestCard requests={requests} appName="App" />);
    expect(container.textContent).toContain("Dark Mode");
    expect(container.textContent).toContain("25");
  });

  it("shows status badges", () => {
    const { container } = render(<FeatureRequestCard requests={requests} appName="App" />);
    expect(container.textContent).toContain("planned");
    expect(container.textContent).toContain("open");
    expect(container.textContent).toContain("done");
  });

  it("shows empty state", () => {
    const { container } = render(<FeatureRequestCard requests={[]} appName="App" />);
    expect(container.textContent).toContain("No feature requests");
  });
});
