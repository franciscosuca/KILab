# Prompt to paste per model

Replace `<MODEL_NAME>` with a short name for the model under test (for example `gemma4` or `gpt6luna`), then paste this text into each session:

```text
Create a single-file HTML/Tailwind CSS interactive "Self-Destruct" button demo.

Save the actual HTML file, not just a code snippet, to:
./self-destruct-<MODEL_NAME>.html

Requirements:
- Use Tailwind CSS via CDN, with all custom CSS and JavaScript inline.
- Open directly in a browser without a build step or local server.
- Create a polished interface with hover, pressed, and disabled states.
- Require confirmation before starting a dramatic 10-second countdown.
- Allow cancellation during the countdown.
- Finish with a simulated destruction animation and a reset option.
- Include keyboard accessibility and respect reduced-motion preferences.
- This is a visual demo only: perform no destructive actions.

Work independently and edit only your uniquely named file, since other agents may run simultaneously.

When finished, report the absolute file path and a brief summary of your design.
```

Keep the prompt identical across models so results are comparable.
