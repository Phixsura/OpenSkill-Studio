import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ErrorClassifierCard from "../src/components/error-classifier-card";

const groups = [
  {
    fingerprint: "abc123",
    category: "network",
    sample_message: "Connection timed out",
    count: 42,
    first_seen: new Date(Date.now() - 86400000).toISOString(),
    last_seen: new Date(Date.now() - 60000).toISOString(),
  },
  {
    fingerprint: "def456",
    category: "auth",
    sample_message: "Invalid token",
    count: 15,
    first_seen: new Date(Date.now() - 3600000).toISOString(),
    last_seen: new Date(Date.now() - 300000).toISOString(),
  },
];
const categoryCounts = { network: 42, auth: 15 };

describe("ErrorClassifierCard", () => {
  it("renders header and app name", () => {
    const { container } = render(
      <ErrorClassifierCard
        groups={groups}
        categoryCounts={categoryCounts}
        totalErrors={57}
        appName="My App"
      />,
    );
    expect(container.textContent).toContain("Error Groups");
    expect(container.textContent).toContain("My App");
  });

  it("shows total and group counts", () => {
    const { container } = render(
      <ErrorClassifierCard
        groups={groups}
        categoryCounts={categoryCounts}
        totalErrors={57}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("57 total errors");
    expect(container.textContent).toContain("2 groups");
  });

  it("renders category badges", () => {
    const { container } = render(
      <ErrorClassifierCard
        groups={groups}
        categoryCounts={categoryCounts}
        totalErrors={57}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("network 42");
    expect(container.textContent).toContain("auth 15");
  });

  it("shows error messages and counts", () => {
    const { container } = render(
      <ErrorClassifierCard
        groups={groups}
        categoryCounts={categoryCounts}
        totalErrors={57}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("Connection timed out");
    expect(container.textContent).toContain("×42");
  });

  it("shows no-errors message when empty", () => {
    const { container } = render(
      <ErrorClassifierCard groups={[]} categoryCounts={{}} totalErrors={0} appName="App" />,
    );
    expect(container.textContent).toContain("No errors");
  });
});
