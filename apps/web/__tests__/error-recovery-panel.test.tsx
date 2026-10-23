import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ErrorRecoveryPanel } from "@/components/error-recovery-panel";

describe("ErrorRecoveryPanel", () => {
  const strategy = { strategy: "retry", description: "Retry the operation", icon: "🔄", autoRecoverable: true };
  it("renders recovery info", () => {
    const { container } = render(
      <ErrorRecoveryPanel strategy={strategy} retryCount={1} maxRetries={3} recoveryRate={85} totalErrors={20} />
    );
    expect(container.textContent).toContain("retry");
    expect(container.textContent).toContain("85%");
    expect(container.textContent).toContain("Auto");
    expect(container.textContent).toContain("1/3");
  });
});
