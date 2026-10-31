import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import TeamManagerCard from "../src/components/api-developer-platform-sdk-consumer-api-team-manager-card";

describe("TeamManagerCard", () => {
  it("renders title and members", () => {
    const { container } = render(<TeamManagerCard />);
    expect(container.textContent).toContain("Team Manager");
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("bob");
    expect(container.textContent).toContain("Platform Team");
  });

  it("shows roles and count", () => {
    const { container } = render(<TeamManagerCard />);
    expect(container.textContent).toContain("owner");
    expect(container.textContent).toContain("developer");
    expect(container.textContent).toContain("4 members");
  });
});
