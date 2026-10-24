import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone321kSolid3700 } from "@/components/milestone-321k-solid-3700";
describe("Milestone321kSolid3700", () => { it("renders", () => {
    const { container } = render(<Milestone321kSolid3700 />);
    expect(container.textContent).toContain("321K+");
    expect(container.textContent).toContain("3,700");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
