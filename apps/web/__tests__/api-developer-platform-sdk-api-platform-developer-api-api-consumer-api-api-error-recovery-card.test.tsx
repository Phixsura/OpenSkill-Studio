import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-error-recovery-card";

describe("ErrorRecoveryCard", () => {
  it("shows rules and rate", () => {
    const rules = [{ rule_id: "r1", error_pattern: "503", action: "fallback" }];
    const { container } = render(<Card rules={rules} recoveryRate={85} totalRecoveries={100} appName="App" />);
    expect(container.textContent).toContain("Error Recovery");
    expect(container.textContent).toContain("85%");
    expect(container.textContent).toContain("503");
    expect(container.textContent).toContain("fallback");
  });
  it("shows empty", () => {
    const { container } = render(<Card rules={[]} recoveryRate={0} totalRecoveries={0} appName="App" />);
    expect(container.textContent).toContain("No recovery rules");
  });
});
