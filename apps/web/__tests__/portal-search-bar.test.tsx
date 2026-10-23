import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PortalSearchBar } from "@/components/portal-search-bar";

describe("PortalSearchBar", () => {
  it("renders input", () => {
    const { container } = render(<PortalSearchBar onSearch={vi.fn()} results={[]} />);
    expect(container.querySelector("input")).toBeTruthy();
  });
  it("shows results", () => {
    const results = [{ type: "doc", title: "Webhook Guide", url: "/docs/webhooks" }];
    const { container } = render(<PortalSearchBar onSearch={vi.fn()} results={results} />);
    const input = container.querySelector("input")!;
    fireEvent.change(input, { target: { value: "webhook" } });
    expect(container.textContent).toContain("Webhook Guide");
  });
});
