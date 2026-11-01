import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import EnvManagerCard from "../src/components/api-developer-platform-sdk-consumer-api-env-manager-card";

describe("EnvManagerCard", () => {
  it("renders title and environments", () => {
    const { container } = render(<EnvManagerCard />);
    expect(container.textContent).toContain("Environment Manager");
    expect(container.textContent).toContain("development");
    expect(container.textContent).toContain("staging");
    expect(container.textContent).toContain("production");
  });

  it("shows var counts and promotion flow", () => {
    const { container } = render(<EnvManagerCard />);
    expect(container.textContent).toContain("12 vars");
    expect(container.textContent).toContain("5 secrets");
    expect(container.textContent).toContain("dev → staging → production");
  });
});
