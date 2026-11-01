import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApiVersionPanel } from "@/components/api-version-panel";

const mockVersions = [
  { version: "v2", status: "active" as const, endpoints: 15, requests: 50000, isDefault: true },
  { version: "v1", status: "deprecated" as const, endpoints: 10, requests: 120000, isDefault: false, sunsetDate: "2025-06-01" },
  { version: "v3", status: "beta" as const, endpoints: 20, requests: 500, isDefault: false },
];

describe("ApiVersionPanel", () => {
  it("renders versions with status", () => {
    const { container } = render(<ApiVersionPanel versions={mockVersions} />);
    expect(container.textContent).toContain("v2");
    expect(container.textContent).toContain("default");
    expect(container.textContent).toContain("deprecated");
    expect(container.textContent).toContain("beta");
  });

  it("shows endpoint and request counts", () => {
    const { container } = render(<ApiVersionPanel versions={mockVersions} />);
    expect(container.textContent).toContain("15 endpoints");
    expect(container.textContent).toContain("50,000 requests");
  });

  it("shows sunset date", () => {
    const { container } = render(<ApiVersionPanel versions={mockVersions} />);
    expect(container.textContent).toContain("2025-06-01");
  });

  it("calls onDeprecate", () => {
    const onDeprecate = vi.fn();
    const { getAllByText } = render(<ApiVersionPanel versions={mockVersions} onDeprecate={onDeprecate} />);
    fireEvent.click(getAllByText("Deprecate")[0]);
    expect(onDeprecate).toHaveBeenCalledWith("v2");
  });
});
