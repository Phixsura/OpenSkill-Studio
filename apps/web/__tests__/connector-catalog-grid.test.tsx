import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ConnectorCatalogGrid } from "@/components/connector-catalog-grid";

const connectors = [
  { connectorId: "slack", name: "Slack", provider: "Slack Inc", category: "communication", icon: "💬", installedCount: 500, status: "available" },
  { connectorId: "stripe", name: "Stripe", provider: "Stripe Inc", category: "payment", icon: "💳", installedCount: 300, status: "beta" },
];

describe("ConnectorCatalogGrid", () => {
  it("renders connectors", () => {
    const { container } = render(<ConnectorCatalogGrid connectors={connectors} />);
    expect(container.textContent).toContain("Slack");
    expect(container.textContent).toContain("Stripe");
    expect(container.textContent).toContain("beta");
  });
  it("filters by category", () => {
    const { container } = render(<ConnectorCatalogGrid connectors={connectors} />);
    const catBtns = container.querySelectorAll("button");
    // click payment category
    const paymentBtn = Array.from(catBtns).find(b => b.textContent?.includes("payment"));
    if (paymentBtn) fireEvent.click(paymentBtn);
    expect(container.textContent).toContain("Stripe");
  });
});
