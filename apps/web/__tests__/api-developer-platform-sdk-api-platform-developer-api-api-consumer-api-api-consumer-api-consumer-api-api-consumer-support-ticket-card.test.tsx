import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-support-ticket-card";

describe("ConsumerApiSupportTicketCard", () => {
  it("shows tickets", () => {
    const tickets = [{ id: "t1", subject: "API Error 500", priority: "high", status: "open", createdAt: "2026-06-01", replyCount: 2 }];
    const { container } = render(<Card tickets={tickets} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Support Tickets");
    expect(container.textContent).toContain("API Error 500");
    expect(container.textContent).toContain("high");
    expect(container.textContent).toContain("open");
    expect(container.textContent).toContain("2 replies");
  });
  it("shows empty", () => {
    const { container } = render(<Card tickets={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No tickets");
  });
});
