import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StatusSummaryPie } from "@/components/status-summary-pie";

describe("StatusSummaryPie", () => {
  it("shows statuses", () => {
    const { container } = render(<StatusSummaryPie byStatus={{ published: 3, draft: 2 }} total={5} />);
    expect(container.textContent).toContain("published");
    expect(container.textContent).toContain("3");
    expect(container.textContent).toContain("60%");
  });
  it("empty state", () => {
    const { container } = render(<StatusSummaryPie byStatus={{}} total={0} />);
    expect(container.textContent).toContain("No apps");
  });
});
