import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SupportTicketList } from "@/components/support-ticket-list";

describe("SupportTicketList", () => {
  it("renders tickets", () => {
    const onSelect = vi.fn();
    const { container, getAllByRole } = render(
      <SupportTicketList openCount={2} onSelect={onSelect} onCreate={vi.fn()}
        tickets={[
          { id: "TKT-0001", title: "Login broken", priority: "high", status: "open", replies: 2 },
          { id: "TKT-0002", title: "Slow API", priority: "medium", status: "open", replies: 0 },
        ]} />
    );
    expect(container.textContent).toContain("Support Tickets");
    expect(container.textContent).toContain("2 open");
    expect(container.textContent).toContain("TKT-0001");
    expect(container.textContent).toContain("Login broken");
    expect(container.textContent).toContain("high");
    const btns = getAllByRole("button");
    fireEvent.click(btns[1]); // first ticket
    expect(onSelect).toHaveBeenCalledWith("TKT-0001");
  });
});
