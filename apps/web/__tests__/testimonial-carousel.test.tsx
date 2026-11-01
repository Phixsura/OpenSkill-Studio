import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TestimonialCarousel } from "@/components/testimonial-carousel";

describe("TestimonialCarousel", () => {
  const testimonials = [
    { quote: "Amazing!", author: "Alice Smith", role: "CTO", company: "Acme",
      rating: 5, avatar_initials: "AS" },
  ];
  it("renders", () => {
    const { container } = render(
      <TestimonialCarousel testimonials={testimonials} avgRating={5} />
    );
    expect(container.textContent).toContain("What Developers Say");
    expect(container.textContent).toContain("Amazing!");
    expect(container.textContent).toContain("Alice Smith");
    expect(container.textContent).toContain("CTO at Acme");
    expect(container.textContent).toContain("AS");
    expect(container.textContent).toContain("★★★★★");
  });
  it("empty returns null", () => {
    const { container } = render(<TestimonialCarousel testimonials={[]} avgRating={0} />);
    expect(container.innerHTML).toBe("");
  });
});
