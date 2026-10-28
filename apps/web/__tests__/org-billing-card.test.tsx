import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import OrgBillingCard from "../src/components/org-billing-card";

const invoices = [
  {
    invoice_id: "INV-001",
    status: "paid" as const,
    total_dollars: 15.0,
    due_date: "2026-10-28",
    item_count: 2,
  },
  {
    invoice_id: "INV-002",
    status: "sent" as const,
    total_dollars: 29.0,
    due_date: "2026-11-15",
    item_count: 3,
  },
  {
    invoice_id: "INV-003",
    status: "overdue" as const,
    total_dollars: 49.0,
    due_date: "2026-10-01",
    item_count: 1,
  },
];

describe("OrgBillingCard", () => {
  it("renders header and app name", () => {
    const { container } = render(
      <OrgBillingCard invoices={invoices} outstandingDollars={78} appName="My App" />,
    );
    expect(container.textContent).toContain("Billing");
    expect(container.textContent).toContain("My App");
  });

  it("shows outstanding balance", () => {
    const { container } = render(
      <OrgBillingCard invoices={invoices} outstandingDollars={78} appName="App" />,
    );
    expect(container.textContent).toContain("$78.00");
    expect(container.textContent).toContain("outstanding");
  });

  it("renders invoice ids", () => {
    const { container } = render(
      <OrgBillingCard invoices={invoices} outstandingDollars={0} appName="App" />,
    );
    expect(container.textContent).toContain("INV-001");
    expect(container.textContent).toContain("INV-002");
  });

  it("shows status badges", () => {
    const { container } = render(
      <OrgBillingCard invoices={invoices} outstandingDollars={0} appName="App" />,
    );
    expect(container.textContent).toContain("paid");
    expect(container.textContent).toContain("sent");
    expect(container.textContent).toContain("overdue");
  });

  it("shows totals", () => {
    const { container } = render(
      <OrgBillingCard invoices={invoices} outstandingDollars={0} appName="App" />,
    );
    expect(container.textContent).toContain("$15.00");
    expect(container.textContent).toContain("$29.00");
  });

  it("shows item counts", () => {
    const { container } = render(
      <OrgBillingCard invoices={invoices} outstandingDollars={0} appName="App" />,
    );
    expect(container.textContent).toContain("2 items");
  });

  it("shows empty state", () => {
    const { container } = render(
      <OrgBillingCard invoices={[]} outstandingDollars={0} appName="App" />,
    );
    expect(container.textContent).toContain("No invoices");
  });
});
