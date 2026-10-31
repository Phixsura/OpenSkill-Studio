import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SecPostureCard } from "@/components/sec-posture-card";

describe("SecPostureCard", () => {
  it("renders posture", () => {
    const { container } = render(
      <SecPostureCard score={85} grade="B" implemented={7} total={9}
        controls={[
          { control: "mfa_enabled", passed: true, weight: 15, category: "identity" },
          { control: "secrets_rotation", passed: false, weight: 10, category: "secrets" },
        ]} />
    );
    expect(container.textContent).toContain("B");
    expect(container.textContent).toContain("85/100");
    expect(container.textContent).toContain("7/9 controls");
    expect(container.textContent).toContain("mfa enabled");
    expect(container.textContent).toContain("secrets rotation");
  });
});
