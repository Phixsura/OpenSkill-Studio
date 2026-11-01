import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIScopeCard from "../src/components/api-scope-card";

const scopes = [
  {
    scope_id: "read:users",
    name: "Read Users",
    description: "Access user data",
    category: "users",
  },
  {
    scope_id: "write:users",
    name: "Write Users",
    description: "Modify user data",
    category: "users",
  },
  { scope_id: "read:apps", name: "Read Apps", description: "Access app data", category: "apps" },
];

describe("APIScopeCard", () => {
  it("renders header and counts", () => {
    const { container } = render(<APIScopeCard scopes={scopes} appName="App" />);
    expect(container.textContent).toContain("API Scopes");
    expect(container.textContent).toContain("3 scopes");
    expect(container.textContent).toContain("2 categories");
  });

  it("shows scope IDs", () => {
    const { container } = render(<APIScopeCard scopes={scopes} appName="App" />);
    expect(container.textContent).toContain("read:users");
    expect(container.textContent).toContain("write:users");
    expect(container.textContent).toContain("read:apps");
  });

  it("shows category badges", () => {
    const { container } = render(<APIScopeCard scopes={scopes} appName="App" />);
    expect(container.textContent).toContain("users");
    expect(container.textContent).toContain("apps");
  });

  it("shows empty state", () => {
    const { container } = render(<APIScopeCard scopes={[]} appName="App" />);
    expect(container.textContent).toContain("No scopes defined");
  });
});
