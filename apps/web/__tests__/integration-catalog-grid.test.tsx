import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { IntegrationCatalogGrid } from "@/components/integration-catalog-grid";

describe("IntegrationCatalogGrid", () => {
  const integrations = [
    { id: "slack", name: "Slack", icon: "💬", category: "comm", description: "Chat", popular: true },
    { id: "github", name: "GitHub", icon: "🐙", category: "dev", description: "Code", popular: false },
  ];
  it("renders", () => {
    const { container } = render(<IntegrationCatalogGrid integrations={integrations} onConnect={vi.fn()} />);
    expect(container.textContent).toContain("Integrations");
    expect(container.textContent).toContain("Slack");
    expect(container.textContent).toContain("GitHub");
    expect(container.textContent).toContain("⭐ Popular");
  });
  it("connect", () => {
    const fn = vi.fn();
    const { container } = render(<IntegrationCatalogGrid integrations={integrations} onConnect={fn} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Connect")!);
    expect(fn).toHaveBeenCalledWith("slack");
  });
});
