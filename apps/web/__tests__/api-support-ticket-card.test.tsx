import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APISupportTicketCard from "../src/components/api-support-ticket-card";

const tickets = [
  { ticket_id: "t1", subject: "Auth failing", priority: "high" as const, status: "in_progress" as const, assignee: "bob" },
  { ticket_id: "t2", subject: "Docs unclear", priority: "low" as const, status: "resolved" as const, assignee: "" },
];

describe("APISupportTicketCard", () => {
  it("renders header and open count", () => {
    const { container } = render(<APISupportTicketCard tickets={tickets} appName="App" />);
    expect(container.textContent).toContain("Support Tickets");
    expect(container.textContent).toContain("1 open / 2 total");
  });

  it("shows priority and subject", () => {
    const { container } = render(<APISupportTicketCard tickets={tickets} appName="App" />);
    expect(container.textContent).toContain("high");
    expect(container.textContent).toContain("Auth failing");
    expect(container.textContent).toContain("in progress");
  });

  it("shows empty state", () => {
    const { container } = render(<APISupportTicketCard tickets={[]} appName="App" />);
    expect(container.textContent).toContain("No support tickets");
  });
});
