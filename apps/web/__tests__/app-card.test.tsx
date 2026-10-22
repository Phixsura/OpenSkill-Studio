import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppCard } from "@/components/app-card";

const BASE_PROPS = {
  id: "app-001",
  name: "Test App",
  slug: "test-app",
  description: "A test application",
  category: "connector",
  status: "published",
};

describe("AppCard", () => {
  it("renders app name", () => {
    const { container } = render(<AppCard {...BASE_PROPS} />);
    expect(container.textContent).toContain("Test App");
  });

  it("renders description", () => {
    const { container } = render(<AppCard {...BASE_PROPS} />);
    expect(container.textContent).toContain("A test application");
  });

  it("renders null description", () => {
    const { container } = render(<AppCard {...BASE_PROPS} description={null} />);
    expect(container.textContent).toContain("Test App");
  });

  it("renders install count", () => {
    const { container } = render(<AppCard {...BASE_PROPS} installCount={42} />);
    expect(container.textContent).toContain("42");
  });

  it("renders developer name", () => {
    const { container } = render(<AppCard {...BASE_PROPS} developerName="Dev Studio" />);
    expect(container.textContent).toContain("Dev Studio");
  });
});
