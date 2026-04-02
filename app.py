import gradio as gr
import zxingcpp
from PIL import Image
from datetime import datetime


def scan_datamatrix(image: Image.Image, history: list) -> tuple[str, str, list, list]:
    """Scan image, append results to history, return updated UI state."""
    if image is None:
        return "No image provided.", "", history, history_to_table(history)

    results = zxingcpp.read_barcodes(image)

    if not results:
        return "No barcode found.", "", history, history_to_table(history)

    timestamp = datetime.now().strftime("%H:%M:%S")
    decoded_texts = []
    metrics_lines = []

    for i, result in enumerate(results, start=1):
        prefix = f"[{i}] " if len(results) > 1 else ""

        decoded_texts.append(f"{prefix}{result.text}")

        fmt = result.format.name if result.format else "Unknown"
        content_type = result.content_type.name if result.content_type else "Unknown"
        position = result.position

        lines = [f"{prefix}Format: {fmt}"]
        lines.append(f"{prefix}Content type: {content_type}")
        lines.append(f"{prefix}Valid: {result.valid}")
        lines.append(f"{prefix}Error: {result.error_message or 'None'}")

        if position:
            corners = [
                f"TL({position.top_left.x},{position.top_left.y})",
                f"TR({position.top_right.x},{position.top_right.y})",
                f"BR({position.bottom_right.x},{position.bottom_right.y})",
                f"BL({position.bottom_left.x},{position.bottom_left.y})",
            ]
            lines.append(f"{prefix}Position: {' | '.join(corners)}")

        if result.orientation is not None:
            lines.append(f"{prefix}Orientation: {result.orientation}°")

        if result.ec_level:
            lines.append(f"{prefix}EC level: {result.ec_level}")

        metrics_lines.extend(lines)
        if len(results) > 1:
            metrics_lines.append("")

        # Store entry in history
        history.append({
            "time": timestamp,
            "text": result.text,
            "format": fmt,
            "content_type": content_type,
            "valid": result.valid,
            "orientation": f"{result.orientation}°" if result.orientation is not None else "-",
            "ec_level": result.ec_level or "-",
            "error": result.error_message or "-",
        })

    decoded_output = "\n".join(decoded_texts)
    metrics_output = "\n".join(metrics_lines).rstrip()

    return decoded_output, metrics_output, history, history_to_table(history)


def history_to_table(history: list) -> list:
    """Convert history list to rows for gr.Dataframe."""
    rows = []
    for idx, entry in enumerate(reversed(history), start=1):
        rows.append([
            idx,
            entry["time"],
            entry["text"],
            entry["format"],
            entry["content_type"],
            entry["valid"],
            entry["orientation"],
            entry["ec_level"],
            entry["error"],
        ])
    return rows


TABLE_HEADERS = ["#", "Time", "Decoded Text", "Format", "Content Type", "Valid", "Orientation", "EC Level", "Error"]


def clear_history() -> tuple[list, list]:
    return [], []


with gr.Blocks(title="Data Matrix Scanner") as demo:
    gr.Markdown("## Data Matrix Barcode Scanner")
    gr.Markdown(
        "Point your camera at a Data Matrix barcode and click **Capture** to scan. "
        "Each scan is added to the history table below."
    )

    scan_history = gr.State([])

    with gr.Row():
        image_input = gr.Image(
            sources=["webcam", "upload"],
            type="pil",
            label="Camera / Upload",
        )

    with gr.Row():
        decoded_output = gr.Textbox(
            label="Last decoded text",
            lines=2,
            interactive=False,
            placeholder="Decoded barcode content will appear here…",
        )
        metrics_output = gr.Textbox(
            label="Last scan metrics",
            lines=6,
            interactive=False,
            placeholder="Format, position, orientation and other details will appear here…",
        )

    with gr.Row():
        gr.Markdown("### Scan History")
        clear_btn = gr.Button("Clear History", variant="stop", size="sm")

    history_table = gr.Dataframe(
        headers=TABLE_HEADERS,
        datatype=["number", "str", "str", "str", "str", "bool", "str", "str", "str"],
        interactive=False,
        wrap=True,
        label=None,
    )

    image_input.change(
        fn=scan_datamatrix,
        inputs=[image_input, scan_history],
        outputs=[decoded_output, metrics_output, scan_history, history_table],
    )

    clear_btn.click(
        fn=clear_history,
        outputs=[scan_history, history_table],
    )

if __name__ == "__main__":
    demo.launch()
