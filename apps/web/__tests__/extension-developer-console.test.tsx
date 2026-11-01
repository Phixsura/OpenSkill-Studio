import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ExtensionDeveloperConsole } from "@/components/extension-developer-console";

const mockSections = [
  { id: "sandbox", label: "Sandbox", icon: "📦", count: 3, status: "ok" as const },
  { id: "webhooks", label: "Webhooks", icon: "🔗", count: 12, status: "warning" as const },
  { id: "metrics", label: "Metrics", icon: "📊" },
  { id: "logs", label: "Logs", icon: "📜", status: "error" as const },
  { id: "builds", label: "Builds", icon: "🏗️", count: 45 },
  { id: "settings", label: "Settings", icon: "⚙️" },
];

const mockStats = [
  { label: "Installs", value: "12.5K", trend: "up" as const },
  { label: "API Calls", value: "450K", trend: "flat" as const },
  { label: "Error Rate", value: "0.3%", trend: "down" as const },
  { label: "Revenue", value: "$2.4K", trend: "up" as const },
];

describe("ExtensionDeveloperConsole", () => {
  it("renders extension info and stats", () => {
    const { container } = render(
      <ExtensionDeveloperConsole extensionName="Slack Bot Pro" version="2.1.0"
        sections={mockSections} quickStats={mockStats} />
    );
    expect(container.textContent).toContain("Slack Bot Pro");
    expect(container.textContent).toContain("v2.1.0");
    expect(container.textContent).toContain("12.5K");
    expect(container.textContent).toContain("$2.4K");
  });

  it("renders section cards", () => {
    const { container } = render(
      <ExtensionDeveloperConsole extensionName="Test" version="1.0"
        sections={mockSections} quickStats={[]} />
    );
    expect(container.textContent).toContain("Sandbox");
    expect(container.textContent).toContain("Webhooks");
    expect(container.textContent).toContain("12 items");
  });

  it("calls onNavigate", () => {
    const onNav = vi.fn();
    const { getByText } = render(
      <ExtensionDeveloperConsole extensionName="Test" version="1.0"
        sections={mockSections} quickStats={[]} onNavigate={onNav} />
    );
    fireEvent.click(getByText("Sandbox"));
    expect(onNav).toHaveBeenCalledWith("sandbox");
  });

  it("shows trend icons", () => {
    const { container } = render(
      <ExtensionDeveloperConsole extensionName="Test" version="1.0"
        sections={[]} quickStats={mockStats} />
    );
    expect(container.textContent).toContain("📈");
    expect(container.textContent).toContain("📉");
  });
});
