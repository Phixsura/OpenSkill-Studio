import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SessionHallOfFame } from "@/components/session-hall-of-fame";
describe("SessionHallOfFame", () => { it("renders", () => {
    const { container } = render(<SessionHallOfFame />);
    expect(container.textContent).toContain("HALL OF FAME");
    expect(container.textContent).toContain("LEGENDARY");
}); });
