import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { QueueDashboard } from "@/components/queue-dashboard";

describe("QueueDashboard", () => {
  it("renders stats", () => {
    const { container } = render(
      <QueueDashboard stats={{ pending: 25, processed: 100, maxSize: 1000, utilizationPct: 2.5 }} />
    );
    expect(container.textContent).toContain("25");
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("2.5%");
    expect(container.textContent).toContain("Pending");
    expect(container.textContent).toContain("Processed");
  });
});
