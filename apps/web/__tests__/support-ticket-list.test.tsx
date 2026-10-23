import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SupportTicketList } from "@/components/support-ticket-list";

describe("SupportTicketList", () => {
  const tickets = [
    { ticket_id: "TKT-001", subject: "Install error", priority: "high", status: "open", created_at: "2026-10-20T00:00:00" },
  ];
  it("renders", () => {
    const { container } = render(<SupportTicketList tickets={tickets} onSelect={vi.fn()} />);
    expect(container.textContent).toContain("Support Tickets");
    expect(container.textContent).toContain("Install error");
    expect(container.textContent).toContain("TKT-001");
    expect(container.textContent).toContain("high");
  });
  it("select", () => {
    const fn = vi.fn();
    const { container } = render(<SupportTicketList tickets={tickets} onSelect={fn} />);
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalledWith("TKT-001");
  });
});
