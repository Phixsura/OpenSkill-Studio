import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StatCounterRow } from "@/components/stat-counter-row";

describe("StatCounterRow", () => {
  const counters = [
    { key: "apps", value: 500, label: "Total Apps", icon: "📦", format: "number" },
    { key: "users", value: 50000, label: "Users", icon: "👥", format: "compact" },
    { key: "revenue", value: 85000, label: "Revenue", icon: "💰", format: "currency" },
  ];
  it("renders", () => {
    const { container } = render(<StatCounterRow counters={counters} />);
    expect(container.textContent).toContain("📦");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("50.0K");
    expect(container.textContent).toContain("$85,000");
    expect(container.textContent).toContain("Total Apps");
  });
});
