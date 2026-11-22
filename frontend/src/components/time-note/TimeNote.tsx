import React from "react";
import classes from "./TimeNote.module.scss";
import TimeIcon from "@mui/icons-material/AccessTimeFilled";
import { formatTime, parseDate } from "src/utils/dates";

type TimeNoteProps = {
    startDate: string | null;
    endDate: string | null;
};

const TimeNote: React.FC<TimeNoteProps> = (props) => {
    const startDate = parseDate(props.startDate);
    const endDate = parseDate(props.endDate);

    return (
        <div className={classes["container"]}>
            <TimeIcon />
            {startDate !== null && <p>{formatTime(startDate)}</p>}
            {endDate !== null && <p>{"- " + formatTime(endDate)}</p>}
        </div>
    );
};

export default TimeNote;
