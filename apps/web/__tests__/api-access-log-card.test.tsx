import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIAccessLogCard from "../src/components/api-access-log-card";

const entries = [
  { log_id: "l1", actor: "alice", method: "GET", path: "/api/users", status_code: 200, ip_address: "10.0.0.1" },
  { log_id: "l2", actor: "bob", method: "POST", path: "/api/apps", status_code: 403, ip_address: "10.0.0.2" },
];

describe("APIAccessLogCard", () => {
  it("renders header and counts", () => {
    const { container } = render(<APIAccessLogCard entries={entries} uniqueActors={2} totalCount={100} appName="App" />);
    expect(container.textContent).toContain("Access Log");
    expect(container.textContent).toContain("100 entries");
    expect(container.textContent).toContain("2 actors");
  });

  it("shows actors, methods, paths", () => {
    const { container } = render(<APIAccessLogCard entries={entries} uniqueActors={2} totalCount={2} appName="App" />);
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("403");
  });

  it("shows empty state", () => {
    const { container } = render(<APIAccessLogCard entries={[]} uniqueActors={0} totalCount={0} appName="App" />);
    expect(container.textContent).toContain("No access logs");
  });
});
