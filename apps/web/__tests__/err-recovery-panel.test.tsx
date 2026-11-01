import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ErrRecoveryPanel } from "@/components/err-recovery-panel";

describe("ErrRecoveryPanel", () => {
  it("renders recovery", () => {
    const { container } = render(
      <ErrRecoveryPanel totalEvents={10} autoRecovered={7} autoPct={70}
        byStrategy={{ retry: 4, fallback: 2, circuit_break: 1, alert: 3 }} />
    );
    expect(container.textContent).toContain("Error Recovery");
    expect(container.textContent).toContain("70% auto-recovered");
    expect(container.textContent).toContain("7");
    expect(container.textContent).toContain("retry");
    expect(container.textContent).toContain("fallback");
    expect(container.textContent).toContain("alert");
  });
});
