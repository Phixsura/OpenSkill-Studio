import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StatusBadgeDisplay } from "@/components/status-badge-display";

describe("StatusBadgeDisplay", () => {
  it("renders badges", () => {
    const { container } = render(
      <StatusBadgeDisplay title="🏷️ Status Badges" badges={[
        { label: "status", value: "operational", color: "#22C55E" },
        { label: "uptime", value: "99.95%", color: "#22C55E" },
        { label: "build", value: "passing", color: "#3B82F6" },
      ]} />
    );
    expect(container.textContent).toContain("Status Badges");
    expect(container.textContent).toContain("operational");
    expect(container.textContent).toContain("99.95%");
    expect(container.textContent).toContain("passing");
  });
});
