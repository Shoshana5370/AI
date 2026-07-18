import gradio as gr
from dotenv import load_dotenv
from netfree_unstrict_ssl import unstrict_ssl

from workflow import create_default_workflow

load_dotenv()
unstrict_ssl()

workflow = create_default_workflow()


def chat(message, history):
    result = workflow.run(message)
    return result.message


demo = gr.ChatInterface(
    fn=chat,
    title="RAG Chat",
    description="Ask a question about the indexed documents.",
)


if __name__ == "__main__":
    demo.launch()
 