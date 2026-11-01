import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CapabilityRegistryPanel } from "@/components/capability-registry-panel";

const mockExts = [
  { extensionId: "ext-chart", provides: [{ name: "chart", version: "2.0", description: "Charting" }],
    requires: [], requirementsMet: true, missingRequirements: [] },
  { extensionId: "ext-app", provides: [{ name: "dashboard", version: "1.0", description: "" }],
    requires: ["auth", "chart"], requirementsMet: false, missingRequirements: ["auth"] },
];

describe("CapabilityRegistryPanel", () => {
  it("renders extensions with capabilities", () => {
    const { container } = render(
      <CapabilityRegistryPanel extensions={mockExts} allCapabilities={["chart", "auth", "dashboard"]} />
    );
    expect(container.textContent).toContain("ext-chart");
    expect(container.textContent).toContain("1 capabilities");
  });

  it("shows missing requirements", () => {
    const { container } = render(
      <CapabilityRegistryPanel extensions={mockExts} allCapabilities={[]} />
    );
    expect(container.textContent).toContain("1 missing");
  });

  it("expands to show details", () => {
    const { getByText, container } = render(
      <CapabilityRegistryPanel extensions={mockExts} allCapabilities={[]} />
    );
    fireEvent.click(getByText("ext-chart"));
    expect(container.textContent).toContain("chart v2.0");
  });

  it("filters by capability search", () => {
    const { container } = render(
      <CapabilityRegistryPanel extensions={mockExts} allCapabilities={["chart"]} />
    );
    const input = container.querySelector("input");
    if (input) fireEvent.change(input, { target: { value: "dashboard" } });
    expect(container.textContent).toContain("ext-app");
    expect(container.textContent).not.toContain("ext-chart");
  });
});
