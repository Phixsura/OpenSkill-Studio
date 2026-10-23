import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApiPlaygroundPanel } from "@/components/api-playground-panel";

describe("ApiPlaygroundPanel", () => {
  const endpoints = [
    { method: "GET", path: "/api/v1/apps", description: "List apps", auth_required: false },
    { method: "POST", path: "/api/v1/apps", description: "Create app", auth_required: true },
  ];
  it("renders", () => {
    const { container } = render(<ApiPlaygroundPanel endpoints={endpoints} onExecute={vi.fn()} />);
    expect(container.textContent).toContain("API Playground");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/v1/apps");
    expect(container.textContent).toContain("🔒");
  });
  it("select and execute", () => {
    const fn = vi.fn();
    const { container } = render(<ApiPlaygroundPanel endpoints={endpoints} onExecute={fn} />);
    const cards = container.querySelectorAll(".cursor-pointer");
    fireEvent.click(cards[0]);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Send Request")!);
    expect(fn).toHaveBeenCalledWith("GET", "/api/v1/apps");
  });
});
