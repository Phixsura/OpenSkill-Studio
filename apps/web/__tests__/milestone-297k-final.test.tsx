import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone297kFinal } from "@/components/milestone-297k-final";
describe("Milestone297kFinal", () => { it("renders", () => {
    const { container } = render(<Milestone297kFinal />);
    expect(container.textContent).toContain("297K");
}); });
