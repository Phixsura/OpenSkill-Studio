import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import DiContainerCard from "../src/components/api-developer-platform-sdk-consumer-api-di-container-card";

describe("DiContainerCard", () => {
  it("renders title and services", () => {
    const { container } = render(<DiContainerCard />);
    expect(container.textContent).toContain("DI Container");
    expect(container.textContent).toContain("DatabasePool");
    expect(container.textContent).toContain("OrderService");
  });

  it("shows lifecycle and stats", () => {
    const { container } = render(<DiContainerCard />);
    expect(container.textContent).toContain("singleton");
    expect(container.textContent).toContain("transient");
    expect(container.textContent).toContain("4 services");
    expect(container.textContent).toContain("3 instantiated");
  });
});
