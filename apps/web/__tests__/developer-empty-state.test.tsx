import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeveloperEmptyState } from "@/components/developer-empty-state";

describe("DeveloperEmptyState", () => {
  it("shows title", () => {
    const { container } = render(<DeveloperEmptyState title="No Apps" description="Create your first app" />);
    expect(container.textContent).toContain("No Apps");
  });

  it("shows description", () => {
    const { container } = render(<DeveloperEmptyState title="X" description="Get started here" />);
    expect(container.textContent).toContain("Get started here");
  });

  it("shows action button", () => {
    const { container } = render(<DeveloperEmptyState title="X" description="Y" actionLabel="Create App" actionHref="/new" />);
    const link = container.querySelector("a");
    expect(link?.textContent).toContain("Create App");
  });

  it("shows custom icon", () => {
    const { container } = render(<DeveloperEmptyState title="X" description="Y" icon="🚀" />);
    expect(container.textContent).toContain("🚀");
  });

  it("hides action when no href", () => {
    const { container } = render(<DeveloperEmptyState title="X" description="Y" />);
    expect(container.querySelector("a")).toBeNull();
  });
});
