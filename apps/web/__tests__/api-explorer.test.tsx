import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiExplorer } from "@/components/api-explorer";

describe("ApiExplorer", () => {
  const endpoints = [
    { method: "GET", path: "/api/v1/apps", summary: "List apps", auth: true, tags: ["apps"] },
    { method: "GET", path: "/api/v1/health", summary: "Health", auth: false, tags: ["system"] },
  ];
  it("renders endpoints", () => {
    const { container } = render(<ApiExplorer endpoints={endpoints} tags={["apps", "system"]} />);
    expect(container.textContent).toContain("API Explorer");
    expect(container.textContent).toContain("/api/v1/apps");
    expect(container.textContent).toContain("/api/v1/health");
    expect(container.textContent).toContain("2 endpoints");
  });
  it("filters by tag", () => {
    const { container } = render(<ApiExplorer endpoints={endpoints} tags={["apps", "system"]} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "apps")!);
    expect(container.textContent).toContain("1 endpoints");
    expect(container.textContent).toContain("/api/v1/apps");
  });
});
