import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SupportPage } from "@/components/support-page";

describe("SupportPage", () => {
  const resources = [
    { id: "docs", title: "Documentation", icon: "📖", href: "/docs", description: "Guides" },
    { id: "faq", title: "FAQ", icon: "❓", href: "/faq", description: "Questions" },
  ];
  it("renders support page", () => {
    const { container } = render(
      <SupportPage resources={resources} openTickets={2} recentIncidents={1}
        hasAlerts={true} onNavigate={vi.fn()} />
    );
    expect(container.textContent).toContain("Help & Support");
    expect(container.textContent).toContain("Documentation");
    expect(container.textContent).toContain("FAQ");
    expect(container.textContent).toContain("2 open tickets");
    expect(container.textContent).toContain("1 active incident");
  });
});
