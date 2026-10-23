import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ActiveUsersCard } from "@/components/active-users-card";

describe("ActiveUsersCard", () => {
  it("renders users", () => {
    const { container } = render(
      <ActiveUsersCard dauDisplay="5,000" wauDisplay="15,000" mauDisplay="25,000"
        stickinessDisplay="20.0%" engagement="high" />
    );
    expect(container.textContent).toContain("Active Users");
    expect(container.textContent).toContain("5,000");
    expect(container.textContent).toContain("DAU");
    expect(container.textContent).toContain("25,000");
    expect(container.textContent).toContain("MAU");
    expect(container.textContent).toContain("20.0%");
    expect(container.textContent).toContain("high engagement");
  });
});
