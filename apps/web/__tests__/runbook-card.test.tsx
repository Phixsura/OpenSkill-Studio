import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import RunbookCard from "../src/components/runbook-card";

const runbooks = [
  {
    runbook_id: "rb1",
    title: "CPU Alert Response",
    description: "Handle CPU",
    steps: [{ instruction: "Check", expected_outcome: "OK" }],
    tags: ["infra"],
    execution_count: 5,
  },
  {
    runbook_id: "rb2",
    title: "Disk Full",
    description: "Handle disk",
    steps: [
      { instruction: "A", expected_outcome: "" },
      { instruction: "B", expected_outcome: "" },
    ],
    tags: [],
    execution_count: 0,
  },
];

describe("RunbookCard", () => {
  it("renders header", () => {
    const { container } = render(<RunbookCard runbooks={runbooks} appName="My App" />);
    expect(container.textContent).toContain("Runbooks");
  });

  it("shows count", () => {
    const { container } = render(<RunbookCard runbooks={runbooks} appName="App" />);
    expect(container.textContent).toContain("2 runbooks");
  });

  it("renders titles and step counts", () => {
    const { container } = render(<RunbookCard runbooks={runbooks} appName="App" />);
    expect(container.textContent).toContain("CPU Alert Response");
    expect(container.textContent).toContain("1 steps");
    expect(container.textContent).toContain("5 runs");
  });

  it("shows tags", () => {
    const { container } = render(<RunbookCard runbooks={runbooks} appName="App" />);
    expect(container.textContent).toContain("infra");
  });

  it("shows empty state", () => {
    const { container } = render(<RunbookCard runbooks={[]} appName="App" />);
    expect(container.textContent).toContain("No runbooks");
  });
});
