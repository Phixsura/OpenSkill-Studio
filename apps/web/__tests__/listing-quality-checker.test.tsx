import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ListingQualityChecker } from "@/components/listing-quality-checker";

describe("ListingQualityChecker", () => {
  it("renders checker", () => {
    const { container } = render(
      <ListingQualityChecker score={67} ready={false} passed={4} total={6} checks={[
        { field: "name", passed: true, message: "Name OK" },
        { field: "description", passed: false, message: "Description too short" },
      ]} />
    );
    expect(container.textContent).toContain("Listing Quality");
    expect(container.textContent).toContain("67%");
    expect(container.textContent).toContain("2 issues");
    expect(container.textContent).toContain("Name OK");
    expect(container.textContent).toContain("Description too short");
  });
});
