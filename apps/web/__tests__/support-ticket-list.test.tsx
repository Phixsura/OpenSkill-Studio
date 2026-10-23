import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SupportTicketList } from "@/components/support-ticket-list";

describe("SupportTicketList", () => {
  const tickets = [
    { id: "TKT-ABC1", subject: "App crash", priority: "urgent", status: "open", createdAt: "2026-01-01" },
    { id: "TKT-DEF2", subject: "Feature request", priority: "low", status: "resolved", createdAt: "2026-01-02" },
  ];
  it("renders tickets", () => {
    const { container } = render(<SupportTicketList tickets={tickets} openCount={1} hasUrgent={true} />);
    expect(container.textContent).toContain("App crash");
    expect(container.textContent).toContain("TKT-ABC1");
    expect(container.textContent).toContain("urgent");
    expect(container.textContent).toContain("Urgent");
    expect(container.textContent).toContain("1 open");
  });
});
