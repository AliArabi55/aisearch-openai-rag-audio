export type GroundingFile = {
    id: string;
    name: string;
    content: string;
};

export type OrderItem = {
    id: string;
    name: string;
    price: number;
    ingredients: string;
    quantity: number;
};

export type OrderSummary = {
    items: OrderItem[];
    total_items: number;
    total_price: number;
    formatted_summary: string;
    table_html: string;
};

export type OrderToolResult = {
    action: "order_updated" | "show_order_summary" | "order_confirmed" | "order_cleared";
    message?: string;
    order_summary?: OrderSummary;
    order_table?: string;
};

export type HistoryItem = {
    id: string;
    transcript: string;
    groundingFiles: GroundingFile[];
};

export type SessionUpdateCommand = {
    type: "session.update";
    session: {
        turn_detection?: {
            type: "server_vad" | "none";
        };
        input_audio_transcription?: {
            model: "whisper-1";
        };
    };
};

export type InputAudioBufferAppendCommand = {
    type: "input_audio_buffer.append";
    audio: string;
};

export type InputAudioBufferClearCommand = {
    type: "input_audio_buffer.clear";
};

export type Message = {
    type: string;
};

export type ResponseAudioDelta = {
    type: "response.audio.delta";
    delta: string;
};

export type ResponseAudioTranscriptDelta = {
    type: "response.audio_transcript.delta";
    delta: string;
};

export type ResponseInputAudioTranscriptionCompleted = {
    type: "conversation.item.input_audio_transcription.completed";
    event_id: string;
    item_id: string;
    content_index: number;
    transcript: string;
};

export type ResponseDone = {
    type: "response.done";
    event_id: string;
    response: {
        id: string;
        output: { id: string; content?: { transcript: string; type: string }[] }[];
    };
};

export type ExtensionMiddleTierToolResponse = {
    type: "extension.middle_tier_tool.response";
    previous_item_id: string;
    tool_name: string;
    tool_result: string; // JSON string that needs to be parsed into ToolResult
};

export type ToolResult = {
    sources?: { chunk_id: string; title: string; chunk: string }[];
} & Partial<OrderToolResult>;
