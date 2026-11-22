const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

/** "7 Mar 2026" */
export const formatDay = (date: Date): string =>
    `${date.getDate()} ${MONTHS[date.getMonth()]} ${date.getFullYear()}`;

/** "19:05" */
export const formatTime = (date: Date): string =>
    `${String(date.getHours()).padStart(2, "0")}:${String(date.getMinutes()).padStart(2, "0")}`;

export const parseDate = (value: string | null | undefined): Date | null => {
    if (!value) return null;
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? null : date;
};
