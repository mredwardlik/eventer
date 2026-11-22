import { describe, expect, test } from "vitest";
import { formatDay, formatTime, parseDate } from "src/utils/dates";

describe("dates", () => {
    test("time always has two digits", () => {
        expect(formatTime(new Date(2026, 2, 7, 9, 5))).toBe("09:05");
        expect(formatTime(new Date(2026, 2, 7, 19, 30))).toBe("19:30");
        expect(formatTime(new Date(2026, 2, 7, 0, 0))).toBe("00:00");
    });

    test("day", () => {
        expect(formatDay(new Date(2026, 2, 7))).toBe("7 Mar 2026");
    });

    test("parse", () => {
        expect(parseDate(null)).toBeNull();
        expect(parseDate("")).toBeNull();
        expect(parseDate("not a date")).toBeNull();
        expect(parseDate("2026-03-07T19:05:00Z")?.toISOString()).toBe("2026-03-07T19:05:00.000Z");
    });
});
