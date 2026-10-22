import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeveloperProfileHeader } from "@/components/developer-profile-header";

describe("DeveloperProfileHeader", () => {
  it("shows name", () => {
    const { container } = render(<DeveloperProfileHeader name="Dev Co" verified={true} appCount={5} totalInstalls={200} categories={["connector"]} />);
    expect(container.textContent).toContain("Dev Co");
    expect(container.textContent).toContain("Verified");
    expect(container.textContent).toContain("5 apps");
  });
  it("shows categories", () => {
    const { container } = render(<DeveloperProfileHeader name="X" verified={false} appCount={0} totalInstalls={0} categories={["connector", "automation"]} />);
    expect(container.textContent).toContain("connector");
  });
});
