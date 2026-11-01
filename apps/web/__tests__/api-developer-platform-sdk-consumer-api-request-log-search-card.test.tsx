import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-request-log-search-card";

describe("RequestLogSearchCard", () => {
  it("shows results", () => {
    const entries = [{ id: "l1", method: "GET", path: "/api/users", status: 200, latencyMs: 50, timestamp: "12:00" }];
    const { container } = render(<Card entries={entries} totalMatches={1} query="users" consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Log Search");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain('"users"');
    expect(container.textContent).toContain("1 results");
  });
  it("shows no results", () => {
    const { container } = render(<Card entries={[]} totalMatches={0} query="missing" consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No results found");
  });
});
