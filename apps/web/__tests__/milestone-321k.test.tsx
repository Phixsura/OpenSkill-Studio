import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone321k } from "@/components/milestone-321k";
describe("Milestone321k", () => { it("renders", () => {
    const { container } = render(<Milestone321k />);
    expect(container.textContent).toContain("321K");
}); });
