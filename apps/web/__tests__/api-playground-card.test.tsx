import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIPlaygroundCard from "../src/components/api-playground-card";

const templates = [
  { request_id: "r1", method: "GET", path: "/api/v1/users", name: "List Users" },
  { request_id: "r2", method: "POST", path: "/api/v1/apps", name: "" },
];
const results = [
  { request_id: "r1", status_code: 200, duration_ms: 45 },
  { request_id: "r2", status_code: 500, duration_ms: 120 },
];

describe("APIPlaygroundCard", () => {
  it("renders header and template count", () => {
    const { container } = render(
      <APIPlaygroundCard templates={templates} recentResults={results} appName="App" />,
    );
    expect(container.textContent).toContain("API Playground");
    expect(container.textContent).toContain("2 templates");
  });

  it("shows methods and paths", () => {
    const { container } = render(
      <APIPlaygroundCard templates={templates} recentResults={[]} appName="App" />,
    );
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/v1/users");
    expect(container.textContent).toContain("List Users");
  });

  it("shows recent results", () => {
    const { container } = render(
      <APIPlaygroundCard templates={[]} recentResults={results} appName="App" />,
    );
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("45ms");
  });

  it("shows empty state", () => {
    const { container } = render(
      <APIPlaygroundCard templates={[]} recentResults={[]} appName="App" />,
    );
    expect(container.textContent).toContain("No playground activity");
  });
});
