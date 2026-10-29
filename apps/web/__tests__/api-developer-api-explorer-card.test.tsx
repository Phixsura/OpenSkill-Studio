import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIExplorerCard from "../src/components/api-developer-api-explorer-card";

const eps = [
  { method: "GET", path: "/api/users", summary: "List users", category: "users" },
  { method: "POST", path: "/api/apps", summary: "Create app", category: "apps" },
];

describe("APIDeveloperAPIExplorerCard", () => {
  it("shows endpoints", () => {
    const { container } = render(<APIDeveloperAPIExplorerCard endpoints={eps} categories={["users", "apps"]} appName="App" />);
    expect(container.textContent).toContain("API Explorer");
    expect(container.textContent).toContain("2 endpoints");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/users");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIExplorerCard endpoints={[]} categories={[]} appName="App" />);
    expect(container.textContent).toContain("No endpoints to explore");
  });
});
