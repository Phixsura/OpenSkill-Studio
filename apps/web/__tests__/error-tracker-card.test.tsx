import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ErrorTrackerCard from "../src/components/error-tracker-card";

const errors = [
  { fingerprint: "fp1", message: "NullPointerException", source: "api-server", count: 42, resolved: false },
  { fingerprint: "fp2", message: "TimeoutError", source: "worker", count: 5, resolved: true },
];

describe("ErrorTrackerCard", () => {
  it("renders header and unresolved count", () => {
    const { container } = render(<ErrorTrackerCard errors={errors} unresolvedCount={1} appName="App" />);
    expect(container.textContent).toContain("Error Tracker");
    expect(container.textContent).toContain("1 unresolved");
  });

  it("shows error messages and counts", () => {
    const { container } = render(<ErrorTrackerCard errors={errors} unresolvedCount={1} appName="App" />);
    expect(container.textContent).toContain("NullPointerException");
    expect(container.textContent).toContain("42x");
  });

  it("shows sources", () => {
    const { container } = render(<ErrorTrackerCard errors={errors} unresolvedCount={0} appName="App" />);
    expect(container.textContent).toContain("api-server");
  });

  it("shows clean state", () => {
    const { container } = render(<ErrorTrackerCard errors={[]} unresolvedCount={0} appName="App" />);
    expect(container.textContent).toContain("No errors tracked");
  });
});
