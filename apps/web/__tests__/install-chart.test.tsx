import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { InstallChart } from "@/components/install-chart";

describe("InstallChart", () => {
  it("renders chart", () => {
    const data = [{ date: "2026-10-01", count: 10 }, { date: "2026-10-02", count: 20 }];
    const { container } = render(
      <InstallChart data={data} growthPct={25} trend="up" peakDay={{ date: "2026-10-02", count: 20 }} />
    );
    expect(container.textContent).toContain("+25%");
    expect(container.textContent).toContain("📈");
    expect(container.textContent).toContain("Peak: 20");
  });
});
