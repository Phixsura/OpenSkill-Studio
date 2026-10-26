import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ExtensionApiExplorer } from "@/components/extension-api-explorer";

const mockGroups = [
  { name: "Users", endpoints: [
    { path: "/users", method: "GET" as const, description: "List users",
      params: [{ name: "limit", type: "int", required: false }],
      responseExample: '{"users": []}' },
    { path: "/users", method: "POST" as const, description: "Create user",
      params: [{ name: "name", type: "string", required: true }],
      responseExample: '{"id": "u1"}' },
  ]},
  { name: "Config", endpoints: [
    { path: "/config", method: "GET" as const, description: "Get config",
      params: [], responseExample: '{"theme": "dark"}' },
  ]},
];

describe("ExtensionApiExplorer", () => {
  it("renders groups and endpoints", () => {
    const { container } = render(<ExtensionApiExplorer groups={mockGroups} extensionName="Slack Bot" />);
    expect(container.textContent).toContain("API Explorer");
    expect(container.textContent).toContain("Users (2)");
    expect(container.textContent).toContain("Config (1)");
    expect(container.textContent).toContain("/users");
  });

  it("expands endpoint details", () => {
    const { container, getByText } = render(<ExtensionApiExplorer groups={mockGroups} extensionName="Test" />);
    fireEvent.click(getByText("List users"));
    expect(container.textContent).toContain("Parameters");
    expect(container.textContent).toContain("limit");
    expect(container.textContent).toContain("Response");
  });

  it("switches groups", () => {
    const { container, getByText } = render(<ExtensionApiExplorer groups={mockGroups} extensionName="Test" />);
    fireEvent.click(getByText("Config (1)"));
    expect(container.textContent).toContain("/config");
  });
});
