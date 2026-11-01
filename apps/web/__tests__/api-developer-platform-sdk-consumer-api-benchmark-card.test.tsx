import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import BenchmarkCard from "../src/components/api-developer-platform-sdk-consumer-api-benchmark-card";

describe("BenchmarkCard", () => {
  it("renders title and runs", () => {
    const { container } = render(<BenchmarkCard />);
    expect(container.textContent).toContain("Endpoint Benchmark");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("/api/search");
  });

  it("shows run count", () => {
    const { container } = render(<BenchmarkCard />);
    expect(container.textContent).toContain("3 benchmark runs");
  });
});
