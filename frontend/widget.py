try:
    import ipywidgets as widgets  # type: ignore[import]  # pylint: disable=import-error
except Exception:
    # Minimal stub implementation of the ipywidgets classes used in this file,
    # so the module can run in non-notebook environments (tests, static analysis, etc.).
    class _StubDropdown:
        def __init__(self, options=None, layout=None):
            self.options = list(options) if options is not None else []
            self.layout = layout or {}
            self.value = self.options[0] if self.options else None
        def __repr__(self):
            return f"<StubDropdown value={self.value} options={self.options}>"

    class _StubTextarea:
        def __init__(self, placeholder="", layout=None):
            self.placeholder = placeholder
            self.layout = layout or {}
            self.value = ""
        def __repr__(self):
            return f"<StubTextarea value={self.value!r}>"

    class _StubButton:
        def __init__(self, description="", disabled=False, tooltip="", icon=""):
            self.description = description
            self.disabled = disabled
            self.tooltip = tooltip
            self.icon = icon
            self._callbacks = []
        def on_click(self, cb):
            # store callback for compatibility; can be triggered manually via click()
            self._callbacks.append(cb)
        def click(self):
            for cb in list(self._callbacks):
                try:
                    cb(self)
                except Exception:
                    pass
        def __repr__(self):
            return f"<StubButton desc={self.description!r}>"

    class _StubOutput:
        def __init__(self, layout=None):
            self.layout = layout or {}
            self._buffer = []
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            return False
        def clear_output(self, wait=False):
            self._buffer.clear()
        def __repr__(self):
            return "<StubOutput>"

    class _StubGridBox:
        def __init__(self, children):
            self.children = list(children)
        def __repr__(self):
            return f"<StubGridBox children={self.children}>"

    import types
    widgets = types.SimpleNamespace(
        Dropdown=_StubDropdown,
        Textarea=_StubTextarea,
        Button=_StubButton,
        Output=_StubOutput,
        GridBox=_StubGridBox,
    )
try:
    from IPython.display import display, HTML, Markdown, clear_output
except Exception:
    # Fallbacks for environments where IPython is not installed (e.g., static analysis or non-notebook runs)
    def display(obj=None):
        if obj is None:
            return
        # Try to print useful representation
        try:
            print(getattr(obj, "data", str(obj)))
        except Exception:
            print(obj)

    class HTML(str):
        pass

    class Markdown(str):
        pass

    def clear_output(wait=False):
        # No-op fallback for clearing output in non-notebook environments
        return

import importlib
try:
    # Import dynamically to avoid static analyzers complaining about missing google.colab
    _colab_ai = importlib.import_module("google.colab.ai")
    ai = _colab_ai
except Exception:
    # Fallback stub for environments where google.colab.ai is not available (e.g., local dev or CI)
    class _StubAI:
        def list_models(self):
            # Return a simple default model list compatible with widgets.Dropdown options
            return ["default-stub-model"]

        def generate_text(self, prompt="", model_name=None, stream=True):
            # Provide a simple streaming generator for compatibility with the rest of the code.
            response = f"Stub response for prompt: {prompt}"
            if stream:
                # yield in chunks to simulate streaming behavior
                for i in range(0, len(response), 40):
                    yield response[i:i+40]
            else:
                yield response

    ai = _StubAI()

dropdown = widgets.Dropdown(
    options=[],
    layout={'width': 'auto'}
)

def update_model_list(new_options):
    dropdown.options = new_options
update_model_list(ai.list_models())

text_input = widgets.Textarea(
    placeholder='Ask me anything....',
    layout={'width': 'auto', 'height': '100px'},
)

button = widgets.Button(
    description='Submit Text',
    disabled=False,
    tooltip='Click to submit the text',
    icon='check'
)

output_area = widgets.Output(
     layout={'width': 'auto', 'max_height': '300px','overflow_y': 'scroll'}
)

def on_button_clicked(b):
    with output_area:
        output_area.clear_output(wait=False)
        accumulated_content = ""
        for new_chunk in ai.generate_text(prompt=text_input.value, model_name=dropdown.value, stream=True):
            if new_chunk is None:
                continue
            accumulated_content += new_chunk
            clear_output(wait=True)
            display(Markdown(accumulated_content))

button.on_click(on_button_clicked)
vbox = widgets.GridBox([dropdown, text_input, button, output_area])

display(HTML("""
<style>
.widget-dropdown select {
    font-size: 18px;
    font-family: "Arial", sans-serif;
}
.widget-textarea textarea {
    font-size: 18px;
    font-family: "Arial", sans-serif;
}
</style>
"""))
display(vbox)
