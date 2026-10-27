import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { QueueDashboard } from "@/components/queue-dashboard";

const queues = [
  { name: "emails", pending: 5, processing: 2, completed: 100, dead: 1 },
  { name: "sync", pending: 0, processing: 0, completed: 50, dead: 0 },
];

describe("QueueDashboard", () => {
  it("renders queues", () => {
    const { container } = render(<QueueDashboard queues={queues} />);
    expect(container.textContent).toContain("emails");
    expect(container.textContent).toContain("5 pending");
    expect(container.textContent).toContain("1 dead");
    expect(container.textContent).toContain("108 total");
  });
  it("empty state", () => {
    const { container } = render(<QueueDashboard queues={[]} />);
    expect(container.textContent).toContain("No queues");
  });
});
