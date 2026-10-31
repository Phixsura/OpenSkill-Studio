import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import DeprecationPlannerCard from "../src/components/api-developer-platform-sdk-consumer-api-deprecation-planner-card";

describe("DeprecationPlannerCard", () => {
  it("renders title and plans", () => {
    const { container } = render(<DeprecationPlannerCard />);
    expect(container.textContent).toContain("Deprecation Planner");
    expect(container.textContent).toContain("/v1/users");
    expect(container.textContent).toContain("/v2/users");
  });

  it("shows migration progress and sunset date", () => {
    const { container } = render(<DeprecationPlannerCard />);
    expect(container.textContent).toContain("75% migrated");
    expect(container.textContent).toContain("2024-06-01");
    expect(container.textContent).toContain("2 deprecation plans");
  });
});
