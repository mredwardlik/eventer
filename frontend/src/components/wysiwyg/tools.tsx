import Embed from "@editorjs/embed";
import Table from "@editorjs/table";
import List from "@editorjs/list";
import Warning from "@editorjs/warning";
import Code from "@editorjs/code";
import LinkTool from "@editorjs/link";
import Image from "@editorjs/image";
import Raw from "@editorjs/raw";
import Header from "@editorjs/header";
import Quote from "@editorjs/quote";
import Marker from "@editorjs/marker";
import ImageGallery from "@rodrigoodhin/editorjs-image-gallery";
import CheckList from "@editorjs/checklist";
import Delimiter from "@editorjs/delimiter";
import InlineCode from "@editorjs/inline-code";
import SimpleImage from "@editorjs/simple-image";
import { API_URL } from "src/services/settings";

// Images are uploaded to the backend with the token of the user
export default (token?: string | null) => {
    const tools = {
        embed: Embed,
        table: Table,
        marker: Marker,
        list: List,
        warning: Warning,
        code: Code,
        linkTool: LinkTool,
        raw: Raw,
        image: {
            class: Image,
            config: {
                endpoints: {
                    byFile: `${API_URL}event/image`,
                },
                additionalRequestHeaders: { Authorization: `Token ${token}` },
            },
        },
        header: Header,
        quote: Quote,
        imageGallery: ImageGallery,
        checklist: CheckList,
        delimiter: Delimiter,
        inlineCode: InlineCode,
        simpleImage: SimpleImage,
    };
    if (!token) return { ...tools, image: Image }; // reading: the tool only shows saved images
    return tools;
};
