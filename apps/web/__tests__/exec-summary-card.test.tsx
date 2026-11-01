import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ExecSummaryCard } from "@/components/exec-summary-card";

describe("ExecSummaryCard", () => {
  it("renders summary", () => {
    const { container } = render(
      <ExecSummaryCard health="strong" summary="Platform strong with 500 apps"
        kpis={[
          { name: "Revenue", value: "$100,000", trend: "up" },
          { name: "Apps", value: "500", trend: "up" },
          { name: "Users", value: "25,000", trend: "up" },
        ]} />
    );
    expect(container.textContent).toContain("Executive Summary");
    expect(container.textContent).toContain("strong");
    expect(container.textContent).toContain("$100,000");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("25,000");
    expect(container.textContent).toContain("Platform strong");
  });
});
