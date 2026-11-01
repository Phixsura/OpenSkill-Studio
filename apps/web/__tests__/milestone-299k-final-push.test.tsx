import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone299kFinalPush } from "@/components/milestone-299k-final-push";
describe("Milestone299kFinalPush", () => { it("renders", () => {
    const { container } = render(<Milestone299kFinalPush />);
    expect(container.textContent).toContain("THE FINAL PUSH");
    expect(container.textContent).toContain("300,000");
}); });
