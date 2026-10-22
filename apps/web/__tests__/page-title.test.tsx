import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PageTitle } from "@/components/page-title";

describe("PageTitle", () => {
  it("shows title", () => {
    const { container } = render(<PageTitle title="My Apps" subtitle="Manage your apps" />);
    expect(container.textContent).toContain("My Apps");
    expect(container.textContent).toContain("Manage your apps");
  });
});
