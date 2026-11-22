import React from "react";
import classes from "./TagsNote.module.scss";

type TagsNoteProps = {
    tags: Array<string> | null;
};

const TagsNote: React.FC<TagsNoteProps> = (props) => {
    const tags = props.tags;

    if (tags.length === 0) return null;
    return (
        <div className={classes["container"]}>
            {tags.map((tag) => <p key={tag}>#{tag}</p>)}
        </div>
    );
};

export default TagsNote;
