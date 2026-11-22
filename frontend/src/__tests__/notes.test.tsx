import { render, screen } from "@testing-library/react";
import { describe, expect, test } from "vitest";
import TimeNote from "src/components/time-note/TimeNote";
import DateNote from "src/components/date-note/DateNote";

const local = (hours: number, minutes: number) => new Date(2026, 2, 7, hours, minutes).toISOString();

describe("event notes", () => {
    test("time of the start and the end", () => {
        render(<TimeNote startDate={local(9, 5)} endDate={local(23, 0)} />);
        expect(screen.getByText("09:05")).toBeInTheDocument();
        expect(screen.getByText("- 23:00")).toBeInTheDocument();
    });

    test("no dates, no text", () => {
        const { container } = render(<TimeNote startDate={null} endDate={null} />);
        expect(container.querySelectorAll("p")).toHaveLength(0);
    });

    test("date", () => {
        render(<DateNote startDate={local(9, 5)} endDate={null} />);
        expect(screen.getByText("7")).toBeInTheDocument();
        expect(screen.getByText("Mar")).toBeInTheDocument();
        expect(screen.getByText("2026")).toBeInTheDocument();
    });
});
