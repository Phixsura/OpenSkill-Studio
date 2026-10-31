import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ConnPoolCard from "../src/components/api-developer-platform-sdk-consumer-api-conn-pool-card";

describe("ConnPoolCard", () => {
  it("renders title and pools", () => {
    const { container } = render(<ConnPoolCard />);
    expect(container.textContent).toContain("Connection Pool");
    expect(container.textContent).toContain("DB Primary");
    expect(container.textContent).toContain("Redis Cache");
  });

  it("shows pool count", () => {
    const { container } = render(<ConnPoolCard />);
    expect(container.textContent).toContain("3 pools");
    expect(container.textContent).toContain("8 active");
  });
});
