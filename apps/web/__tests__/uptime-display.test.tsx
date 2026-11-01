import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UptimeDisplay } from "@/components/uptime-display";

describe("UptimeDisplay", () => {
  it("renders uptime stats", () => {
    const { container } = render(
      <UptimeDisplay uptimePct={99.95} nines={3} ninesLabel="999s" downtimeMinutes={22} budgetMinutes={43} />
    );
    expect(container.textContent).toContain("99.95%");
    expect(container.textContent).toContain("999s");
    expect(container.textContent).toContain("22m");
    expect(container.textContent).toContain("43m");
    expect(container.textContent).toContain("budget used");
  });
});
