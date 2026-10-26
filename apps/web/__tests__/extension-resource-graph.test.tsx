import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ExtensionResourceGraph } from "@/components/extension-resource-graph";

const mockData = [
  { timestamp: "12:00", cpu: 30, memory: 128, network: 50 },
  { timestamp: "12:01", cpu: 45, memory: 150, network: 80 },
  { timestamp: "12:02", cpu: 60, memory: 180, network: 120 },
  { timestamp: "12:03", cpu: 85, memory: 200, network: 90 },
  { timestamp: "12:04", cpu: 50, memory: 170, network: 60 },
];

describe("ExtensionResourceGraph", () => {
  it("renders extension name and current values", () => {
    const { container } = render(
      <ExtensionResourceGraph data={mockData} extensionName="Slack Bot" cpuLimit={100} memoryLimit={256} />
    );
    expect(container.textContent).toContain("Slack Bot Resources");
    expect(container.textContent).toContain("CPU:");
    expect(container.textContent).toContain("Mem:");
    expect(container.textContent).toContain("Net:");
  });

  it("shows resource bars", () => {
    const { container } = render(
      <ExtensionResourceGraph data={mockData} extensionName="Test" cpuLimit={100} memoryLimit={256} />
    );
    expect(container.textContent).toContain("CPU");
    expect(container.textContent).toContain("Memory");
    expect(container.textContent).toContain("/ 100%");
    expect(container.textContent).toContain("/ 256MB");
  });

  it("shows timeline", () => {
    const { container } = render(
      <ExtensionResourceGraph data={mockData} extensionName="Test" cpuLimit={100} memoryLimit={256} />
    );
    expect(container.textContent).toContain("12:00");
    expect(container.textContent).toContain("12:04");
  });
});
