import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppDetailHeader } from "@/components/app-detail-header";

describe("AppDetailHeader", () => {
  it("shows name", () => {
    const { container } = render(<AppDetailHeader name="My App" slug="my-app" category="connector" status="published" />);
    expect(container.textContent).toContain("My App");
  });

  it("shows slug", () => {
    const { container } = render(<AppDetailHeader name="X" slug="my-app" category="connector" status="draft" />);
    expect(container.textContent).toContain("@my-app");
  });

  it("shows developer", () => {
    const { container } = render(<AppDetailHeader name="X" slug="x" category="connector" status="draft" developerName="Dev Co" />);
    expect(container.textContent).toContain("Dev Co");
  });

  it("shows status badge", () => {
    const { container } = render(<AppDetailHeader name="X" slug="x" category="connector" status="published" />);
    expect(container.textContent).toContain("published");
  });

  it("shows category", () => {
    const { container } = render(<AppDetailHeader name="X" slug="x" category="ui_extension" status="draft" />);
    expect(container.textContent).toContain("ui extension");
  });
});
