import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RevenueDashboardCard } from "@/components/revenue-dashboard-card";

describe("RevenueDashboardCard", () => {
  it("renders revenue data", () => {
    const { container } = render(
      <RevenueDashboardCard mrr="$1,000" arr="$12,000" arpu="$20" customers={50} growthPct={25} growthDirection="up" />
    );
    expect(container.textContent).toContain("$1,000");
    expect(container.textContent).toContain("$12,000");
    expect(container.textContent).toContain("50");
    expect(container.textContent).toContain("25%");
  });
  it("shows down trend", () => {
    const { container } = render(
      <RevenueDashboardCard mrr="$500" arr="$6,000" arpu="$10" customers={50} growthPct={-10} growthDirection="down" />
    );
    expect(container.textContent).toContain("📉");
  });
});
