import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import DeadLetterCard from "../src/components/api-developer-platform-sdk-consumer-api-dead-letter-card";

describe("DeadLetterCard", () => {
  it("renders title and stats", () => {
    const { container } = render(<DeadLetterCard />);
    expect(container.textContent).toContain("Dead Letter Inspector");
    expect(container.textContent).toContain("Dead");
    expect(container.textContent).toContain("Replayed");
  });

  it("shows recent and total", () => {
    const { container } = render(<DeadLetterCard />);
    expect(container.textContent).toContain("order.created");
    expect(container.textContent).toContain("45 total letters");
  });
});
