import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIRequestLogCard from "../src/components/api-request-log-card";

const pathStats = [
  { path: "/api/users", count: 500, avg_ms: 75.0 },
  { path: "/api/apps", count: 200, avg_ms: 30.0 },
];

describe("APIRequestLogCard", () => {
  it("renders header and counts", () => {
    const { container } = render(<APIRequestLogCard pathStats={pathStats} totalCount={1000} errorCount={50} appName="App" />);
    expect(container.textContent).toContain("Request Log");
    expect(container.textContent).toContain("1,000 requests");
    expect(container.textContent).toContain("50 errors");
  });

  it("shows paths and stats", () => {
    const { container } = render(<APIRequestLogCard pathStats={pathStats} totalCount={700} errorCount={0} appName="App" />);
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("75ms");
  });

  it("shows empty state", () => {
    const { container } = render(<APIRequestLogCard pathStats={[]} totalCount={0} errorCount={0} appName="App" />);
    expect(container.textContent).toContain("No requests logged");
  });
});
