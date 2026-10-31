import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SecretRotateDash } from "@/components/secret-rotate-dash";

describe("SecretRotateDash", () => {
  it("renders", () => {
    const { container } = render(
      <SecretRotateDash overdueCount={1} maxAgeDays={90}
        secrets={[
          { name: "db_pass", ageDays: 100, overdue: true, daysUntilRotation: 0, type: "password" },
          { name: "api_key", ageDays: 10, overdue: false, daysUntilRotation: 80, type: "api_key" },
        ]} />
    );
    expect(container.textContent).toContain("Secret Rotation");
    expect(container.textContent).toContain("1 overdue");
    expect(container.textContent).toContain("90d policy");
    expect(container.textContent).toContain("db_pass");
    expect(container.textContent).toContain("ROTATE NOW");
    expect(container.textContent).toContain("80d left");
  });
});
