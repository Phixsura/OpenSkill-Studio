import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GrandFinalStatus } from "@/components/grand-final-status";

describe("GrandFinalStatus", () => {
  it("renders", () => {
    const { container } = render(<GrandFinalStatus />);
    expect(container.textContent).toContain("232K+");
    expect(container.textContent).toContain("2,691");
    expect(container.textContent).toContain("7,882+");
    expect(container.textContent).toContain("ALL SYSTEMS GREEN");
  });
});
