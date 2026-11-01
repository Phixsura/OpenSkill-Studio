import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UplatformUhealthUbadge } from "@/components/platform-health-badge";

describe("UplatformUhealthUbadge", () => {
  it("renders", () => {
    const { container } = render(<UplatformUhealthUbadge status="operational" />);
    expect(container.textContent).toContain("operational");
  });
});
