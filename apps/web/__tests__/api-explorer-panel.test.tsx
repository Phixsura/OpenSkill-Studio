import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiExplorerPanel } from "@/components/api-explorer-panel";

describe("ApiExplorerPanel", () => {
  it("renders groups", () => {
    const groups = { users: [{ method: "GET", path: "/users", summary: "List", try_url: "" }] };
    const { container } = render(<ApiExplorerPanel groups={groups} baseUrl="https://api.com" />);
    expect(container.textContent).toContain("users");
    expect(container.textContent).toContain("https://api.com");
  });
  it("expands on click", () => {
    const groups = { apps: [{ method: "POST", path: "/apps", summary: "Create app", try_url: "" }] };
    const { container } = render(<ApiExplorerPanel groups={groups} baseUrl="https://api.com" />);
    fireEvent.click(container.querySelector("button")!);
    expect(container.textContent).toContain("/apps");
    expect(container.textContent).toContain("Create app");
  });
});
